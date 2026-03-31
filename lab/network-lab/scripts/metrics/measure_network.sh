#!/usr/bin/env bash
set -euo pipefail

echo "dns_lookup_api=$(docker exec kp-edge sh -c 'getent hosts api-service >/dev/null && echo ok || echo fail')"
echo "dns_lookup_auth=$(docker exec kp-api sh -c 'getent hosts auth-service >/dev/null && echo ok || echo fail')"

echo "tcp_connect_api=$(docker exec kp-edge python - <<'PY'
import socket, time
s=socket.socket()
t=time.time()
try:
    s.settimeout(2)
    s.connect(("api-service", 8080))
    print(round(time.time()-t, 6))
except Exception:
    print("fail")
finally:
    s.close()
PY
)"

echo "tcp_connect_auth=$(docker exec kp-api python - <<'PY'
import socket, time
s=socket.socket()
t=time.time()
try:
    s.settimeout(2)
    s.connect(("auth-service", 8080))
    print(round(time.time()-t, 6))
except Exception:
    print("fail")
finally:
    s.close()
PY
)"
