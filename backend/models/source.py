from dataclasses import dataclass, asdict


@dataclass
class Source:
    id: str
    type: str
    x: float
    y: float
    radius: float
    strength: float

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        return cls(
            id=str(data.get("id", "src_1")),
            type=str(data.get("type", "cooling")),
            x=float(data.get("x", 240)),
            y=float(data.get("y", 180)),
            radius=float(data.get("radius", 120)),
            strength=float(data.get("strength", 0.08)),
        )

    def to_dict(self) -> dict:
        return asdict(self)
