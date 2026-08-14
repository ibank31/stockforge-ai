# StockForge AI Architecture

StockForge is designed as a lightweight orchestration core with replaceable plugins.

```text
CLI
  |
  v
Core Services
  |-- Project Manager
  |-- Config Manager
  |-- Database
  |-- Queue
  |-- Pipeline
  |-- Plugin Manager
  |
  +--> Generator plugins
  +--> QC plugins
  +--> Enhancement plugins
  +--> Vector plugins
  +--> Metadata plugins
  +--> Marketplace adapters
```

The core should not import vendor-specific AI engines directly. External tools such as ComfyUI are integrated through adapters/plugins.

The Termux device is the control plane. Heavy model inference may run on another machine or service later.
