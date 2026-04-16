from __future__ import annotations

from typing import Dict, List

from backend.mitigation.methods import METHOD_METADATA, list_available_methods
from backend.physics.decay_models import coherence_factor, corrected_noise, deterministic_instability, relaxation_factor
from backend.physics.markovian import MARKOVIAN_EXPLANATION, build_time_axis, clamp
from backend.physics.t1_t2 import effective_decay_constants


def _compose_method_profile(method_keys: List[str]) -> dict:
    profile = {
        "t1_multiplier": 1.0,
        "t2_multiplier": 1.0,
        "noise_alpha_multiplier": 1.0,
        "noise_post_gain": 1.0,
        "estimate_gain": 1.0,
        "fi_gain": 1.0,
        "instability_amplitude": 0.0,
        "detail_variables": {},
    }

    for key in method_keys:
        if key == "dd":
            profile["t2_multiplier"] *= 1.28
            profile["t1_multiplier"] *= 1.05
            profile["detail_variables"]["eta_dd"] = 1.28
        elif key == "randomized":
            profile["noise_alpha_multiplier"] *= 0.88
            profile["detail_variables"]["rho_rc"] = 0.88
        elif key == "pauli":
            profile["noise_post_gain"] *= 0.96
            profile["t2_multiplier"] *= 1.08
            profile["detail_variables"]["tau_pt"] = 0.96
        elif key == "zne":
            profile["fi_gain"] *= 1.12
            profile["noise_post_gain"] *= 0.93
            profile["detail_variables"]["lambda_zne"] = 1.5
        elif key == "pec":
            profile["fi_gain"] *= 1.18
            profile["noise_post_gain"] *= 0.88
            profile["noise_alpha_multiplier"] *= 0.85
            profile["instability_amplitude"] += 0.012
            profile["detail_variables"]["kappa_pec"] = 0.88
        elif key == "cdr":
            profile["estimate_gain"] *= 1.04
            profile["fi_gain"] *= 1.08
            profile["noise_post_gain"] *= 0.95
            profile["detail_variables"]["beta_cdr"] = 1.08
        elif key == "mem":
            profile["estimate_gain"] *= 1.03
            profile["noise_post_gain"] *= 0.985
            profile["detail_variables"]["mu_mem"] = 1.03

    return profile


def _efficiency_score(fi_curve: List[float], noise_curve: List[float]) -> float:
    if not fi_curve or not noise_curve:
        return 0.0
    fi_area = sum(fi_curve)
    noise_area = sum(noise_curve)
    return fi_area / max(noise_area + len(noise_curve), 1e-6)


def _stability_score(coherence_curve: List[float]) -> float:
    if not coherence_curve:
        return 0.0
    return sum(coherence_curve) / len(coherence_curve)


