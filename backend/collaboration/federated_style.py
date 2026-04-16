from __future__ import annotations

from copy import deepcopy

from backend.collaboration.aggregation import weighted_curve, weighted_scalar


def build_mode_result(base_method_result: dict) -> dict:
    result = deepcopy(base_method_result)
    sensors = result["sensors"]
    if not sensors:
        return result

    reliability_weights = []
    for sensor in sensors:
        ts = sensor["time_series"]
        final_noise = sensor["final"]["effective_noise"]
        stability = sensor["final"]["stability_score"]
        reliability = max(0.05, 0.65 * (1.0 - final_noise) + 0.35 * stability)
        reliability_weights.append(reliability)
        sensor["reliability_weight"] = round(reliability, 3)
        sensor["contribution_score"] = round(sensor["final"]["fisher_info"] * reliability, 3)

    result["global_time_series"] = {
        "time": sensors[0]["time_series"]["time"],
        "estimate": weighted_curve([s["time_series"]["estimate"] for s in sensors], reliability_weights),
        "fisher_info": weighted_curve([s["time_series"]["fisher_info"] for s in sensors], reliability_weights),
        "crb": weighted_curve([s["time_series"]["crb"] for s in sensors], reliability_weights),
        "effective_noise": weighted_curve([s["time_series"]["effective_noise"] for s in sensors], reliability_weights),
    }

    final_avg_fi = weighted_scalar([s["final"]["fisher_info"] for s in sensors], reliability_weights)
    final_avg_crb = weighted_scalar([s["final"]["crb"] for s in sensors], reliability_weights)
    final_avg_noise = weighted_scalar([s["final"]["effective_noise"] for s in sensors], reliability_weights)
    final_avg_estimate = weighted_scalar([s["final"]["estimate"] for s in sensors], reliability_weights)
    stability = weighted_scalar([s["final"]["stability_score"] for s in sensors], reliability_weights)
    efficiency = weighted_scalar([s["final"]["efficiency_score"] for s in sensors], reliability_weights)

    result["global"]["final_avg_fisher_info"] = round(final_avg_fi, 3)
    result["global"]["final_avg_crb"] = round(final_avg_crb, 3)
    result["global"]["final_avg_effective_noise"] = round(final_avg_noise, 3)
    result["global"]["final_avg_estimate"] = round(final_avg_estimate, 3)
    result["global"]["stability_score"] = round(stability, 3)
    result["global"]["efficiency_score"] = round(efficiency, 3)
    result["global"]["robustness_score"] = round(sum(reliability_weights) / len(reliability_weights), 3)
    result["global"]["collaboration_gain"] = round(max(0.0, (final_avg_fi - (sum(s["final"]["fisher_info"] for s in sensors) / len(sensors)))) * 10.0, 2)
    return result
