# StockForge remote GPU backends

StockForge keeps model storage and GPU execution separate.

- **Model storage:** Hugging Face model repository (`ibank31/stockforge-models`).
- **Compute workers:** Hugging Face ZeroGPU Space or a Kaggle GPU worker.
- **Core adapter:** `stockforge.remote_gradio.RemoteGradioProvider`.
- **Worker API:** Gradio queue endpoint `generate_remote`.

Both workers accept the same seven values:

1. prompt
2. width
3. height
4. steps
5. seed
6. randomize_seed
7. stockforge_job_id

The worker returns image output, the effective seed, and measured GPU seconds.
The core downloads the returned file into a provider-owned staging directory,
then the existing `ArtifactIngestor` moves it into the project artifact store.

## Hugging Face

`deploy/zerogpu/app.py` remains the interactive Space. `deploy/zerogpu/remote_api.py`
adds the machine endpoint. Deploy `remote_api.py` as the Space entry point when
StockForge needs programmatic generation.

The HF Space API is a standard Gradio queue: submit, receive `event_id`, then
poll the event until `complete`. See the official Hugging Face Spaces API
endpoint documentation for the current HTTP contract.

## Kaggle

`deploy/kaggle/worker.py` is the same model execution boundary without the
ZeroGPU decorator. It can be started from a Kaggle notebook with `share=True`,
then the resulting Gradio URL is configured as a StockForge provider endpoint.

Set `HF_TOKEN` in the Kaggle secret environment so the worker can pull the
private model repository without putting the token into code or provider config.

## Important recovery boundary

The Gradio worker keeps a completed result keyed by `stockforge_job_id` for the
life of the worker process. This prevents accidental duplicate submission when
the core retries against the same live worker. It is **not durable across a
worker restart**. Therefore the remote provider must not be treated as fully
crash-recovery-safe until the worker persists job state outside its process.

This limitation is deliberate. StockForge's durable execution layer must not
pretend that an ephemeral remote worker provides stronger guarantees than it
actually does.
