import json
from pathlib import Path
import math


def forecast_capacity(data: dict) -> dict:
    results = []

    current_requests = data["current_daily_requests"]
    growth = data["daily_growth_rate"]
    capacity_per_replica = data["requests_per_replica_capacity"]

    for days in data["forecast_windows_days"]:
        projected_requests = round(current_requests * ((1 + growth) ** days))
        required_replicas = math.ceil(projected_requests / capacity_per_replica)

        results.append({
            "window_days": days,
            "projected_daily_requests": projected_requests,
            "required_replicas": required_replicas,
            "current_replicas": data["current_replicas"],
            "scale_up_required": required_replicas > data["current_replicas"],
        })

    return {
        "forecast_model": "compound_daily_growth",
        "daily_growth_rate": growth,
        "results": results,
    }


def main():
    data = json.loads(Path("capacity_forecasting/workload_growth_input.json").read_text())
    forecast = forecast_capacity(data)

    out = Path("capacity_forecasting/capacity_forecast_report.json")
    out.write_text(json.dumps(forecast, indent=2))

    print(json.dumps(forecast, indent=2))


if __name__ == "__main__":
    main()
