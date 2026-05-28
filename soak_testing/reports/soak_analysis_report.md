# Long-Running Soak Test Report

| Duration | Latency Drift | Drift % | Error Accumulation | Resource Pressure | Decision |
|---|---:|---:|---:|---|---|
| 1h | 28 ms | 12.73% | 4 | low | continue |
| 6h | 185 ms | 82.22% | 36 | medium | watch |
| 24h | 550 ms | 239.13% | 212 | high | block |