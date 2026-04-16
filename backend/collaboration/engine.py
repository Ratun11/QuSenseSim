from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from backend.collaboration.entangled_style import build_mode_result as build_entangled_result
from backend.collaboration.federated_style import build_mode_result as build_federated_result
from backend.collaboration.independent import build_mode_result as build_independent_result
from backend.mitigation.variants import compose_profile, get_variant, list_variant_families
from backend.physics.decay_models import coherence_factor, corrected_noise, deterministic_instability, relaxation_factor
from backend.physics.markovian import MARKOVIAN_EXPLANATION, build_time_axis
from backend.physics.t1_t2 import effective_decay_constants

MODE_METADATA = {
    "independent": {
        "label": "Independent",
        "description": "Each sensor senses on its own. Global metrics are aggregated after local sensing.",
    },
    "entangled": {
        "label": "Entangled-Style",
        "description": "Sensors gain shared sensitivity in low noise, but the mode becomes more fragile when collective noise rises.",
    },
    "federated": {
        "label": "Federated-Style",
        "description": "Sensors sense locally and then collaborate through reliability-weighted aggregation for better robustness under heterogeneity.",
    },
}

def _efficiency_score(fi_curve: List[float], noise_curve: List[float]) -> float:
    if not fi_curve or not noise_curve:
        return 0.0
    return sum(fi_curve) / max(sum(noise_curve) + len(noise_curve), 1e-6)

def _stability_score(coherence_curve: List[float]) -> float:
    return sum(coherence_curve) / len(coherence_curve) if coherence_curve else 0.0

