import os
import time
from pathlib import Path

import gradio as gr
import spaces
import torch
from huggingface_hub import hf_hub_download

# ComfyUI's quantization-aware runtime is required for qwen_3_4b_fp8_mixed.safetensors.
# Do not load this checkpoint with Transformers load_state_dict().
from comfy_diffusion import check_runtime, vae_decode
from comfy_diffusion.conditioning import encode_prompt
from comfy_diffusion.models import ModelManager
from comfy_diffusion.nodes import run_node
from comfy_diffusion.sampling import sample

MODEL_REPO = "ibank31/stockforge-models"
ROOT = Path(os.getenv("STOCKFORGE_MODEL_DIR", "/tmp/stockforge-models"))
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
Z_IMAGE_FILE = "z_image_turbo_fp8_e4m3fn.safetensors"
QWEN_FILE = "qwen_3_4b_fp8_mixed.safetensors"
AE_FILE = "ae.safetensors"
ALLOWED_CANVASES = {(1024, 1024), (1344, 768)}


def _prepare_models():
    for folder in ("diffusion_models", "text_encoders", "vae"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    files = {
        Z_IMAGE_FILE: "diffusion_models",
        QWEN_FILE: "text_encoders",
        AE_FILE: "vae",
    }
    for filename, folder in files.items():
        target = ROOT / folder / filename
        if target.exists() and target.stat().st_size > 0:
            print(f"[StockForge] Cached: {folder}/{filename}")
            continue
        print(f"[StockForge] Downloading {filename}...")
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=filename,
            revision="main",
            token=HF_TOKEN,
            local_dir=str(ROOT / folder),
            local_dir_use_symlinks=False,
        )


def _load_runtime_models():
    runtime = check_runtime()
    if isinstance(runtime, dict) and runtime.get("error"):
        raise RuntimeError(runtime["error"])
    _prepare_models()
    manager = ModelManager(models_dir=ROOT)
    print("[StockForge] Loading FP8 Z-Image model through Comfy runtime...")
    model = run_node(
        "UNETLoader",
        unet_name=Z_IMAGE_FILE,
        weight_dtype="default",
    )[0]
    print("[StockForge] Loading Qwen3 FP8 mixed text encoder through Comfy runtime...")
    clip = run_node(
        "CLIPLoader",
        clip_name=QWEN_FILE,
        type="lumina2",
        device="default",
    )[0]
    print("[StockForge] Loading AE VAE...")
    vae = manager.load_vae(AE_FILE)
    print("[StockForge] Models ready")
    return model, clip, vae


MODEL_CACHE = None


def _get_models():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        MODEL_CACHE = _load_runtime_models()
    return MODEL_CACHE


def estimate_duration(prompt, width, height, steps, seed, randomize_seed):
    return min(55, max(20, 8 + int(steps) * 4))


