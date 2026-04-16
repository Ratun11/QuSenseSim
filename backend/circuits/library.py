from backend.models.circuit import Circuit

FIXED_CIRCUITS = [
    Circuit(
        id="fixed_ramsey",
        name="Ramsey Sensing Circuit",
        mode="fixed",
        number_of_qubits=1,
        gate_sequence=[
            {"type": "H", "target_qubit": 0},
            {"type": "RZ", "target_qubit": 0, "parameter": 0.50},
            {"type": "H", "target_qubit": 0},
            {"type": "M", "target_qubit": 0},
        ],
        description="Classic phase-sensitive single-qubit sensing sequence.",
    ).to_dict(),
    Circuit(
        id="fixed_phase_estimation",
        name="Phase Estimation Circuit",
        mode="fixed",
        number_of_qubits=2,
        gate_sequence=[
            {"type": "H", "target_qubit": 0},
            {"type": "CX", "target_qubit": 1, "control_qubit": 0},
            {"type": "RZ", "target_qubit": 1, "parameter": 0.70},
            {"type": "M", "target_qubit": 0},
            {"type": "M", "target_qubit": 1},
        ],
        description="Two-qubit circuit with controlled interaction for phase probing.",
    ).to_dict(),
    Circuit(
        id="fixed_basic_single_qubit",
        name="Basic Single-Qubit Sensing",
        mode="fixed",
        number_of_qubits=1,
        gate_sequence=[
            {"type": "RY", "target_qubit": 0, "parameter": 0.35},
            {"type": "RZ", "target_qubit": 0, "parameter": 0.20},
            {"type": "M", "target_qubit": 0},
        ],
        description="Compact sensing circuit with simple rotation-based probing.",
    ).to_dict(),
]
