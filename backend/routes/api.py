from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, request

from backend.analysis.export import json_export_string, table_to_csv_string
from backend.analysis.rankings import build_rankings
from backend.analysis.summary_tables import build_all_tables
from backend.circuits.library import FIXED_CIRCUITS
from backend.circuits.storage import load_custom_circuits, save_custom_circuit
from backend.collaboration.engine import run_collaboration_analysis
from backend.environment.sources import build_default_sources
from backend.mitigation.variants import list_variant_families, list_variants
from backend.models.circuit import Circuit
from backend.models.sensor import Sensor
from backend.simulation.engine import build_default_state, run_simulation

api_bp = Blueprint("api", __name__)

APP_STATE = {"setup_state": None, "analysis_results": None}

def _all_circuits_by_id() -> dict:
    fixed = {item["id"]: item for item in FIXED_CIRCUITS}
    custom = {item["id"]: item for item in load_custom_circuits()}
    return {**fixed, **custom}

def _refresh_setup_state(setup_state: dict) -> dict:
    simulate_payload = {
        "environment": setup_state.get("environment", {}),
        "sensors": setup_state.get("sensors", []),
        "sources": setup_state.get("sources", build_default_sources()),
        "selected_sensor_id": setup_state.get("selected_sensor_id"),
        "circuits_by_id": _all_circuits_by_id(),
    }
    simulated_state = run_simulation(simulate_payload)
    refreshed_setup = {
        **setup_state,
        "environment": simulated_state["environment"],
        "sensors": simulated_state["sensors"],
        "sources": simulated_state.get("sources", setup_state.get("sources", [])),
    }
    APP_STATE["setup_state"] = refreshed_setup
    return refreshed_setup

@api_bp.get("/api/circuits/fixed")
def get_fixed_circuits():
    return jsonify(FIXED_CIRCUITS)

@api_bp.get("/api/circuits/custom")
def get_custom_circuits():
    return jsonify(load_custom_circuits())

@api_bp.post("/api/circuits/save")
def save_circuit():
    payload = request.get_json(silent=True) or {}
    circuit_name = str(payload.get("name", "")).strip()
    if not circuit_name:
        return jsonify({"error": "Circuit name is required."}), 400
    payload["id"] = payload.get("id") or f"custom_{uuid.uuid4().hex[:8]}"
    payload["mode"] = "custom"
    payload["number_of_qubits"] = max(1, int(payload.get("number_of_qubits", 1)))
    payload["gate_sequence"] = payload.get("gate_sequence", [])
    circuit = Circuit.from_dict(payload)
    result = save_custom_circuit(circuit)
    return jsonify({"message": "Circuit saved successfully.", "circuit": circuit.to_dict(), **result})

@api_bp.post("/api/circuits/assign")
def assign_circuit():
    payload = request.get_json(silent=True) or {}
    circuit_id = payload.get("circuit_id")
    sensor = payload.get("sensor", {})
    circuit = _all_circuits_by_id().get(circuit_id)
    if not circuit:
        return jsonify({"error": "Circuit not found."}), 404
    sensor["assigned_circuit_id"] = circuit["id"]
    sensor["assigned_circuit_name"] = circuit["name"]
    sensor["circuit_mode"] = circuit["mode"]
    return jsonify({"message": "Circuit assigned successfully.", "sensor": sensor, "circuit": circuit})

@api_bp.post("/api/simulate")
def simulate():
    payload = request.get_json(silent=True) or {}
    payload["circuits_by_id"] = _all_circuits_by_id()
    if "sources" not in payload:
        payload["sources"] = build_default_sources()
    return jsonify(run_simulation(payload))

@api_bp.post("/api/reset")
def reset():
    payload = request.get_json(silent=True) or {}
    sensor_count = int(payload.get("sensor_count", 4))
    state = build_default_state(sensor_count=sensor_count)
    state["circuits_by_id"] = _all_circuits_by_id()
    return jsonify(run_simulation(state))

@api_bp.post("/api/sensor/update-position")
def update_sensor_position():
    payload = request.get_json(silent=True) or {}
    sensor = payload.get("sensor", {})
    sensor["x"] = float(payload.get("x", sensor.get("x", 0)))
    sensor["y"] = float(payload.get("y", sensor.get("y", 0)))
    return jsonify({"message": "Sensor position updated.", "sensor": sensor})

@api_bp.post("/api/noise/update")
def update_noise():
    payload = request.get_json(silent=True) or {}
    sensor = payload.get("sensor", {})
    sensor["gate_noise"] = float(payload.get("gate_noise", sensor.get("gate_noise", 0.02)))
    sensor["measurement_noise"] = float(payload.get("measurement_noise", sensor.get("measurement_noise", 0.02)))
    sensor["device_noise"] = float(payload.get("device_noise", sensor.get("device_noise", 0.02)))
    sensor["noise"] = round(sensor["gate_noise"] + sensor["measurement_noise"] + sensor["device_noise"], 3)
    return jsonify({"message": "Sensor component noises updated.", "sensor": sensor})

@api_bp.post("/api/source/update-position")
def update_source_position():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", {})
    source["x"] = float(payload.get("x", source.get("x", 0)))
    source["y"] = float(payload.get("y", source.get("y", 0)))
    return jsonify({"message": "Source position updated.", "source": source})

