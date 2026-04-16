from dataclasses import dataclass, field
from typing import List
from backend.models.gate import Gate


@dataclass
class Circuit:
    id: str
    name: str
    mode: str
    number_of_qubits: int
    gate_sequence: List[Gate] = field(default_factory=list)
    description: str = ""

    def __post_init__(self):
        normalized = []
        for gate in self.gate_sequence:
            if isinstance(gate, Gate):
                normalized.append(gate)
            elif isinstance(gate, dict):
                normalized.append(Gate.from_dict(gate))
            else:
                raise TypeError(f"Unsupported gate type: {type(gate)}")
        self.gate_sequence = normalized

    @classmethod
    def from_dict(cls, data: dict) -> "Circuit":
        return cls(
            id=str(data.get("id", "unknown")),
            name=str(data.get("name", "Unnamed Circuit")),
            mode=str(data.get("mode", "custom")),
            number_of_qubits=int(data.get("number_of_qubits", 1)),
            gate_sequence=data.get("gate_sequence", []),
            description=str(data.get("description", "")),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode,
            "number_of_qubits": self.number_of_qubits,
            "gate_sequence": [g.to_dict() for g in self.gate_sequence],
            "description": self.description,
        }