@spaces.GPU(duration=estimate_duration, size="large")
def generate_gpu(prompt, width, height, steps, seed, randomize_seed):
    started = time.perf_counter()
    model, clip, vae = _get_models()
    if randomize_seed:
        seed = int.from_bytes(os.urandom(8), "little") & 0xFFFFFFFFFFFFFFFF
    seed = int(seed)

    positive = encode_prompt(clip, str(prompt).strip())
    negative = encode_prompt(clip, "")

    latent = {"samples": torch.zeros((1, 16, int(height) // 8, int(width) // 8), dtype=torch.float32)}
    model = run_node("ModelSamplingAuraFlow", model=model, shift=3.0)[0]
    denoised = sample(
        model,
        positive,
        negative,
        latent,
        steps=int(steps),
        cfg=1.0,
        sampler_name="res_multistep",
        scheduler="simple",
        seed=seed,
    )
    image = vae_decode(vae, denoised)
    elapsed = round(time.perf_counter() - started, 3)
    return image, seed, elapsed



@spaces.GPU(duration=8, size="large")
def runtime_startup_audit():
    """CPU-only runtime inspection persisted for later inspection."""
    import importlib
    import pkgutil
    import sys
    import json

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "python": sys.version.split()[0],
        "comfy_diffusion": None,
        "relevant_modules": [],
        "qwen_source_files": [],
    }

    try:
        mod = importlib.import_module("comfy_diffusion")

        result["comfy_diffusion"] = {
            "file": getattr(mod, "__file__", None),
            "version": getattr(mod, "__version__", "NOT_EXPOSED"),
        }

        root = Path(mod.__file__).parent

        modules = []
        for item in pkgutil.walk_packages(
            mod.__path__,
            mod.__name__ + "."
        ):
            name = item.name.lower()

            if any(
                key in name
                for key in (
                    "qwen",
                    "lumina",
                    "model",
                    "text",
                    "clip",
                    "vae",
                    "conditioning",
                    "nodes",
                )
            ):
                modules.append(item.name)

        result["relevant_modules"] = modules[:300]

        source_matches = []

        for py in root.rglob("*.py"):
            try:
                data = py.read_text(errors="ignore")
            except Exception:
                continue

            lower = data.lower()

            if any(
                key in lower
                for key in (
                    "qwenimage",
                    "qwen_image",
                    "qwen2_5_vl",
                    "qwen_2.5_vl",
                    "qwenimagevae",
                )
            ):
                source_matches.append(str(py.relative_to(root)))

        result["qwen_source_files"] = source_matches[:300]

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    audit_file = Path("/tmp/stockforge_runtime_audit.json")
    audit_file.write_text(
        json.dumps(result, indent=2, sort_keys=True)
    )

    print("[StockForge] Runtime audit persisted:", audit_file)

    return result


def runtime_qwen_loader_audit():
    """Inspect Qwen model loader capabilities without loading checkpoints."""
    import importlib
    import inspect

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "checks": {},
    }

    try:
        nodes = importlib.import_module(
            "comfy_diffusion.nodes"
        )

        run_node = getattr(nodes, "run_node", None)
        list_nodes = getattr(nodes, "list_nodes", None)

        if not callable(run_node) or not callable(list_nodes):
            result["status"] = "error"
            result["error"] = "Required runtime functions unavailable"
            return result

        registry = list_nodes()

        for node_name in (
            "UNETLoader",
            "CLIPLoader",
            "VAELoader",
            "ModelSamplingAuraFlow",
        ):
            info = registry.get(node_name)

            if info is None:
                result["checks"][node_name] = {
                    "present": False
                }
                continue

            entry = {
                "present": True,
                "node_type": type(info).__name__,
            }

            for attr in (
                "category",
                "input_types",
                "output_types",
                "output_names",
                "python_module",
            ):
                try:
                    value = getattr(info, attr)
                    if callable(value):
                        value = value()
                    entry[attr] = str(value)[:15000]
                except Exception:
                    pass

            result["checks"][node_name] = entry

        # Inspect ModelManager methods and loader source.
        try:
            mm_mod = importlib.import_module(
                "comfy_diffusion.models"
            )
            manager = getattr(mm_mod, "ModelManager", None)

            if manager:
                result["model_manager"] = {
                    "module": mm_mod.__file__,
                    "methods": [
                        x for x in dir(manager)
                        if any(
                            k in x.lower()
                            for k in (
                                "load",
                                "model",
                                "clip",
                                "vae",
                                "unet",
                            )
                        )
                    ],
                }

                for method_name in (
                    "load_model",
                    "load_clip",
                    "load_vae",
                ):
                    method = getattr(manager, method_name, None)

                    if method:
                        result["model_manager"][method_name] = {
                            "signature": str(
                                inspect.signature(method)
                            )
                        }

        except Exception as e:
            result["model_manager_error"] = (
                type(e).__name__ + ": " + str(e)
            )

        # Inspect Qwen pipeline manifests if available.
        for module_name in (
            "comfy_diffusion.pipelines.image.qwen",
            "comfy_diffusion.pipelines.image.qwen.layered",
        ):
            try:
                mod = importlib.import_module(module_name)

                manifest = getattr(mod, "manifest", None)

                if callable(manifest):
                    try:
                        result["checks"][module_name] = manifest()
                    except Exception as e:
                        result["checks"][module_name] = {
                            "manifest_error":
                                type(e).__name__ + ": " + str(e)
                        }
                else:
                    result["checks"][module_name] = {
                        "module": mod.__file__,
                        "manifest": "NOT_EXPOSED"
                    }

            except Exception as e:
                result["checks"][module_name] = {
                    "import_error":
                        type(e).__name__ + ": " + str(e)
                }

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_qwen_node_details():
    """Inspect exact metadata for Qwen-related Comfy nodes. CPU-only."""
    import importlib

    targets = [
        "ModelMergeQwenImage",
        "TextEncodeQwenImageEdit",
        "TextEncodeQwenImageEditPlus",
        "EmptyQwenImageLayeredLatentImage",
        "QwenImageDiffsynthControlnet",
        "ModelSamplingAuraFlow",
        "CLIPLoader",
        "UNETLoader",
        "VAELoader",
        "KSampler",
        "VAEDecode",
    ]

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "nodes": {},
    }

    try:
        nodes = importlib.import_module(
            "comfy_diffusion.nodes"
        )

        list_nodes = getattr(nodes, "list_nodes", None)

        if not callable(list_nodes):
            result["status"] = "error"
            result["error"] = "list_nodes unavailable"
            return result

        registry = list_nodes()

        for target in targets:
            info = registry.get(target)

            if info is None:
                result["nodes"][target] = {
                    "present": False
                }
                continue

            data = {
                "present": True,
                "type": type(info).__name__,
            }

            # NodeInfo is intentionally inspected without executing node code.
            for attr in (
                "name",
                "display_name",
                "category",
                "description",
                "input_types",
                "output_types",
                "output_names",
                "output_tooltips",
                "python_module",
                "node_class",
                "is_api_node",
            ):
                try:
                    value = getattr(info, attr)
                    if callable(value):
                        value = value()
                    data[attr] = str(value)[:10000]
                except Exception:
                    pass

            result["nodes"][target] = data

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_node_registry_query():
    """Query actual Comfy node registry without executing generation."""
    import importlib
    import inspect

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "registry": {},
        "matches": [],
    }

    try:
        nodes = importlib.import_module(
            "comfy_diffusion.nodes"
        )

        list_nodes = getattr(nodes, "list_nodes", None)

        if not callable(list_nodes):
            result["status"] = "error"
            result["error"] = "list_nodes not available"
            return result

        result["list_nodes_signature"] = str(
            inspect.signature(list_nodes)
        )

        records = list_nodes()

        result["registry_type"] = type(records).__name__
        result["registry_count"] = len(records)

        keywords = (
            "qwen",
            "image",
            "textencode",
            "text_encode",
            "clip",
            "vae",
            "latent",
            "sampling",
            "sampler",
            "unet",
            "model",
        )

        for item in records:
            try:
                if isinstance(item, dict):
                    node_id = (
                        item.get("name")
                        or item.get("id")
                        or item.get("node_id")
                        or ""
                    )
                    info = item
                else:
                    node_id = str(
                        getattr(item, "name", "")
                        or getattr(item, "node_id", "")
                        or ""
                    )
                    info = {
                        "type": type(item).__name__,
                        "repr": repr(item)[:2000],
                    }

                haystack = (
                    str(node_id) + " " + str(info)
                ).lower()

                if any(k in haystack for k in keywords):
                    result["matches"].append({
                        "node_id": node_id,
                        "info": info,
                    })

            except Exception as e:
                result["matches"].append({
                    "parse_error": type(e).__name__ + ": " + str(e)
                })

        result["match_count"] = len(result["matches"])

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_run_node_audit():
    """Inspect run_node implementation and Comfy node registry mechanism."""
    import importlib
    import inspect
    import re

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "run_node": {},
        "registry_candidates": [],
        "qwen_strings": [],
    }

    try:
        nodes = importlib.import_module(
            "comfy_diffusion.nodes"
        )

        run_node = getattr(nodes, "run_node", None)

        if run_node is None:
            result["status"] = "error"
            result["error"] = "run_node not found"
            return result

        result["run_node"]["module"] = nodes.__file__
        result["run_node"]["signature"] = str(
            inspect.signature(run_node)
        )

        try:
            source = inspect.getsource(run_node)
        except Exception as e:
            source = ""
            result["run_node"]["source_error"] = (
                type(e).__name__ + ": " + str(e)
            )

        result["run_node"]["source"] = source[:20000]

        module_source = Path(nodes.__file__).read_text(
            errors="ignore"
        )

        # Find registry-like identifiers without importing/executing them.
        patterns = (
            r"[A-Za-z0-9_]*(?:NODE|NODE_CLASS|REGISTRY|registry|nodes)[A-Za-z0-9_]*"
        )

        candidates = sorted(
            set(re.findall(patterns, module_source))
        )

        result["registry_candidates"] = candidates[:300]

        # Locate Qwen-related references inside nodes.py.
        qwen_lines = []

        for i, line in enumerate(
            module_source.splitlines(), 1
        ):
            if any(
                key.lower() in line.lower()
                for key in (
                    "qwen",
                    "qwenimage",
                    "qwen_image",
                    "qwen_vl",
                    "TextEncodeQwen",
                )
            ):
                qwen_lines.append({
                    "line": i,
                    "text": line[:500],
                })

        result["qwen_strings"] = qwen_lines[:300]

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_qwen_node_audit():
    """Inspect Comfy node registry for Qwen T2I capability. CPU-only."""
    import importlib
    import inspect

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "nodes": {},
        "qwen_related": [],
    }

    try:
        nodes_mod = importlib.import_module(
            "comfy_diffusion.nodes"
        )

        # Inspect exported/public attributes without executing generation.
        names = sorted(
            name for name in dir(nodes_mod)
            if not name.startswith("_")
        )

        qwen_keywords = (
            "qwen",
            "image",
            "clip",
            "vae",
            "latent",
            "sampling",
            "model",
        )

        for name in names:
            if any(k in name.lower() for k in qwen_keywords):
                try:
                    obj = getattr(nodes_mod, name)

                    entry = {
                        "object_type": type(obj).__name__,
                    }

                    if callable(obj):
                        try:
                            entry["signature"] = str(
                                inspect.signature(obj)
                            )
                        except Exception:
                            entry["signature"] = "NOT_AVAILABLE"

                    result["nodes"][name] = entry

                    if "qwen" in name.lower():
                        result["qwen_related"].append(name)

                except Exception as e:
                    result["nodes"][name] = {
                        "error": type(e).__name__ + ": " + str(e)
                    }

        # Inspect run_node itself for registry-related metadata.
        result["run_node"] = {
            "module": nodes_mod.__file__,
            "has_run_node": hasattr(nodes_mod, "run_node"),
        }

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_qwen_source_inspect():
    """Inspect deployed Qwen pipeline source without GPU/model loading."""
    import importlib
    import inspect
    import re

    result = {
        "status": "ok",
        "gpu_used": False,
        "models_loaded": False,
        "files": {},
    }

    try:
        mod = importlib.import_module(
            "comfy_diffusion.pipelines.image.qwen"
        )

        root = Path(mod.__file__).parent

        targets = sorted(root.glob("*.py"))

        for py in targets:
            try:
                source = py.read_text(errors="ignore")
            except Exception as e:
                result["files"][py.name] = {
                    "error": str(e)
                }
                continue

            lines = source.splitlines()

            relevant = []

            keywords = (
                "2511",
                "2512",
                "QwenImage",
                "Qwen2.5",
                "Qwen2_5",
                "VL",
                "VAE",
                "scheduler",
                "transformer",
                "checkpoint",
                "model_name",
                "filename",
            )

            for i, line in enumerate(lines, 1):
                if any(k.lower() in line.lower() for k in keywords):
                    relevant.append({
                        "line": i,
                        "text": line[:500],
                    })

            classes = re.findall(
                r"^\s*class\s+([A-Za-z0-9_]+)",
                source,
                re.MULTILINE
            )

            functions = re.findall(
                r"^\s*(?:async\s+)?def\s+([A-Za-z0-9_]+)",
                source,
                re.MULTILINE
            )

            result["files"][py.name] = {
                "classes": classes[:100],
                "functions": functions[:200],
                "relevant_lines": relevant[:300],
            }

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def runtime_audit():
    """Return CPU-only startup audit. Never requests GPU."""
    import json

    audit_file = Path("/tmp/stockforge_runtime_audit.json")

    if not audit_file.exists():
        return {
            "status": "not_ready",
            "gpu_used": False,
            "message": "Startup audit file not available yet.",
        }

    return json.loads(audit_file.read_text())


