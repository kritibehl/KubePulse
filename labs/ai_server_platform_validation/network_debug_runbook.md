
Network Debug Runbook
curl http://127.0.0.1:8001/v1/models
curl http://127.0.0.1:8001/health

Common failures:

connection refused: server is not running or wrong namespace/container
timeout: endpoint unreachable or process hung
HTTP 500: application/model-serving failure
