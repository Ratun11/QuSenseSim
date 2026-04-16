from __future__ import annotations

import math

from backend.physics.markovian import clamp


def relaxation_factor(t: float, t1_eff: float) -> float:
    return math.exp(-t / max(t1_eff, 1e-6))


def coherence_factor(t: float, t2_eff: float) -> float:
    return math.exp(-t / max(t2_eff, 1e-6))


def time_noise_term(t: float, tau: float, alpha: float) -> float:
    return max(0.0, alpha) * (1.0 - math.exp(-t / max(tau, 1e-6)))


def deterministic_instability(t: float, total_time: float, amplitude: float) -> float:
    if amplitude <= 0:
        return 0.0
    phase = (2.0 * math.pi * t) / max(total_time, 1e-6)
    return amplitude * math.sin(phase)


def corrected_noise(base_noise: float, t: float, tau: float, alpha: float, decoherence_penalty: float, instability: float, post_gain: float) -> float:
    raw = base_noise + time_noise_term(t, tau, alpha) + decoherence_penalty + instability
    return clamp(raw * post_gain, 0.01, 1.0)
