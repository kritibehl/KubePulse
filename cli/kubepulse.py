import requests, sys

BASE = "http://127.0.0.1:8000"

cmd = sys.argv[1]

if cmd == "run":
    r = requests.post(f"{BASE}/scenarios/multi-service-cascade")
    print(r.json())

elif cmd == "compare":
    r = requests.post(f"{BASE}/compare/baseline-vs-candidate")
    print(r.json())
