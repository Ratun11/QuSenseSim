from math import sqrt


def compute_source_effects(sensor, sources, enabled: bool = True):
    if not enabled:
        return {
            "source_noise_modifier": 0.0,
            "source_effects": [],
            "inside_source_count": 0,
        }

    effects = []
    total_modifier = 0.0
    inside_count = 0

    for source in sources:
        dx = float(sensor.x) - float(source["x"])
        dy = float(sensor.y) - float(source["y"])
        distance = sqrt(dx * dx + dy * dy)
        radius = float(source["radius"])
        strength = float(source["strength"])

        if distance > radius:
            continue

        inside_count += 1
        influence = max(0.0, 1.0 - distance / radius)

        source_type = str(source["type"]).lower()
        signed_effect = 0.0
        target_component = "effective_noise"

        if source_type == "cooling":
            signed_effect = -strength * influence
            target_component = "effective_noise"
        elif source_type == "heating":
            signed_effect = strength * influence
            target_component = "effective_noise"
        elif source_type == "shielding":
            signed_effect = -strength * influence
            target_component = "environment_noise"
        elif source_type == "interference":
            signed_effect = strength * influence
            target_component = "measurement_noise"
        else:
            signed_effect = 0.0

        total_modifier += signed_effect
        effects.append({
            "source_id": source["id"],
            "source_type": source_type,
            "distance": round(distance, 3),
            "influence": round(influence, 3),
            "modifier": round(signed_effect, 3),
            "target_component": target_component,
        })

    return {
        "source_noise_modifier": round(total_modifier, 3),
        "source_effects": effects,
        "inside_source_count": inside_count,
    }
