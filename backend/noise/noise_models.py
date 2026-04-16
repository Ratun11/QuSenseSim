from math import sqrt

WORKSPACE_CENTER = (320.0, 260.0)


def compute_sensor_component_noise(sensor) -> dict:
    gate_noise = float(sensor.gate_noise)
    measurement_noise = float(sensor.measurement_noise)
    device_noise = float(sensor.device_noise)
    combined = gate_noise + measurement_noise + device_noise
    return {
        "gate_noise": gate_noise,
        "measurement_noise": measurement_noise,
        "device_noise": device_noise,
        "combined_sensor_noise": combined,
    }


def compute_environment_noise(environment) -> float:
    return float(environment.global_noise) if environment.environment_noise_enabled else 0.0


def compute_circuit_noise(circuit: dict | None, enabled: bool = True):
    if not circuit or not enabled:
        return 0.0, {
            "num_gates": 0,
            "num_cx": 0,
            "num_rotation_gates": 0,
            "qubits": 1,
            "rotation_factor": 0.15,
            "circuit_factor": 0.0,
            "gate_preview": [],
        }

    gates = circuit.get("gate_sequence", [])
    gate_types = [str(g.get("type", "")).upper() for g in gates]
    num_gates = len(gates)
    num_cx = sum(1 for g in gate_types if g == "CX")
    num_rotation_gates = sum(1 for g in gate_types if g in {"RX", "RY", "RZ"})
    qubits = int(circuit.get("number_of_qubits", 1))

    circuit_noise = 0.01 * num_gates + 0.03 * num_cx + 0.005 * num_rotation_gates
    rotation_factor = 0.15 + 0.03 * num_rotation_gates
    circuit_factor = 0.08 * num_rotation_gates + 0.05 * num_cx

    preview = []
    for gate in gates[:6]:
        gate_name = str(gate.get("type", ""))
        parameter = gate.get("parameter")
        preview.append(gate_name if parameter is None else f"{gate_name}({parameter})")

    return circuit_noise, {
        "num_gates": num_gates,
        "num_cx": num_cx,
        "num_rotation_gates": num_rotation_gates,
        "qubits": qubits,
        "rotation_factor": rotation_factor,
        "circuit_factor": circuit_factor,
        "gate_preview": preview,
    }


def compute_spatial_noise(sensor, enabled: bool = True) -> float:
    if not enabled:
        return 0.0

    dx = float(sensor.x) - WORKSPACE_CENTER[0]
    dy = float(sensor.y) - WORKSPACE_CENTER[1]
    distance = sqrt(dx * dx + dy * dy)
    return min(0.12, distance / 1800.0)
