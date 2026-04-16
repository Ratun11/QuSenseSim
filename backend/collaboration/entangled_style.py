from __future__ import annotations

from copy import deepcopy

from backend.collaboration.aggregation import average_curve


def _clamp(value: float, low: float = 0.01, high: float = 10.0) -> float:
    return max(low, min(high, value))


def build_mode_result(base_method_result: dict, sensor_count: int) -> dict:
    result = deepcopy(base_method_result)
    sensors = result["sensors"]
    if not sensors:
        return result

    avg_noise = sum(s["final"]["effective_noise"] for s in sensors) / len(sensors)
    avg_quality = 1.0 - avg_noise
    sensitivity_gain = 1.0 + 0.12 * (sensor_count - 1) * max(0.2, avg_quality)
    fragility_factor = 1.0 + 0.16 * (sensor_count - 1) * (0.7 + avg_noise)

    for sensor in sensors:
        ts = sensor["time_series"]
        new_fi = []
        new_crb = []
        new_est = []
        new_noise = []
        new_coh = []
        new_relax = []

        for idx, t in enumerate(ts["time"]):
            base_noise = ts["effective_noise"][idx]
            base_fi = ts["fisher_info"][idx]
            base_est = ts["estimate"][idx]
            base_coh = ts["coherence"][idx]
            base_relax = ts["relaxation"][idx]

            coupled_noise = min(0.995, base_noise * (1.0 + 0.09 * (sensor_count - 1)) * (1.0 + 0.12 * avg_noise))
            coupled_coh = max(0.01, base_coh * (1.0 - 0.04 * (sensor_count - 1) * max(0.25, base_noise)))
            coupled_relax = max(0.01, base_relax * (1.0 - 0.02 * (sensor_count - 1) * max(0.2, base_noise)))

            fi = _clamp(base_fi * sensitivity_gain * coupled_coh * (1.0 - 0.55 * coupled_noise) / max(1.0, fragility_factor * 0.55))
            crb = 1.0 / fi
            est = max(0.0, base_est * (1.0 + 0.03 * (sensor_count - 1) * avg_quality) * (1.0 - 0.10 * coupled_noise))

            new_noise.append(round(coupled_noise, 4))
            new_coh.append(round(coupled_coh, 4))
            new_relax.append(round(coupled_relax, 4))
            new_fi.append(round(fi, 4))
            new_crb.append(round(crb, 4))
            new_est.append(round(est, 4))

        ts["effective_noise"] = new_noise
        ts["coherence"] = new_coh
        ts["relaxation"] = new_relax
        ts["fisher_info"] = new_fi
        ts["crb"] = new_crb
        ts["estimate"] = new_est

        sensor["t1_eff"] = round(sensor["t1_eff"] / (1.0 + 0.05 * (sensor_count - 1)), 3)
        sensor["t2_eff"] = round(sensor["t2_eff"] / (1.0 + 0.11 * (sensor_count - 1)), 3)
        sensor["final"]["estimate"] = round(new_est[-1], 3)
        sensor["final"]["fisher_info"] = round(new_fi[-1], 3)
        sensor["final"]["crb"] = round(new_crb[-1], 3)
        sensor["final"]["effective_noise"] = round(new_noise[-1], 3)
        sensor["final"]["stability_score"] = round(sum(new_coh) / len(new_coh), 3)
        sensor["final"]["efficiency_score"] = round(sum(new_fi) / max(sum(new_noise) + len(new_noise), 1e-6), 3)
        sensor["reliability_weight"] = round(max(0.05, 1.0 - sensor["final"]["effective_noise"]), 3)
        sensor["contribution_score"] = round(sensor["final"]["fisher_info"] * sensor["reliability_weight"], 3)

    result["global_time_series"] = {
        "time": sensors[0]["time_series"]["time"],
        "estimate": average_curve([s["time_series"]["estimate"] for s in sensors]),
        "fisher_info": average_curve([s["time_series"]["fisher_info"] for s in sensors]),
        "crb": average_curve([s["time_series"]["crb"] for s in sensors]),
        "effective_noise": average_curve([s["time_series"]["effective_noise"] for s in sensors]),
    }

    final_avg_fi = sum(s["final"]["fisher_info"] for s in sensors) / len(sensors)
    final_avg_crb = sum(s["final"]["crb"] for s in sensors) / len(sensors)
    final_avg_noise = sum(s["final"]["effective_noise"] for s in sensors) / len(sensors)
    stability = sum(s["final"]["stability_score"] for s in sensors) / len(sensors)
    efficiency = sum(s["final"]["efficiency_score"] for s in sensors) / len(sensors)
    final_est = sum(s["final"]["estimate"] for s in sensors) / len(sensors)

    result["global"]["final_avg_fisher_info"] = round(final_avg_fi, 3)
    result["global"]["final_avg_crb"] = round(final_avg_crb, 3)
    result["global"]["final_avg_effective_noise"] = round(final_avg_noise, 3)
    result["global"]["final_avg_estimate"] = round(final_est, 3)
    result["global"]["stability_score"] = round(stability, 3)
    result["global"]["efficiency_score"] = round(efficiency, 3)
    result["global"]["robustness_score"] = round(max(0.05, 1.0 - final_avg_noise) * 0.9, 3)
    result["global"]["collaboration_gain"] = round((sensitivity_gain - 1.0) * 100.0, 2)
    return result
