from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = (ROOT / "deploy/pipeline-worker/src/index.js").read_text()
SPACE_APP = (ROOT / "deploy/zerogpu/app.py").read_text()
DEPLOY = (ROOT / ".github/workflows/deploy-zerogpu.yml").read_text()


def test_pipeline_calls_actual_app_remote_upscale_signature():
    expected = 'runRemote(this.env, step, "upscale_remote", [sourceUrl, `${jobId}-upscale`]'
    assert expected in PIPELINE
    assert '"upscale_remote", [sourceUrl, `${jobId}-upscale`, 1, jobId]' not in PIPELINE
    assert '"upscale_remote", [sourceUrl, `${jobId}-upscale`, 4]' not in PIPELINE


def test_space_app_exposes_two_argument_remote_upscale():
    assert 'def upscale_remote(source_path, job_id=""):' in SPACE_APP
    assert ('api_name="/upscale_remote"' in SPACE_APP) or ("api_name='/upscale_remote'" in SPACE_APP)


def test_live_smoke_uses_machine_endpoint_not_ui_endpoint():
    assert 'api_name="/upscale_remote"' in DEPLOY
    assert 'api_name="/upscale")' not in DEPLOY
    assert 'api_name="/upscale_remote")' in DEPLOY


def test_generation_lane_is_qwen_2512():
    assert 'QWEN_DIFFUSION_FILE = "qwen_image_2512_fp8_e4m3fn.safetensors"' in SPACE_APP
    assert 'QWEN_LORA_FILE = "Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors"' in SPACE_APP
    assert 'steps=4' in SPACE_APP