def runtime_qwen_probe():
    """Inspect the deployed Comfy runtime for Qwen-Image support. No GPU."""
    import importlib
    import pkgutil

    result = {
        "status": "ok",
        "gpu_used": False,
        "model_loaded": False,
        "qwen_image_support": False,
        "comfy_diffusion": None,
        "matching_modules": [],
    }

    try:
        mod = importlib.import_module("comfy_diffusion")
        result["comfy_diffusion"] = {
            "module": getattr(mod, "__file__", None),
            "version": getattr(mod, "__version__", None),
        }

        root = Path(mod.__file__).parent
        matches = []

        for py in root.rglob("*.py"):
            try:
                data = py.read_text(errors="ignore")
            except Exception:
                continue

            lower = data.lower()

            if "qwenimage" in lower or "qwen_image" in lower:
                matches.append(str(py.relative_to(root)))

        result["matching_modules"] = matches[:100]
        result["qwen_image_support"] = bool(matches)

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error"] = str(e)

    return result


def gpu_probe():
    """Read actual GPU capabilities without loading StockForge models."""
    if not torch.cuda.is_available():
        return {
            "status": "error",
            "cuda_available": False,
            "error": "CUDA unavailable",
        }

    free_bytes, total_bytes = torch.cuda.mem_get_info(0)
    props = torch.cuda.get_device_properties(0)

    return {
        "status": "ok",
        "cuda_available": True,
        "device_name": torch.cuda.get_device_name(0),
        "compute_capability": f"{props.major}.{props.minor}",
        "total_vram_gib": round(total_bytes / 1024**3, 3),
        "free_vram_gib": round(free_bytes / 1024**3, 3),
        "allocated_vram_gib": round(torch.cuda.memory_allocated(0) / 1024**3, 3),
        "reserved_vram_gib": round(torch.cuda.memory_reserved(0) / 1024**3, 3),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "models_loaded": False,
        "image_generated": False,
    }


