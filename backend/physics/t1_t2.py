from __future__ import annotations


def effective_decay_constants(sensor: dict, environment: dict, total_time: float, t1: float, t2: float) -> tuple[float, float, dict]:
    base_noise = float(sensor.get("effective_noise", sensor.get("noise", 0.1)))
    circuit_noise = float(sensor.get("circuit_noise", 0.0))
    spatial_noise = float(sensor.get("spatial_noise", 0.0))
    environment_noise = float(sensor.get("environment_noise", environment.get("global_noise", 0.15)))
    source_modifier = float(sensor.get("source_noise_modifier", 0.0))
    num_cx = int(sensor.get("num_cx", 0))
    num_rot = int(sensor.get("num_rotation_gates", 0))

    noise_load = 0.55 * base_noise + 0.20 * environment_noise + 0.15 * circuit_noise + 0.10 * spatial_noise
    acceleration = max(0.0, source_modifier)
    protection = max(0.0, -source_modifier)

    t1_eff = t1 * (1.0 - 0.18 * noise_load - 0.08 * acceleration + 0.06 * protection)
    t2_eff = t2 * (1.0 - 0.28 * noise_load - 0.12 * acceleration + 0.08 * protection)

    t1_eff *= max(0.70, 1.0 - 0.02 * num_cx)
    t2_eff *= max(0.62, 1.0 - 0.03 * num_cx - 0.01 * num_rot)

    t1_eff = max(0.25, min(3.5 * total_time, t1_eff))
    t2_eff = max(0.20, min(3.0 * total_time, t2_eff))

    return t1_eff, t2_eff, {
        "noise_load": round(noise_load, 3),
        "source_acceleration": round(acceleration, 3),
        "source_protection": round(protection, 3),
    }
