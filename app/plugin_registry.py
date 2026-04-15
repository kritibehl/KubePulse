from app.network_degradation_engine import run_network_degradation

def list_plugins() -> list[str]:
    return ["packet_loss", "jitter", "intermittent_disconnect", "partial_partition", "recovery_oscillation"]

class _Plugin:
    def __init__(self, name: str):
        self.name = name
    def run(self) -> dict:
        return run_network_degradation(self.name)

def get_plugin(name: str):
    if name not in list_plugins():
        raise ValueError(f"Unknown plugin: {name}")
    return _Plugin(name)
