from typing import Dict, List

from backend.models.environment import Environment
from backend.models.sensor import Sensor
from backend.models.source import Source
from backend.noise.noise_engine import compute_noise_breakdown
from backend.simulation.metrics import compute_metrics
from backend.environment.sources import build_default_sources


def run_simulation(payload: Dict) -> Dict:
    environment = Environment.from_dict(payload.get("environment", {}))
    sensors = [Sensor.from_dict(item) for item in payload.get("sensors", [])]
    sources = [Source.from_dict(item).to_dict() for item in payload.get("sources", build_default_sources())]
    circuits_by_id = payload.get("circuits_by_id", {})

    computed: List[dict] = []
    for sensor in sensors:
        circuit = circuits_by_id.get(sensor.assigned_circuit_id) if sensor.assigned_circuit_id else None
        noise_data = compute_noise_breakdown(sensor, environment, circuit, sources)
        metrics = compute_metrics(environment, noise_data)

        sensor.status = noise_data["status"]
        sensor.estimate = metrics["estimate"]
        sensor.fisher_info = metrics["fisher_info"]
        sensor.crb = metrics["crb"]

        data = sensor.to_dict()
        data.update(noise_data)
        data.update({
            "noise_rate_gamma": metrics["noise_rate_gamma"],
            "sensing_time": metrics["sensing_time"],
        })
        computed.append(data)

    if computed:
        avg_estimate = round(sum(item["estimate"] for item in computed) / len(computed), 3)
        avg_fisher_info = round(sum(item["fisher_info"] for item in computed) / len(computed), 3)
        avg_crb = round(sum(item["crb"] for item in computed) / len(computed), 3)
        avg_effective_noise = round(sum(item["effective_noise"] for item in computed) / len(computed), 3)
        degraded_count = sum(1 for item in computed if item["status"] == "degraded")
        stable_count = sum(1 for item in computed if item["status"] == "stable")
    else:
        avg_estimate = avg_fisher_info = avg_crb = avg_effective_noise = 0.0
        degraded_count = stable_count = 0

    selected_sensor_id = payload.get("selected_sensor_id")
    selected_sensor = next((item for item in computed if item["id"] == selected_sensor_id), computed[0] if computed else None)

    return {
        "environment": environment.to_dict(),
        "sources": sources,
        "sensors": computed,
        "selected_sensor": selected_sensor,
        "global_results": {
            "avg_estimate": avg_estimate,
            "avg_fisher_info": avg_fisher_info,
            "avg_crb": avg_crb,
            "avg_effective_noise": avg_effective_noise,
            "degraded_count": degraded_count,
            "stable_count": stable_count,
        },
    }


def build_default_state(sensor_count: int = 4) -> Dict:
    sensor_count = max(1, min(8, int(sensor_count)))
    positions = [
        (290, 250), (610, 265), (345, 465), (675, 485),
        (860, 320), (845, 610), (515, 650), (225, 600),
    ]
    default_circuit_ids = [
        "fixed_ramsey",
        "fixed_phase_estimation",
        "fixed_basic_single_qubit",
        None,
        None,
        None,
        None,
        None,
    ]
    default_names = {
        "fixed_ramsey": "Ramsey Sensing Circuit",
        "fixed_phase_estimation": "Phase Estimation Circuit",
        "fixed_basic_single_qubit": "Basic Single-Qubit Sensing",
        None: "Unassigned",
    }

    sensors = []
    for i in range(sensor_count):
        x, y = positions[i]
        circuit_id = default_circuit_ids[i]
        gate_noise = round(0.01 + i * 0.005, 3)
        measurement_noise = round(0.02 + i * 0.004, 3)
        device_noise = round(0.03 + i * 0.006, 3)
        sensors.append(
            {
                "id": i + 1,
                "name": f"Sensor {i + 1}",
                "x": x,
                "y": y,
                "noise": round(gate_noise + measurement_noise + device_noise, 3),
                "gate_noise": gate_noise,
                "measurement_noise": measurement_noise,
                "device_noise": device_noise,
                "assigned_circuit_id": circuit_id,
                "assigned_circuit_name": default_names[circuit_id],
                "circuit_mode": "fixed" if circuit_id else "fixed",
                "estimate": 0.0,
                "fisher_info": 0.0,
                "crb": 0.0,
                "status": "stable",
            }
        )

    return {
        "environment": {
            "global_noise": 0.15,
            "field_strength": 0.60,
            "phase_shift": 0.50,
            "circuit_noise_enabled": True,
            "environment_noise_enabled": True,
            "spatial_noise_enabled": True,
            "source_effects_enabled": True,
        },
        "sources": build_default_sources(),
        "selected_sensor_id": 1,
        "sensors": sensors,
    }
