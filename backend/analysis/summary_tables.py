from __future__ import annotations

def _iter_results(analysis: dict):
    for mode_key in analysis.get("mode_order", []):
        mode_pack = analysis.get("results", {}).get(mode_key, {})
        for config_key in mode_pack.get("config_order", []):
            result = mode_pack.get("results", {}).get(config_key, {})
            yield mode_key, mode_pack, config_key, result

def _series_stats(series: list[float]) -> tuple[float, float, float]:
    if not series:
        return 0.0, 0.0, 0.0
    return float(series[0]), float(series[-1]), float(sum(series)/len(series))

def build_all_tables(analysis: dict, selected_mode: str | None = None, selected_scope: str | None = None) -> dict:
    rows_global, rows_estimate, rows_noise, rows_sensor = [], [], [], []
    for mode_key, mode_pack, config_key, result in _iter_results(analysis):
        if selected_mode and selected_mode != "all" and mode_key != selected_mode:
            continue
        if selected_scope and selected_scope != "all" and result.get("scope") != selected_scope:
            continue

        g = result.get("global", {})
        ts = result.get("global_time_series", {})
        fi0, fi1, fia = _series_stats(ts.get("fisher_info", []))
        crb0, crb1, crba = _series_stats(ts.get("crb", []))
        est0, est1, esta = _series_stats(ts.get("estimate", []))
        n0, n1, na = _series_stats(ts.get("effective_noise", []))

        base = {
            "mode": mode_pack.get("mode_label", mode_key),
            "mode_key": mode_key,
            "scope": result.get("scope_label", result.get("scope", "none")),
            "family": result.get("family", "None"),
            "variant": result.get("label", "No Mitigation"),
            "variant_key": result.get("variant_key", config_key),
        }
        rows_global.append({
            **base,
            "final_fi": round(g.get("final_avg_fisher_info", 0.0), 3),
            "final_crb": round(g.get("final_avg_crb", 0.0), 3),
            "avg_noise": round(g.get("final_avg_effective_noise", 0.0), 3),
            "improvement": round(g.get("improvement_pct", 0.0), 2),
        })
        rows_estimate.append({
            **base,
            "initial": round(est0, 3),
            "final": round(est1, 3),
            "avg": round(esta, 3),
            "error": round(g.get("final_avg_estimate_error", 0.0), 3),
        })
        rows_noise.append({
            **base,
            "initial": round(n0, 3),
            "final": round(n1, 3),
            "avg": round(na, 3),
            "reduction": round(max(0.0, n0 - n1), 3),
        })
        for sensor in result.get("sensors", []):
            rows_sensor.append({
                "sensor": sensor.get("name", f"Sensor {sensor.get('id')}"),
                "mode": mode_pack.get("mode_label", mode_key),
                "mode_key": mode_key,
                "scope": result.get("scope_label", result.get("scope", "none")),
                "family": sensor.get("family", result.get("family", "None")),
                "variant": sensor.get("label", result.get("label", "No Mitigation")),
                "fi": round(sensor.get("final", {}).get("fisher_info", 0.0), 3),
                "crb": round(sensor.get("final", {}).get("crb", 0.0), 3),
                "noise": round(sensor.get("final", {}).get("effective_noise", 0.0), 3),
                "reliability": round(sensor.get("reliability_weight", 0.0), 3),
            })
    return {
        "global": rows_global,
        "estimate": rows_estimate,
        "noise": rows_noise,
        "sensor": rows_sensor,
    }
