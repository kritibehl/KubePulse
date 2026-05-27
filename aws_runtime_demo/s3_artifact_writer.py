import json
from pathlib import Path


def write_release_artifact(deployment_id: str, artifact_name: str, payload: dict) -> Path:
    out_dir = Path("aws_runtime_demo/release_artifacts") / deployment_id
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / artifact_name
    out.write_text(json.dumps(payload, indent=2))

    return out


def s3_style_uri(path: Path) -> str:
    return f"s3://kubepulse-release-artifacts/{path.relative_to('aws_runtime_demo/release_artifacts')}"