def _sensor_time_series(sensor: dict, environment: dict, time_config: dict, method_keys: List[str]) -> dict:
    total_time = float(time_config["total_time"])
    times = time_config["times"]
    dt = float(time_config["dt"])
    t1 = float(time_config["t1"])
    t2 = float(time_config["t2"])

    profile = _compose_method_profile(method_keys)
    base_noise = float(sensor.get("effective_noise", sensor.get("noise", 0.1)))
    base_estimate = float(sensor.get("estimate", 0.5))
    base_fi = float(sensor.get("fisher_info", 1.0))
    field_strength = float(environment.get("field_strength", 0.6))
    phase_shift = float(environment.get("phase_shift", 0.5))
    circuit_noise = float(sensor.get("circuit_noise", 0.0))
    spatial_noise = float(sensor.get("spatial_noise", 0.0))
    source_modifier = float(sensor.get("source_noise_modifier", 0.0))
    inside_sources = int(sensor.get("inside_source_count", 0))

    t1_eff_raw, t2_eff_raw, decay_context = effective_decay_constants(sensor, environment, total_time, t1, t2)
    t1_eff = max(0.2, t1_eff_raw * profile["t1_multiplier"])
    t2_eff = max(0.18, t2_eff_raw * profile["t2_multiplier"])

    tau_noise = max(0.2, 0.45 * total_time + 0.25 * total_time * base_noise + 0.08 * inside_sources)
    alpha = (0.16 + 0.55 * base_noise + 0.25 * circuit_noise + 0.18 * spatial_noise + max(0.0, source_modifier) * 0.6)
    alpha *= profile["noise_alpha_multiplier"]
    alpha = max(0.02, min(alpha, 0.95))

    estimate_curve = []
    fi_curve = []
    crb_curve = []
    noise_curve = []
    coherence_curve = []
    relaxation_curve = []

    for t in times:
        relaxation = relaxation_factor(t, t1_eff)
        coherence = coherence_factor(t, t2_eff)
        decoherence_penalty = 0.035 * (1.0 - coherence) + 0.025 * (1.0 - relaxation)
        instability = deterministic_instability(t, total_time, profile["instability_amplitude"])
        effective_noise_t = corrected_noise(
            base_noise=base_noise,
            t=t,
            tau=tau_noise,
            alpha=alpha,
            decoherence_penalty=decoherence_penalty,
            instability=instability,
            post_gain=profile["noise_post_gain"],
        )

        estimate_t = (
            field_strength * relaxation * (0.58 + 0.42 * coherence)
            + phase_shift * 0.15 * coherence
        ) * profile["estimate_gain"]

        fi_t = max(
            0.1,
            base_fi
            * coherence
            * (0.72 + 0.28 * relaxation)
            * (1.0 - 0.70 * effective_noise_t)
            * profile["fi_gain"]
        )
        crb_t = 1.0 / fi_t

        estimate_curve.append(round(estimate_t, 4))
        fi_curve.append(round(fi_t, 4))
        crb_curve.append(round(crb_t, 4))
        noise_curve.append(round(effective_noise_t, 4))
        coherence_curve.append(round(coherence, 4))
        relaxation_curve.append(round(relaxation, 4))

    final_estimate = estimate_curve[-1]
    ideal_final = (field_strength + phase_shift * 0.15) * profile["estimate_gain"]
    final_error = abs(ideal_final - final_estimate)
    final_accuracy = max(0.0, 1.0 - (final_error / max(ideal_final, 1e-6)))

    return {
        "id": sensor["id"],
        "name": sensor["name"],
        "status": sensor.get("status", "stable"),
        "base_effective_noise": round(base_noise, 3),
        "t1_eff": round(t1_eff, 3),
        "t2_eff": round(t2_eff, 3),
        "tau_noise": round(tau_noise, 3),
        "alpha_noise": round(alpha, 3),
        "method_variables": {k: round(v, 3) if isinstance(v, (int, float)) else v for k, v in profile["detail_variables"].items()},
        "decay_context": decay_context,
        "time_series": {
            "time": [round(t, 4) for t in times],
            "estimate": estimate_curve,
            "fisher_info": fi_curve,
            "crb": crb_curve,
            "effective_noise": noise_curve,
            "coherence": coherence_curve,
            "relaxation": relaxation_curve,
        },
        "final": {
            "estimate": round(final_estimate, 3),
            "fisher_info": round(fi_curve[-1], 3),
            "crb": round(crb_curve[-1], 3),
            "effective_noise": round(noise_curve[-1], 3),
            "stability_score": round(_stability_score(coherence_curve), 3),
            "efficiency_score": round(_efficiency_score(fi_curve, noise_curve), 3),
            "estimate_error": round(final_error, 3),
            "accuracy": round(final_accuracy, 3),
        },
    }


def _aggregate_global(sensor_results: List[dict], baseline_final_fi: float | None = None) -> dict:
    final_avg_fi = sum(item["final"]["fisher_info"] for item in sensor_results) / len(sensor_results)
    final_avg_crb = sum(item["final"]["crb"] for item in sensor_results) / len(sensor_results)
    final_avg_noise = sum(item["final"]["effective_noise"] for item in sensor_results) / len(sensor_results)
    final_avg_estimate = sum(item["final"]["estimate"] for item in sensor_results) / len(sensor_results)
    avg_stability = sum(item["final"]["stability_score"] for item in sensor_results) / len(sensor_results)
    avg_efficiency = sum(item["final"]["efficiency_score"] for item in sensor_results) / len(sensor_results)
    avg_error = sum(item["final"]["estimate_error"] for item in sensor_results) / len(sensor_results)
    avg_accuracy = sum(item["final"]["accuracy"] for item in sensor_results) / len(sensor_results)

    improvement = 0.0
    if baseline_final_fi and baseline_final_fi > 0:
        improvement = ((final_avg_fi - baseline_final_fi) / baseline_final_fi) * 100.0

    time_len = len(sensor_results[0]["time_series"]["time"])
    global_curves = {
        "time": sensor_results[0]["time_series"]["time"],
        "estimate": [],
        "fisher_info": [],
        "crb": [],
        "effective_noise": [],
        "coherence": [],
        "relaxation": [],
    }

    for idx in range(time_len):
        for key in ("estimate", "fisher_info", "crb", "effective_noise", "coherence", "relaxation"):
            avg_value = sum(item["time_series"][key][idx] for item in sensor_results) / len(sensor_results)
            global_curves[key].append(round(avg_value, 4))

    return {
        "global": {
            "final_avg_estimate": round(final_avg_estimate, 3),
            "final_avg_fisher_info": round(final_avg_fi, 3),
            "final_avg_crb": round(final_avg_crb, 3),
            "final_avg_effective_noise": round(final_avg_noise, 3),
            "stability_score": round(avg_stability, 3),
            "efficiency_score": round(avg_efficiency, 3),
            "final_avg_estimate_error": round(avg_error, 3),
            "final_avg_accuracy": round(avg_accuracy, 3),
            "improvement_pct": round(improvement, 2),
        },
        "global_time_series": global_curves,
    }


