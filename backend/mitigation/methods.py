from __future__ import annotations

import random
from typing import Dict, Tuple

METHOD_METADATA: Dict[str, dict] = {
    "baseline": {
        "label": "No Mitigation",
        "category": "Baseline",
        "description": "Reference case without any mitigation."
    },
    "dd": {
        "label": "Dynamical Decoupling",
        "category": "Execution-Time",
        "description": "Reduces time-based decoherence during execution."
    },
    "randomized": {
        "label": "Randomized Compiling",
        "category": "Execution-Time",
        "description": "Smooths error concentration by randomizing compilations."
    },
    "pauli": {
        "label": "Pauli Twirling",
        "category": "Execution-Time",
        "description": "Converts coherent errors into more stochastic noise."
    },
    "zne": {
        "label": "Zero Noise Extrapolation",
        "category": "Post-Processing",
        "description": "Extrapolates measurements toward the zero-noise limit."
    },
    "pec": {
        "label": "Probabilistic Error Cancellation",
        "category": "Post-Processing",
        "description": "Aggressive correction with mild instability."
    },
    "cdr": {
        "label": "Clifford Data Regression",
        "category": "Post-Processing",
        "description": "Regression-based correction learned from easy circuits."
    },
    "mem": {
        "label": "Measurement Error Mitigation",
        "category": "Post-Processing",
        "description": "Improves estimate quality more than raw noise level."
    },
    "combined": {
        "label": "Combined Selected Methods",
        "category": "Hybrid",
        "description": "Sequential application of all selected mitigation methods."
    },
}


def list_available_methods() -> list[dict]:
    ordered = ["dd", "randomized", "pauli", "zne", "pec", "cdr", "mem"]
    return [{"key": key, **METHOD_METADATA[key]} for key in ordered]


def _pec_variance(sensor_id: int, noise: float) -> float:
    seeded = random.Random(f"pec:{sensor_id}:{round(noise, 4)}")
    return seeded.uniform(-0.015, 0.015)


def apply_single_method(
    method_key: str,
    effective_noise: float,
    estimate_multiplier: float,
    sensor_id: int,
) -> Tuple[float, float, dict]:
    noise = float(effective_noise)
    multiplier = float(estimate_multiplier)
    details = {}

    if method_key == "dd":
        eta_dd = 0.85
        noise *= eta_dd
        details = {"eta_dd": round(eta_dd, 3)}
    elif method_key == "randomized":
        rho_rc = 0.90
        noise *= rho_rc
        details = {"rho_rc": round(rho_rc, 3)}
    elif method_key == "pauli":
        tau_pt = 0.92
        noise *= tau_pt
        details = {"tau_pt": round(tau_pt, 3)}
    elif method_key == "zne":
        lambda_zne = 1.5
        zne_factor = 0.75
        noise *= zne_factor
        details = {"lambda_zne": round(lambda_zne, 3), "zne_factor": round(zne_factor, 3)}
    elif method_key == "pec":
        kappa_pec = 0.70
        variance = _pec_variance(sensor_id, noise)
        noise = max(0.01, noise * kappa_pec + variance)
        details = {"kappa_pec": round(kappa_pec, 3), "pec_variance": round(variance, 3)}
    elif method_key == "cdr":
        beta_cdr = 0.80
        noise *= beta_cdr
        details = {"beta_cdr": round(beta_cdr, 3)}
    elif method_key == "mem":
        mu_mem = 1.05
        mem_noise_factor = 0.98
        noise *= mem_noise_factor
        multiplier *= mu_mem
        details = {"mu_mem": round(mu_mem, 3), "mem_noise_factor": round(mem_noise_factor, 3)}

    return max(0.01, min(noise, 1.0)), multiplier, details