@api_bp.post("/api/source/create")
def create_source():
    payload = request.get_json(silent=True) or {}
    source = {
        "id": payload.get("id") or f"src_{uuid.uuid4().hex[:8]}",
        "type": str(payload.get("type", "cooling")),
        "x": float(payload.get("x", 240)),
        "y": float(payload.get("y", 180)),
        "radius": float(payload.get("radius", 120)),
        "strength": float(payload.get("strength", 0.08)),
    }
    return jsonify({"message": "Source created.", "source": source})

@api_bp.post("/api/source/delete")
def delete_source():
    payload = request.get_json(silent=True) or {}
    source_id = payload.get("source_id")
    if not source_id:
        return jsonify({"error": "source_id is required."}), 400
    return jsonify({"message": "Source deleted.", "source_id": source_id})

@api_bp.get("/api/sensor/<int:sensor_id>")
def get_sensor(sensor_id: int):
    state = build_default_state(sensor_count=max(sensor_id, 4))
    target = next((Sensor.from_dict(s).to_dict() for s in state["sensors"] if s["id"] == sensor_id), None)
    if target is None:
        return jsonify({"error": "Sensor not found."}), 404
    return jsonify(target)

@api_bp.post("/api/save_state")
def save_state():
    payload = request.get_json(silent=True) or {}
    APP_STATE["setup_state"] = payload.get("setup_state", payload)
    return jsonify({"status": "saved"})

@api_bp.get("/api/load_state")
def load_state():
    return jsonify(APP_STATE)

@api_bp.get("/api/get_analysis")
def get_analysis():
    return jsonify(APP_STATE.get("analysis_results") or {})

@api_bp.get("/api/mitigation/variants")
def get_mitigation_variants():
    return jsonify({"families": list_variant_families(), "all_variants": list_variants()})

@api_bp.post("/api/run_collaboration_analysis")
def run_collaboration_route():
    payload = request.get_json(silent=True) or {}
    selected_modes = payload.get("modes", [])
    time_config = payload.get("time_config", {})
    uniform_variants = payload.get("uniform_variants", [])
    personalized_assignments = payload.get("personalized_assignments", {})
    incoming_state = payload.get("state")
    setup_state = incoming_state or APP_STATE.get("setup_state")
    if not setup_state:
        return jsonify({"error": "No setup state available. Save setup from dashboard first."}), 400
    refreshed_setup = _refresh_setup_state(setup_state)
    analysis_results = run_collaboration_analysis(
        refreshed_setup,
        selected_modes=selected_modes,
        time_config=time_config,
        selected_uniform_variants=uniform_variants,
        personalized_assignments=personalized_assignments,
    )
    APP_STATE["analysis_results"] = analysis_results
    return jsonify(analysis_results)

@api_bp.get("/api/analysis/summary")
def get_analysis_summary():
    analysis = APP_STATE.get("analysis_results") or {}
    if not analysis:
        return jsonify({"error": "No analysis results available yet."}), 404
    setup = APP_STATE.get("setup_state") or {}
    return jsonify({
        "rankings": build_rankings(analysis),
        "time_config": analysis.get("time_config", {}),
        "selected_modes": analysis.get("selected_modes", []),
        "setup_overview": {
            "sensor_count": len(setup.get("sensors", [])),
            "source_count": len(setup.get("sources", [])),
            "field_strength": setup.get("environment", {}).get("field_strength"),
            "phase_shift": setup.get("environment", {}).get("phase_shift"),
            "global_noise": setup.get("environment", {}).get("global_noise"),
            "collaboration_mode": setup.get("collaboration_mode", "independent"),
        },
    })

@api_bp.get("/api/analysis/tables")
def get_analysis_tables():
    analysis = APP_STATE.get("analysis_results") or {}
    if not analysis:
        return jsonify({"error": "No analysis results available yet."}), 404
    selected_mode = request.args.get("mode", "all")
    selected_scope = request.args.get("scope", "all")
    return jsonify(build_all_tables(analysis, selected_mode=selected_mode, selected_scope=selected_scope))

@api_bp.get("/api/analysis/rankings")
def get_analysis_rankings():
    analysis = APP_STATE.get("analysis_results") or {}
    if not analysis:
        return jsonify({"error": "No analysis results available yet."}), 404
    return jsonify(build_rankings(analysis))

@api_bp.post("/api/export/table")
def export_table():
    analysis = APP_STATE.get("analysis_results") or {}
    if not analysis:
        return jsonify({"error": "No analysis results available yet."}), 404
    payload = request.get_json(silent=True) or {}
    table_name = payload.get("table", "global")
    mode = payload.get("mode", "all")
    scope = payload.get("scope", "all")
    rows = build_all_tables(analysis, selected_mode=mode, selected_scope=scope).get(table_name, [])
    return jsonify({"filename": f"{table_name}_summary.csv", "content": table_to_csv_string(rows)})

@api_bp.post("/api/export/figure")
def export_figure():
    payload = request.get_json(silent=True) or {}
    return jsonify({"figure": payload.get("figure", "figure"), "status": "ready"})

@api_bp.get("/api/export/report")
def export_report():
    analysis = APP_STATE.get("analysis_results") or {}
    if not analysis:
        return jsonify({"error": "No analysis results available yet."}), 404
    return jsonify({
        "filename": "analysis_report_snapshot.json",
        "content": json_export_string({
            "time_config": analysis.get("time_config", {}),
            "best_combo": analysis.get("best_combo", {}),
            "rankings": build_rankings(analysis),
            "tables": build_all_tables(analysis),
        }),
    })