def generate(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise gr.Error("Prompt is required.")
    dimensions = (int(width), int(height))
    if dimensions not in ALLOWED_CANVASES:
        supported = ", ".join(f"{w}x{h}" for w, h in sorted(ALLOWED_CANVASES))
        raise gr.Error(f"Supported canvases are {supported}.")
    if not 4 <= int(steps) <= 12:
        raise gr.Error("Steps must be between 4 and 12 for the free-tier benchmark.")

    print(f"[StockForge] Standalone prompt length: {len(prompt)}")
    return generate_gpu(prompt, int(width), int(height), int(steps), int(seed), bool(randomize_seed))


_REMOTE_CACHE = {}


def generate_remote(
    prompt,
    width=1024,
    height=1024,
    steps=8,
    seed=0,
    randomize_seed=True,
    stockforge_job_id="",
):
    """Stable machine-to-machine endpoint registered on the active Space demo."""
    job_id = str(stockforge_job_id or "").strip()
    if not job_id:
        raise gr.Error("stockforge_job_id is required")
    if job_id in _REMOTE_CACHE:
        return _REMOTE_CACHE[job_id]
    result = generate(prompt, width, height, steps, seed, randomize_seed)
    _REMOTE_CACHE[job_id] = result
    return result


def portfolio_health():
    """Non-GPU health proof for the standalone-asset generation boundary."""
    return {
        "status": "ok",
        "generation_mode": "standalone_portfolio",
        "legacy_reality_compiler": "disabled",
        "default_constraints": [
            "one primary subject",
            "white isolated background",
            "no people, hands, tools, devices, screens, text, numbers, stamps, or unrelated props",
        ],
        "gpu_used": False,
    }


with gr.Blocks(title="StockForge V5 ZeroGPU") as demo:
    gr.Markdown("# StockForge V5 · ZeroGPU\nStandalone Asset Portfolio · FP8-aware Z-Image Turbo runtime.")
    prompt = gr.Textbox(label="Prompt", lines=4)
    with gr.Row():
        width = gr.Number(value=1024, label="Width", precision=0)
        height = gr.Number(value=1024, label="Height", precision=0)
        steps = gr.Slider(4, 12, value=8, step=1, label="Steps")
    with gr.Row():
        seed = gr.Number(value=0, label="Seed", precision=0)
        randomize = gr.Checkbox(value=True, label="Random seed")
    generate_button = gr.Button("Generate", variant="primary")
    output = gr.Image(label="Generated image", type="pil")
    output_seed = gr.Number(label="Used seed", precision=0)
    gpu_seconds = gr.Number(label="Measured GPU-function seconds", precision=3)
    generate_button.click(generate, [prompt, width, height, steps, seed, randomize], [output, output_seed, gpu_seconds], api_name="generate")
    remote_prompt = gr.Textbox(visible=False)
    remote_width = gr.Number(value=1024, visible=False)
    remote_height = gr.Number(value=1024, visible=False)
    remote_steps = gr.Number(value=8, visible=False)
    remote_seed = gr.Number(value=0, visible=False)
    remote_randomize = gr.Checkbox(value=True, visible=False)
    remote_job_id = gr.Textbox(visible=False)
    remote_button = gr.Button(visible=False)
    remote_output = gr.Image(visible=False, type="pil")
    remote_output_seed = gr.Number(visible=False)
    remote_gpu_seconds = gr.Number(visible=False)
    remote_button.click(
        generate_remote,
        [remote_prompt, remote_width, remote_height, remote_steps, remote_seed, remote_randomize, remote_job_id],
        [remote_output, remote_output_seed, remote_gpu_seconds],
        api_name="generate_remote",
    )
    health_button = gr.Button("Standalone Portfolio Health Check")

    health_output = gr.JSON(label="Standalone Portfolio Status")
    health_button.click(portfolio_health, outputs=health_output, api_name="portfolio_health")


    runtime_qwen_button = gr.Button("Runtime Qwen Compatibility")
    runtime_qwen_output = gr.JSON(label="Runtime Qwen Compatibility")
    runtime_qwen_button.click(
        runtime_qwen_probe,
        outputs=runtime_qwen_output,
        api_name="runtime_qwen_probe",
    )

    runtime_qwen_loader_button = gr.Button("Qwen Loader Audit")
    runtime_qwen_loader_output = gr.JSON(label="Qwen Loader Audit")
    runtime_qwen_loader_button.click(
        runtime_qwen_loader_audit,
        outputs=runtime_qwen_loader_output,
        api_name="runtime_qwen_loader_audit",
    )

    runtime_qwen_details_button = gr.Button("Qwen Node Details")
    runtime_qwen_details_output = gr.JSON(label="Qwen Node Details")
    runtime_qwen_details_button.click(
        runtime_qwen_node_details,
        outputs=runtime_qwen_details_output,
        api_name="runtime_qwen_node_details",
    )

    runtime_node_registry_button = gr.Button("Node Registry Query")
    runtime_node_registry_output = gr.JSON(label="Node Registry Query")
    runtime_node_registry_button.click(
        runtime_node_registry_query,
        outputs=runtime_node_registry_output,
        api_name="runtime_node_registry_query",
    )

    runtime_run_node_button = gr.Button("run_node Audit")
    runtime_run_node_output = gr.JSON(label="run_node Audit")
    runtime_run_node_button.click(
        runtime_run_node_audit,
        outputs=runtime_run_node_output,
        api_name="runtime_run_node_audit",
    )

    runtime_qwen_node_button = gr.Button("Qwen Node Audit")
    runtime_qwen_node_output = gr.JSON(label="Qwen Node Audit")
    runtime_qwen_node_button.click(
        runtime_qwen_node_audit,
        outputs=runtime_qwen_node_output,
        api_name="runtime_qwen_node_audit",
    )

    runtime_qwen_source_button = gr.Button("Qwen Source Inspect")
    runtime_qwen_source_output = gr.JSON(label="Qwen Source Inspect")
    runtime_qwen_source_button.click(
        runtime_qwen_source_inspect,
        outputs=runtime_qwen_source_output,
        api_name="runtime_qwen_source_inspect",
    )

    runtime_audit_button = gr.Button("Runtime Audit")
    runtime_audit_output = gr.JSON(label="Runtime Audit")
    runtime_audit_button.click(
        runtime_audit,
        outputs=runtime_audit_output,
        api_name="runtime_audit",
    )

    gpu_probe_button = gr.Button("GPU Capability Probe")
    gpu_probe_output = gr.JSON(label="GPU Runtime Capability")
    gpu_probe_button.click(
        gpu_probe,
        outputs=gpu_probe_output,
        api_name="gpu_probe",
    )



# CPU-only runtime audit. This executes during application startup.
# It must never call a ZeroGPU function or load model checkpoints.
runtime_startup_audit()

if __name__ == "__main__":
    demo.queue(max_size=32).launch()