def run_time_evolution(state: Dict, selected_methods: List[str], time_config: Dict) -> Dict:
    sensors = state.get("sensors", [])
    environment = state.get("environment", {})

    times, dt = build_time_axis(time_config.get("total_time", 6.0), time_config.get("num_steps", 50))
    resolved_time_config = {
        "total_time": float(time_config.get("total_time", 6.0)),
        "num_steps": int(time_config.get("num_steps", 50)),
        "t1": float(time_config.get("t1", 5.0)),
        "t2": float(time_config.get("t2", 3.0)),
        "times": times,
        "dt": dt,
    }

    selected_methods = [m for m in selected_methods if m in METHOD_METADATA and m not in {"baseline", "combined"}]
    results = {}
    method_order = ["baseline"]

    baseline_sensor_results = [_sensor_time_series(sensor, environment, resolved_time_config, []) for sensor in sensors]
    baseline_pack = _aggregate_global(baseline_sensor_results, baseline_final_fi=None)
    results["baseline"] = {
        "key": "baseline",
        "label": METHOD_METADATA["baseline"]["label"],
        "category": METHOD_METADATA["baseline"]["category"],
        "sensors": baseline_sensor_results,
        **baseline_pack,
    }
    baseline_final_fi = results["baseline"]["global"]["final_avg_fisher_info"]

    for method_key in selected_methods:
        sensor_results = [_sensor_time_series(sensor, environment, resolved_time_config, [method_key]) for sensor in sensors]
        pack = _aggregate_global(sensor_results, baseline_final_fi=baseline_final_fi)
        results[method_key] = {
            "key": method_key,
            "label": METHOD_METADATA[method_key]["label"],
            "category": METHOD_METADATA[method_key]["category"],
            "sensors": sensor_results,
            **pack,
        }
        method_order.append(method_key)

    if len(selected_methods) > 1:
        sensor_results = [_sensor_time_series(sensor, environment, resolved_time_config, selected_methods) for sensor in sensors]
        pack = _aggregate_global(sensor_results, baseline_final_fi=baseline_final_fi)
        results["combined"] = {
            "key": "combined",
            "label": METHOD_METADATA["combined"]["label"],
            "category": METHOD_METADATA["combined"]["category"],
            "sensors": sensor_results,
            **pack,
        }
        method_order.append("combined")

    ranked = sorted(
        [key for key in results.keys() if key != "baseline"],
        key=lambda k: (
            results[k]["global"]["final_avg_fisher_info"],
            results[k]["global"]["stability_score"],
            results[k]["global"]["efficiency_score"],
        ),
        reverse=True,
    )
    best_method = ranked[0] if ranked else "baseline"

    return {
        "markovian_explanation": MARKOVIAN_EXPLANATION,
        "time_config": {
            "total_time": round(resolved_time_config["total_time"], 3),
            "num_steps": resolved_time_config["num_steps"],
            "dt": round(resolved_time_config["dt"], 4),
            "t1": round(resolved_time_config["t1"], 3),
            "t2": round(resolved_time_config["t2"], 3),
        },
        "time_points": [round(t, 4) for t in times],
        "method_order": method_order,
        "best_method": best_method,
        "results": results,
        "available_methods": list_available_methods(),
        "sensor_names": [{"id": sensor["id"], "name": sensor["name"]} for sensor in sensors],
    }
