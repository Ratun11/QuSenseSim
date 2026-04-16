from __future__ import annotations


MARKOVIAN_EXPLANATION = (
    "Markovian noise is memoryless: the sensor state at each time step depends on the current "
    "noise rates, circuit complexity, spatial exposure, and chosen mitigation, not on a long "
    "internal history. This is appropriate here because QuSenseSim is designed as an interactive, "
    "physically interpretable simulator rather than a full density-matrix hardware solver."
)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def build_time_axis(total_time: float, num_steps: int) -> tuple[list[float], float]:
    total_time = max(0.2, float(total_time))
    num_steps = max(5, int(num_steps))
    dt = total_time / (num_steps - 1)
    times = [round(i * dt, 6) for i in range(num_steps)]
    return times, dt
