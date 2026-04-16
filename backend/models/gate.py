from dataclasses import dataclass
from typing import Optional


@dataclass
class Gate:
    type: str
    target_qubit: int
    control_qubit: Optional[int] = None
    parameter: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Gate":
        return cls(
            type=str(data.get("type", "H")).upper(),
            target_qubit=int(data.get("target_qubit", 0)),
            control_qubit=data.get("control_qubit"),
            parameter=data.get("parameter"),
        )

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "target_qubit": self.target_qubit,
            "control_qubit": self.control_qubit,
            "parameter": self.parameter,
        }
