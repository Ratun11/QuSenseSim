from __future__ import annotations

def build_rankings(analysis: dict) -> dict:
    rows = analysis.get("global_summary", [])
    if not rows:
        return {
            "best_overall_method": None,
            "best_variant": None,
            "best_mode": None,
            "best_personalized_setup": None,
            "personalized_gain_over_uniform": None,
            "interpretation": "No analysis results available yet.",
        }

    best_overall = max(rows, key=lambda r: (r.get("final_avg_fi", 0.0), -r.get("final_avg_noise", 0.0)))
    best_variant = max(
        [r for r in rows if r.get("scope") == "uniform"],
        key=lambda r: r.get("final_avg_fi", 0.0),
        default=None,
    )

    mode_best = {}
    for row in rows:
        mode = row["mode"]
        if mode not in mode_best or row["final_avg_fi"] > mode_best[mode]["final_avg_fi"]:
            mode_best[mode] = row
    best_mode = max(mode_best.values(), key=lambda r: r["final_avg_fi"]) if mode_best else None

    personalized_rows = [r for r in rows if r.get("scope") == "personalized"]
    best_personalized = max(personalized_rows, key=lambda r: r.get("final_avg_fi", 0.0), default=None)

    best_uniform = max([r for r in rows if r.get("scope") == "uniform"], key=lambda r: r.get("final_avg_fi", 0.0), default=None)
    personalized_gain = None
    if best_personalized and best_uniform and best_uniform["final_avg_fi"]:
        personalized_gain = round(((best_personalized["final_avg_fi"] - best_uniform["final_avg_fi"]) / best_uniform["final_avg_fi"]) * 100.0, 2)

    interpretation = f"{best_overall['mode_label']} with {best_overall['variant']} is the strongest overall configuration."
    if best_personalized:
        interpretation += f" The best personalized setup appears in {best_personalized['mode_label']}."
    if personalized_gain is not None:
        interpretation += f" Personalized mitigation changes FI by {personalized_gain}% compared with the best uniform variant."

    return {
        "best_overall_method": best_overall,
        "best_variant": best_variant,
        "best_mode": best_mode,
        "best_personalized_setup": best_personalized,
        "personalized_gain_over_uniform": personalized_gain,
        "interpretation": interpretation,
    }
