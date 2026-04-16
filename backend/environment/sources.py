from backend.models.source import Source


def build_default_sources() -> list[dict]:
    return [
        Source(id="src_cool_1", type="cooling", x=430, y=320, radius=120, strength=0.08).to_dict(),
        Source(id="src_heat_1", type="heating", x=760, y=500, radius=110, strength=0.07).to_dict(),
    ]
