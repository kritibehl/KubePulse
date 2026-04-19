import json
import os
import statistics
import time
from pathlib import Path

import requests

API_BASE = os.environ["OPENAI_COMPAT_BASE"].rstrip("/")
MODEL = os.environ["OPENAI_COMPAT_MODEL"]
INPUT_FILE = os.environ.get("PROMPTS_FILE", "ai_serving/configs/prompts.jsonl")
OUT_FILE = os.environ.get("OUT_FILE", "ai_serving/results/baseline/requests.jsonl")

headers = {"Content-Type": "application/json"}
api_key = os.environ.get("OPENAI_COMPAT_API_KEY")
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

Path(OUT_FILE).parent.mkdir(parents=True, exist_ok=True)

latencies = []
statuses = []
rows = []

with open(INPUT_FILE) as f:
    prompts = [json.loads(line) for line in f if line.strip()]

for row in prompts:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": row["prompt"]}],
        "max_tokens": row.get("max_tokens", 64),
        "temperature": 0.0,
    }
    started = time.perf_counter()
    r = requests.post(f"{API_BASE}/chat/completions", headers=headers, json=payload, timeout=120)
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)
    latencies.append(elapsed_ms)
    statuses.append(r.status_code)
    body = {}
    try:
        body = r.json()
    except Exception:
        body = {"raw_text": r.text[:500]}
    rows.append({
        "prompt": row["prompt"],
        "status_code": r.status_code,
        "latency_ms": elapsed_ms,
        "response_preview": json.dumps(body)[:500],
    })

with open(OUT_FILE, "w") as f:
    for row in rows:
        f.write(json.dumps(row) + "\n")

ok = [x for x, s in zip(latencies, statuses) if s == 200]
timeout_rate = round(sum(1 for s in statuses if s != 200) / max(len(statuses), 1), 4)

def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round((p / 100.0) * (len(sorted_vals) - 1)))))
    return round(sorted_vals[idx], 2)

ok_sorted = sorted(ok)
summary = {
    "requests_total": len(statuses),
    "success_total": sum(1 for s in statuses if s == 200),
    "timeout_rate": timeout_rate,
    "latency_p50_ms": pct(ok_sorted, 50),
    "latency_p95_ms": pct(ok_sorted, 95),
    "latency_p99_ms": pct(ok_sorted, 99),
    "latency_mean_ms": round(statistics.mean(ok) if ok else 0.0, 2),
    "throughput_rps": round((len(ok) / (sum(ok) / 1000.0)) if ok and sum(ok) > 0 else 0.0, 2),
}

summary_path = str(Path(OUT_FILE).with_name("summary.json"))
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
