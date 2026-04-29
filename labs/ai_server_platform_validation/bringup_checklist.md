
Bringup Checklist
Linux Host
SSH access works
CPU and memory visible
disk space sufficient
system load reasonable
ROCm / GPU
rocm-smi returns GPU telemetry
GPU memory is visible
temperature and power look normal
vLLM
vLLM process starts
model loads successfully
/v1/models responds
Network
localhost endpoint reachable
no firewall issue for internal benchmark path
Release Gate
baseline benchmark captured
long-prompt burst benchmark captured
release decision generated