def _sensor_time_series(sensor: dict, environment: dict, time_config: dict, variant_keys) -> dict:
    total_time = float(time_config["total_time"])
    times = time_config["times"]
    t1 = float(time_config["t1"])
    t2 = float(time_config["t2"])
    if isinstance(variant_keys, str):
        variant_keys = [variant_keys]
    variant_keys = [v for v in (variant_keys or []) if v and v != "baseline"]
    profile = compose_profile(variant_keys)

    base_noise = float(sensor.get("effective_noise", sensor.get("noise", 0.1)))
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

    estimate_curve, fi_curve, crb_curve, noise_curve, coherence_curve, relaxation_curve = [], [], [], [], [], []
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
            base_fi * coherence * (0.72 + 0.28 * relaxation) * (1.0 - 0.70 * effective_noise_t) * profile["fi_gain"]
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
    primary_variant_key = variant_keys[-1] if variant_keys else "baseline"
    variant = get_variant(primary_variant_key)

    return {
        "id": sensor["id"],
        "name": sensor["name"],
        "status": sensor.get("status", "stable"),
        "family": variant["family"],
        "label": variant["label"],
        "parameter_name": variant["parameter_name"],
        "parameter_value": variant["parameter_value"],
        "variant_key": primary_variant_key,
        "all_variant_keys": variant_keys,
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
    global_curves = {key: [] for key in ("estimate", "fisher_info", "crb", "effective_noise", "coherence", "relaxation")}
    global_curves["time"] = sensor_results[0]["time_series"]["time"]
    for idx in range(time_len):
        for key in ("estimate", "fisher_info", "crb", "effective_noise", "coherence", "relaxation"):
            global_curves[key].append(round(sum(item["time_series"][key][idx] for item in sensor_results) / len(sensor_results), 4))

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

def _build_scope_result(sensors: list[dict], environment: dict, resolved_time_config: dict, scope: str, variant_key: str | None = None, personalized_assignments: dict | None = None) -> dict:
    personalized_assignments = personalized_assignments or {}
    sensor_results = []
    for sensor in sensors:
        if scope == "personalized":
            sensor_variant = personalized_assignments.get(str(sensor["id"])) or personalized_assignments.get(sensor["id"]) or "baseline"
        elif scope == "uniform":
            sensor_variant = variant_key or "baseline"
        else:
            sensor_variant = "baseline"
        sensor_results.append(_sensor_time_series(sensor, environment, resolved_time_config, sensor_variant))

    baseline_final_fi = None
    if scope != "none":
        baseline_sensor_results = [_sensor_time_series(sensor, environment, resolved_time_config, "baseline") for sensor in sensors]
        baseline_final_fi = sum(item["final"]["fisher_info"] for item in baseline_sensor_results) / len(baseline_sensor_results)

    pack = _aggregate_global(sensor_results, baseline_final_fi=baseline_final_fi)

    if scope == "personalized":
        variant = {
            "family": "Personalized",
            "label": "Personalized Sensor Mitigation",
            "parameter_name": "assignment",
            "parameter_value": len([v for v in personalized_assignments.values() if v and v != "baseline"]),
            "key": "personalized",
        }
    else:
        variant = get_variant(variant_key or "baseline")

    return {
        "scope": scope,
        "family": variant["family"],
        "label": variant["label"],
        "parameter_name": variant["parameter_name"],
        "parameter_value": variant["parameter_value"],
        "variant_key": variant_key or ("personalized" if scope == "personalized" else "baseline"),
        "scope_label": "Personalized" if scope == "personalized" else ("Uniform" if scope == "uniform" else "No Mitigation"),
        "sensors": sensor_results,
        **pack,
    }

def _apply_mode(mode_key: str, scope_result: dict, sensor_count: int) -> dict:
    if mode_key == "independent":
        return build_independent_result(scope_result)
    if mode_key == "entangled":
        return build_entangled_result(scope_result, sensor_count=sensor_count)
    if mode_key == "federated":
        return build_federated_result(scope_result)
    return build_independent_result(scope_result)

def _score(mode_result: dict) -> float:
    g = mode_result["global"]
    return g["final_avg_fisher_info"] - 0.12 * g["final_avg_effective_noise"] + 0.08 * g.get("robustness_score", 0.0)

def run_collaboration_analysis(setup_state: dict, selected_modes: list[str], time_config: dict, selected_uniform_variants: list[str], personalized_assignments: dict | None) -> dict:
    selected_modes = [m for m in selected_modes if m in MODE_METADATA] or ["independent", "entangled", "federated"]
    sensors = setup_state.get("sensors", [])
    environment = setup_state.get("environment", {})
    times, dt = build_time_axis(time_config.get("total_time", 6.0), time_config.get("num_steps", 60))
    resolved_time_config = {
        "total_time": float(time_config.get("total_time", 6.0)),
        "num_steps": int(time_config.get("num_steps", 60)),
        "t1": float(time_config.get("t1", 7.0)),
        "t2": float(time_config.get("t2", 4.0)),
        "times": times,
        "dt": dt,
    }

    uniform_variants = [v for v in selected_uniform_variants if v and v != "baseline"]
    configs = [{"scope": "none", "variant_key": "baseline", "label_key": "baseline"}]
    for v in uniform_variants:
        configs.append({"scope": "uniform", "variant_key": v, "label_key": v})
    configs.append({"scope": "personalized", "variant_key": None, "label_key": "personalized"})

    mode_results = {}
    best_combo = {"mode": None, "config_key": None, "score": -1e9}
    config_order = [c["label_key"] for c in configs]

    for mode_key in selected_modes:
        transformed = {}
        for config in configs:
            base_scope_result = _build_scope_result(
                sensors=sensors,
                environment=environment,
                resolved_time_config=resolved_time_config,
                scope=config["scope"],
                variant_key=config["variant_key"],
                personalized_assignments=personalized_assignments,
            )
            transformed_result = _apply_mode(mode_key, deepcopy(base_scope_result), sensor_count=len(sensors))
            transformed[config["label_key"]] = transformed_result
            score = _score(transformed_result)
            if score > best_combo["score"]:
                best_combo = {"mode": mode_key, "config_key": config["label_key"], "score": score}
        mode_results[mode_key] = {
            "mode_key": mode_key,
            "mode_label": MODE_METADATA[mode_key]["label"],
            "mode_description": MODE_METADATA[mode_key]["description"],
            "config_order": config_order,
            "results": transformed,
        }

    rows = []
    for mode_key, mode_pack in mode_results.items():
        for config_key in mode_pack["config_order"]:
            result = mode_pack["results"][config_key]
            g = result["global"]
            rows.append({
                "mode": mode_key,
                "mode_label": MODE_METADATA[mode_key]["label"],
                "scope": result["scope"],
                "scope_label": result["scope_label"],
                "family": result["family"],
                "variant": result["label"],
                "parameter_name": result["parameter_name"],
                "parameter_value": result["parameter_value"],
                "config_key": config_key,
                "final_avg_fi": g["final_avg_fisher_info"],
                "final_avg_crb": g["final_avg_crb"],
                "final_avg_noise": g["final_avg_effective_noise"],
                "stability_score": g["stability_score"],
                "robustness_score": g.get("robustness_score", 0.0),
                "efficiency_score": g["efficiency_score"],
                "improvement_pct": g["improvement_pct"],
                "is_best": best_combo["mode"] == mode_key and best_combo["config_key"] == config_key,
            })

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
        "selected_modes": selected_modes,
        "mode_order": selected_modes,
        "config_order": config_order,
        "sensor_names": [{"id": s["id"], "name": s["name"]} for s in sensors],
        "mode_metadata": MODE_METADATA,
        "variant_families": list_variant_families(),
        "best_combo": {"mode": best_combo["mode"], "config_key": best_combo["config_key"]},
        "results": mode_results,
        "global_summary": rows,
        "personalized_assignments": personalized_assignments or {},
    }
