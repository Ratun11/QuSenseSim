from dataclasses import dataclass


@dataclass
class Environment:
    global_noise: float = 0.15
    field_strength: float = 0.60
    phase_shift: float = 0.50
    circuit_noise_enabled: bool = True
    environment_noise_enabled: bool = True
    spatial_noise_enabled: bool = True
    source_effects_enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "Environment":
        return cls(
            global_noise=float(data.get("global_noise", 0.15)),
            field_strength=float(data.get("field_strength", 0.60)),
            phase_shift=float(data.get("phase_shift", 0.50)),
            circuit_noise_enabled=bool(data.get("circuit_noise_enabled", True)),
            environment_noise_enabled=bool(data.get("environment_noise_enabled", True)),
            spatial_noise_enabled=bool(data.get("spatial_noise_enabled", True)),
            source_effects_enabled=bool(data.get("source_effects_enabled", True)),
        )

    def to_dict(self) -> dict:
        return {
            "global_noise": round(self.global_noise, 3),
            "field_strength": round(self.field_strength, 3),
            "phase_shift": round(self.phase_shift, 3),
            "circuit_noise_enabled": self.circuit_noise_enabled,
            "environment_noise_enabled": self.environment_noise_enabled,
            "spatial_noise_enabled": self.spatial_noise_enabled,
            "source_effects_enabled": self.source_effects_enabled,
        }
