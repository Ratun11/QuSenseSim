from backend.noise.noise_models import (
    compute_circuit_noise,
    compute_environment_noise,
    compute_sensor_component_noise,
    compute_spatial_noise,
)
from backend.noise.status import get_status
from backend.environment.source_engine import compute_source_effects


def compute_noise_breakdown(sensor, environment, circuit, sources):
    sensor_components = compute_sensor_component_noise(sensor)
    environment_noise = compute_environment_noise(environment)
    circuit_noise, circuit_stats = compute_circuit_noise(
        circuit,
        enabled=environment.circuit_noise_enabled,
    )
    spatial_noise = compute_spatial_noise(
        sensor,
        enabled=environment.spatial_noise_enabled,
    )
    source_data = compute_source_effects(
        sensor,
        sources,
        enabled=environment.source_effects_enabled,
    )

    measurement_noise = sensor_components["measurement_noise"]
    source_measurement_bonus = sum(
        effect["modifier"] for effect in source_data["source_effects"]
        if effect["target_component"] == "measurement_noise"
    )
    adjusted_measurement_noise = max(0.0, measurement_noise + source_measurement_bonus)

    source_environment_bonus = sum(
        effect["modifier"] for effect in source_data["source_effects"]
        if effect["target_component"] == "environment_noise"
    )
    adjusted_environment_noise = max(0.0, environment_noise + source_environment_bonus)

    gate_noise = sensor_components["gate_noise"]
    device_noise = sensor_components["device_noise"]
    combined_sensor_noise = gate_noise + adjusted_measurement_noise + device_noise

    base_noise = 0.5 * combined_sensor_noise + 0.5 * adjusted_environment_noise
    source_effective_modifier = sum(
        effect["modifier"] for effect in source_data["source_effects"]
        if effect["target_component"] == "effective_noise"
    )
    effective_noise = min(1.0, max(0.0, (base_noise + circuit_noise + spatial_noise + source_effective_modifier) * 0.85))

    return {
        "gate_noise": round(gate_noise, 3),
        "measurement_noise": round(adjusted_measurement_noise, 3),
        "device_noise": round(device_noise, 3),
        "sensor_noise": round(combined_sensor_noise, 3),
        "environment_noise": round(adjusted_environment_noise, 3),
        "circuit_noise": round(circuit_noise, 3),
        "spatial_noise": round(spatial_noise, 3),
        "source_noise_modifier": round(source_effective_modifier, 3),
        "base_noise": round(base_noise, 3),
        "effective_noise": round(effective_noise, 3),
        "status": get_status(effective_noise),
        "inside_source_count": source_data["inside_source_count"],
        "source_effects": source_data["source_effects"],
        **circuit_stats,
    }
