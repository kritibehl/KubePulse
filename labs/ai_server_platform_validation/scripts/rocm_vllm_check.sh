#!/usr/bin/env bash
set -euo pipefail

echo "=== ROCm GPU Telemetry ==="
rocm-smi || echo "rocm-smi unavailable"

echo "=== vLLM Process ==="
ps -ef | grep "vllm.entrypoints.openai.api_server" | grep -v grep || echo "vLLM server not running"
