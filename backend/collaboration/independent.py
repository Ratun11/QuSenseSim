from __future__ import annotations

from copy import deepcopy

from backend.collaboration.aggregation import average_curve


def build_mode_result(base_method_result: dict) -> dict:
    result = deepcopy(base_method_result)
    sensors = result["sensors"]

    for sensor in sensors:
        reliability = max(0.05, 1.0 - sensor["final"]["effective_noise"])
        sensor["reliability_weight"] = round(reliability, 3)
        sensor["contribution_score"] = round(sensor["final"]["fisher_info"] * reliability, 3)

    result["global_time_series"] = {
        "time": sensors[0]["time_series"]["time"] if sensors else [],
        "estimate": average_curve([s["time_series"]["estimate"] for s in sensors]),
        "fisher_info": average_curve([s["time_series"]["fisher_info"] for s in sensors]),
        "crb": average_curve([s["time_series"]["crb"] for s in sensors]),
        "effective_noise": average_curve([s["time_series"]["effective_noise"] for s in sensors]),
    }
    result["global"]["robustness_score"] = round(sum(s["reliability_weight"] for s in sensors) / len(sensors), 3) if sensors else 0.0
    result["global"]["collaboration_gain"] = 0.0
    return result
