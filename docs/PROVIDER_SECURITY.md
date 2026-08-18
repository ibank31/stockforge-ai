# Provider Configuration and Secret Boundary

StockForge treats provider configuration and provider credentials as separate concerns.

## Rules

1. Jobs and pipeline payloads must never contain API keys, bearer tokens, passwords, or other credentials.
2. Provider configuration may contain non-secret endpoint/options and a `SecretRef`.
3. `SecretRef` stores only the name of an environment variable. It never stores the secret value.
4. Secret resolution is explicit at execution time and should happen as close to the provider adapter boundary as possible.
5. Resolved secrets must never be serialized into job records, artifacts, provenance, normal logs, exception messages, or CLI output.
6. Provider IDs are stable references; changing credentials must not change job identity or provenance.
7. A future encrypted secret store may implement the same boundary, but the core domain contract must not depend on one secret manager.

## Example

```text
Job payload
  provider_id = "comfyui.local"
        |
        v
ProviderConfig
  endpoint = http://127.0.0.1:8188
  secret_ref = COMFYUI_API_KEY
        |
        v
Runtime environment
  COMFYUI_API_KEY = <secret>
        |
        v
Provider adapter
```

The job can be persisted and replayed without persisting the credential itself.
