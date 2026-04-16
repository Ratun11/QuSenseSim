import json
import re
from pathlib import Path
from typing import List

from backend.models.circuit import Circuit

BASE_DIR = Path(__file__).resolve().parents[2]
SAVE_DIR = BASE_DIR / "data" / "saved_circuits"
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "circuit"


def save_custom_circuit(circuit: Circuit) -> dict:
    filename = f"{slugify(circuit.name)}_{slugify(circuit.id)}.json"
    path = SAVE_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(circuit.to_dict(), file, indent=2)
    return {"saved": True, "path": str(path.name)}


def load_custom_circuits() -> List[dict]:
    circuits: List[dict] = []
    for path in sorted(SAVE_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            circuits.append(Circuit.from_dict(data).to_dict())
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    return circuits
