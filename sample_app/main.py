from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time
import os

app = FastAPI(title="KubePulse Sample App")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/work")
def work():
    artificial_delay_ms = int(os.getenv("ARTIFICIAL_DELAY_MS", "0"))
    error_mode = os.getenv("ERROR_MODE", "false").lower() == "true"

    if artificial_delay_ms > 0:
        time.sleep(artificial_delay_ms / 1000.0)

    if error_mode:
        return JSONResponse(status_code=500, content={"status": "error"})

    return {"status": "ok"}
