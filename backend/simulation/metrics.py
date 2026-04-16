import math


def compute_metrics(environment, noise_data: dict) -> dict:
    gamma = noise_data["effective_noise"]  # Markovian noise rate
    t = 1.0  # sensing time, kept fixed in this phase
    rotation_factor = noise_data.get("rotation_factor", 0.15)
    qubit_factor = 0.35 * noise_data.get("qubits", 1)
    circuit_factor = noise_data.get("circuit_factor", 0.0)
    source_factor = 0.03 * noise_data.get("inside_source_count", 0)

    estimate = environment.field_strength * math.exp(-gamma * t) + environment.phase_shift * rotation_factor
    fisher_info = max(
        0.1,
        5 * math.exp(-2 * gamma * t) + qubit_factor + circuit_factor + source_factor,
    )
    crb = 1 / fisher_info

    return {
        "estimate": round(estimate, 3),
        "fisher_info": round(fisher_info, 3),
        "crb": round(crb, 3),
        "noise_rate_gamma": round(gamma, 3),
        "sensing_time": t,
    }
