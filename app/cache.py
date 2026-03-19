import os
try:
    import redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL")
_client = redis.from_url(REDIS_URL, decode_responses=True) if redis and REDIS_URL else None

def set_latest_run_for_scenario(scenario: str, run_id: str) -> None:
    if _client:
        _client.set(f"kubepulse:latest:{scenario}", run_id)

def cache_health() -> dict:
    if not _client:
        return {"enabled": False}
    try:
        return {"enabled": True, "ping": bool(_client.ping())}
    except Exception as exc:
        return {"enabled": True, "error": str(exc)}
