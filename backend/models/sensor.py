from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Sensor:
    id: int
    name: str
    x: float
    y: float
    noise: float = 0.0
    gate_noise: float = 0.02
    measurement_noise: float = 0.02
    device_noise: float = 0.02
    assigned_circuit_id: Optional[str] = None
    assigned_circuit_name: str = "Unassigned"
    circuit_mode: str = "fixed"
    estimate: float = 0.0
    fisher_info: float = 0.0
    crb: float = 0.0
    status: str = "stable"

    @classmethod
    def from_dict(cls, data: dict) -> "Sensor":
        gate_noise = float(data.get("gate_noise", data.get("noise", 0.02)))
        measurement_noise = float(data.get("measurement_noise", 0.02))
        device_noise = float(data.get("device_noise", 0.02))
        return cls(
            id=int(data.get("id", 1)),
            name=str(data.get("name", "Sensor 1")),
            x=float(data.get("x", 110)),
            y=float(data.get("y", 110)),
            noise=float(data.get("noise", gate_noise + measurement_noise + device_noise)),
            gate_noise=gate_noise,
            measurement_noise=measurement_noise,
            device_noise=device_noise,
            assigned_circuit_id=data.get("assigned_circuit_id"),
            assigned_circuit_name=str(data.get("assigned_circuit_name", "Unassigned")),
            circuit_mode=str(data.get("circuit_mode", "fixed")),
            estimate=float(data.get("estimate", 0.0)),
            fisher_info=float(data.get("fisher_info", 0.0)),
            crb=float(data.get("crb", 0.0)),
            status=str(data.get("status", "stable")),
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["noise"] = round(self.gate_noise + self.measurement_noise + self.device_noise, 3)
        return data
