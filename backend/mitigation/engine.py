from __future__ import annotations

import math
from typing import Dict, List

from backend.mitigation.methods import METHOD_METADATA, apply_single_method


def compute_metrics(noise: float, field_strength: float, phase_shift: float, estimate_multiplier: float = 1.0) -> dict:
    gamma = max(0.01, noise)
    sensing_time = 1.0

    raw_estimate = field_strength * math.exp(-gamma * sensing_time) + phase_shift * 0.15
    estimate = raw_estimate * estimate_multiplier
    fisher_info = max(0.1, 5.5 * math.exp(-2 * gamma * sensing_time) + 0.7 - abs(phase_shift - 0.5))
    crb = 1.0 / fisher_info

    ideal_estimate = field_strength + phase_shift * 0.15
    estimate_error = abs(ideal_estimate - estimate)
    accuracy = max(0.0, 1.0 - (estimate_error / max(ideal_estimate, 1e-6)))

    return {
        "estimate": round(estimate, 3),
        "fisher_info": round(fisher_info, 3),
        "crb": round(crb, 3),
        "effective_noise": round(gamma, 3),
        "estimate_error": round(estimate_error, 3),
        "accuracy": round(accuracy, 3),
        "noise_rate_gamma": round(gamma, 3),
        "sensing_time": sensing_time,
    }


def _run_method_on_sensor(method_keys: List[str], sensor: dict, environment: dict) -> dict:
    base_noise = float(sensor.get("effective_noise", sensor.get("noise", 0.1)))
    noise = base_noise
    estimate_multiplier = 1.0
    method_trace = []

    for key in method_keys:
        before_noise = noise
        noise, estimate_multiplier, details = apply_single_method(key, noise, estimate_multiplier, int(sensor["id"]))
        method_trace.append({
            "method": key,
            "noise_before": round(before_noise, 3),
            "noise_after": round(noise, 3),
            "details": details,
        })

    metrics = compute_metrics(
        noise=noise,
        field_strength=float(environment["field_strength"]),
        phase_shift=float(environment["phase_shift"]),
        estimate_multiplier=estimate_multiplier,
    )

    return {
        "id": sensor["id"],
        "name": sensor["name"],
        "status": sensor.get("status", "stable"),
        "baseline_noise": round(base_noise, 3),
        "method_trace": method_trace,
        **metrics,
    }


def _aggregate(method_key: str, label: str, category: str, sensor_results: List[dict], baseline_fi: float | None = None) -> dict:
    avg_estimate = sum(item["estimate"] for item in sensor_results) / len(sensor_results)
    avg_fi = sum(item["fisher_info"] for item in sensor_results) / len(sensor_results)
    avg_crb = sum(item["crb"] for item in sensor_results) / len(sensor_results)
    avg_noise = sum(item["effective_noise"] for item in sensor_results) / len(sensor_results)
    avg_error = sum(item["estimate_error"] for item in sensor_results) / len(sensor_results)
    avg_accuracy = sum(item["accuracy"] for item in sensor_results) / len(sensor_results)

    improvement = 0.0
    if baseline_fi and baseline_fi > 0:
        improvement = ((avg_fi - baseline_fi) / baseline_fi) * 100.0

    return {
        "key": method_key,
        "label": label,
        "category": category,
        "sensors": sensor_results,
        "global": {
            "avg_estimate": round(avg_estimate, 3),
            "avg_fisher_info": round(avg_fi, 3),
            "avg_crb": round(avg_crb, 3),
            "avg_effective_noise": round(avg_noise, 3),
            "avg_estimate_error": round(avg_error, 3),
            "avg_accuracy": round(avg_accuracy, 3),
            "improvement_pct": round(improvement, 2),
        },
    }


def run_mitigation_pipeline(state: Dict, selected_methods: List[str]) -> Dict:
    sensors = state.get("sensors", [])
    environment = state.get("environment", {})
    selected_methods = [m for m in selected_methods if m in METHOD_METADATA and m not in {"baseline", "combined"}]

    baseline_sensor_results = [
        _run_method_on_sensor([], sensor, environment) for sensor in sensors
    ]
    baseline_result = _aggregate(
        "baseline",
        METHOD_METADATA["baseline"]["label"],
        METHOD_METADATA["baseline"]["category"],
        baseline_sensor_results,
        baseline_fi=None,
    )
    baseline_avg_fi = baseline_result["global"]["avg_fisher_info"]

    results = {"baseline": baseline_result}
    method_order = ["baseline"]

    for method_key in selected_methods:
        sensor_results = [_run_method_on_sensor([method_key], sensor, environment) for sensor in sensors]
        results[method_key] = _aggregate(
            method_key,
            METHOD_METADATA[method_key]["label"],
            METHOD_METADATA[method_key]["category"],
            sensor_results,
            baseline_fi=baseline_avg_fi,
        )
        method_order.append(method_key)

    if len(selected_methods) > 1:
        sensor_results = [_run_method_on_sensor(selected_methods, sensor, environment) for sensor in sensors]
        results["combined"] = _aggregate(
            "combined",
            METHOD_METADATA["combined"]["label"],
            METHOD_METADATA["combined"]["category"],
            sensor_results,
            baseline_fi=baseline_avg_fi,
        )
        method_order.append("combined")

    ranked = sorted(
        [key for key in results.keys() if key != "baseline"],
        key=lambda k: (results[k]["global"]["avg_fisher_info"], -results[k]["global"]["avg_effective_noise"]),
        reverse=True,
    )
    best_method = ranked[0] if ranked else "baseline"

    return {
        "method_order": method_order,
        "best_method": best_method,
        "results": results,
        "available_methods": [key for key in METHOD_METADATA.keys() if key not in {"baseline", "combined"}],
        "sensor_names": [{"id": sensor["id"], "name": sensor["name"]} for sensor in sensors],
    }
