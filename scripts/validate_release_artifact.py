import json
from pathlib import Path

p = Path("labs/ai_server_platform_validation/artifacts/release_decision.json")

if not p.exists():
    raise SystemExit("missing release_decision.json")

data = json.loads(p.read_text())
decision = data.get("release_decision")
print("release_decision =", decision)

if decision != "block":
    raise SystemExit("expected release_decision=block, got %s" % decision)

if data.get("safe_to_operate") is not False:
    raise SystemExit("expected safe_to_operate=false, got %s" % data.get("safe_to_operate"))

print("validated expected blocked rollout artifact")
