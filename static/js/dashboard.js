const state = {
    environment: {
        global_noise: 0.15,
        field_strength: 0.60,
        phase_shift: 0.50,
        circuit_noise_enabled: true,
        environment_noise_enabled: true,
        spatial_noise_enabled: true,
        source_effects_enabled: true,
    },
    sensors: [],
    sources: [],
    deleted_source_ids: [],
    deleted_sensor_ids: [],
    next_sensor_id: 5,
    selected_sensor_id: 1,
    selected_source_id: null,
    fixedCircuits: [],
    customCircuits: [],
    collaboration_mode: "independent",
};

const el = {};

document.addEventListener("DOMContentLoaded", async () => {
    cacheElements();
    bindUI();
    await loadCircuits();
    const restored = await restoreSavedSetupState();
    if (!restored) {
        await resetDashboard(false);
    }
});

function cacheElements() {
    el.sensorCount = document.getElementById("sensorCount");
    el.addSensorBtn = document.getElementById("addSensorBtn");
    el.globalNoise = document.getElementById("globalNoise");
    el.fieldStrength = document.getElementById("fieldStrength");
    el.phaseShift = document.getElementById("phaseShift");
    el.workspaceZoom = document.getElementById("workspaceZoom");
    el.collaborationMode = document.getElementById("collaborationMode");

    el.selectedGateNoise = document.getElementById("selectedGateNoise");
    el.selectedMeasurementNoise = document.getElementById("selectedMeasurementNoise");
    el.selectedDeviceNoise = document.getElementById("selectedDeviceNoise");

    el.sensorCountValue = document.getElementById("sensorCountValue");
    el.globalNoiseValue = document.getElementById("globalNoiseValue");
    el.fieldStrengthValue = document.getElementById("fieldStrengthValue");
    el.phaseShiftValue = document.getElementById("phaseShiftValue");
    el.workspaceZoomValue = document.getElementById("workspaceZoomValue");
    el.selectedGateNoiseValue = document.getElementById("selectedGateNoiseValue");
    el.selectedMeasurementNoiseValue = document.getElementById("selectedMeasurementNoiseValue");
    el.selectedDeviceNoiseValue = document.getElementById("selectedDeviceNoiseValue");

    el.enableCircuitNoise = document.getElementById("enableCircuitNoise");
    el.enableEnvironmentNoise = document.getElementById("enableEnvironmentNoise");
    el.enableSpatialNoise = document.getElementById("enableSpatialNoise");
    el.enableSourceEffects = document.getElementById("enableSourceEffects");

    el.simulateBtn = document.getElementById("simulateBtn");
    el.resetBtn = document.getElementById("resetBtn");
    el.proceedToAnalysisBtn = document.getElementById("proceedToAnalysisBtn");
    el.removeCircuitBtn = document.getElementById("removeCircuitBtn");
    el.deleteSelectedSourceBtn = document.getElementById("deleteSelectedSourceBtn");
    el.deleteSelectedSensorBtn = document.getElementById("deleteSelectedSensorBtn");

    el.workspaceViewport = document.getElementById("workspaceViewport");
    el.workspaceScaleWrap = document.getElementById("workspaceScaleWrap");
    el.workspace = document.getElementById("workspace");
    el.environmentOverlay = document.getElementById("environmentOverlay");
    el.sensorLayer = document.getElementById("sensorLayer");
    el.sourceLayer = document.getElementById("sourceLayer");

    el.fixedCircuitList = document.getElementById("fixedCircuitList");
    el.customCircuitList = document.getElementById("customCircuitList");

    el.selectedName = document.getElementById("selectedName");
    el.selectedStatus = document.getElementById("selectedStatus");
    el.selectedCircuitName = document.getElementById("selectedCircuitName");
    el.selectedCircuitMode = document.getElementById("selectedCircuitMode");
    el.selectedEstimate = document.getElementById("selectedEstimate");
    el.selectedFI = document.getElementById("selectedFI");
    el.selectedCRB = document.getElementById("selectedCRB");
    el.selectedGamma = document.getElementById("selectedGamma");
    el.selectedTime = document.getElementById("selectedTime");

    el.gateNoise = document.getElementById("gateNoise");
    el.measurementNoise = document.getElementById("measurementNoise");
    el.deviceNoise = document.getElementById("deviceNoise");
    el.sensorNoise = document.getElementById("sensorNoise");
    el.environmentNoise = document.getElementById("environmentNoise");
    el.circuitNoise = document.getElementById("circuitNoise");
    el.spatialNoise = document.getElementById("spatialNoise");
    el.sourceModifier = document.getElementById("sourceModifier");
    el.baseNoise = document.getElementById("baseNoise");
    el.effectiveNoise = document.getElementById("effectiveNoise");
    el.sourceEffectsPanel = document.getElementById("sourceEffectsPanel");

    el.circuitPreview = document.getElementById("circuitPreview");

    el.avgEstimate = document.getElementById("avgEstimate");
    el.avgFI = document.getElementById("avgFI");
    el.avgCRB = document.getElementById("avgCRB");
    el.avgEffectiveNoise = document.getElementById("avgEffectiveNoise");
    el.stableCount = document.getElementById("stableCount");
    el.degradedCount = document.getElementById("degradedCount");

    el.effectiveNoiseBar = document.getElementById("effectiveNoiseBar");
    el.avgNoiseBar = document.getElementById("avgNoiseBar");
    el.effectiveNoiseBarLabel = document.getElementById("effectiveNoiseBarLabel");
    el.avgNoiseBarLabel = document.getElementById("avgNoiseBarLabel");

    el.sourceAddButtons = document.querySelectorAll(".source-add-btn");
}

function bindUI() {
    const globalPairs = [
        [el.globalNoise, el.globalNoiseValue],
        [el.fieldStrength, el.fieldStrengthValue],
        [el.phaseShift, el.phaseShiftValue],
    ];

    globalPairs.forEach(([slider, label]) => {
        slider.addEventListener("input", async () => {
            label.textContent = slider.step === "1" ? slider.value : Number(slider.value).toFixed(2);
            syncEnvironmentFromControls();
            await simulate();
        });
    });

    el.workspaceZoom.addEventListener("input", () => {
        const zoom = Number(el.workspaceZoom.value);
        el.workspaceZoomValue.textContent = `${zoom}%`;
        el.workspaceScaleWrap.style.transform = `scale(${zoom / 100})`;
        setTimeout(centerWorkspaceView, 30);
    });

    [
        [el.selectedGateNoise, el.selectedGateNoiseValue],
        [el.selectedMeasurementNoise, el.selectedMeasurementNoiseValue],
        [el.selectedDeviceNoise, el.selectedDeviceNoiseValue],
    ].forEach(([slider, label]) => {
        slider.addEventListener("input", async () => {
            label.textContent = Number(slider.value).toFixed(2);
            await updateSelectedSensorNoise();
        });
    });

    if (el.collaborationMode) {
        el.collaborationMode.addEventListener("change", () => {
            state.collaboration_mode = el.collaborationMode.value;
        });
    }

    [el.enableCircuitNoise, el.enableEnvironmentNoise, el.enableSpatialNoise, el.enableSourceEffects].forEach((checkbox) => {
        checkbox.addEventListener("change", async () => {
            syncEnvironmentFromControls();
            await simulate();
        });
    });

    el.sourceAddButtons.forEach((btn) => {
        btn.addEventListener("click", async () => {
            await addSource(btn.dataset.type);
        });
    });

    el.simulateBtn.addEventListener("click", simulate);
    el.resetBtn.addEventListener("click", () => resetDashboard(true));

    if (el.addSensorBtn) {
        el.addSensorBtn.addEventListener("click", async () => {
            await addSensor();
        });
    }

    if (el.removeCircuitBtn) {
        el.removeCircuitBtn.addEventListener("click", async () => {
            await removeCircuitFromSelectedSensor();
        });
    }

    if (el.deleteSelectedSourceBtn) {
        el.deleteSelectedSourceBtn.addEventListener("click", async () => {
            await deleteSelectedSource();
        });
    }

    if (el.deleteSelectedSensorBtn) {
        el.deleteSelectedSensorBtn.addEventListener("click", async () => {
            await deleteSelectedSensor();
        });
    }

    if (el.proceedToAnalysisBtn) {
        el.proceedToAnalysisBtn.addEventListener("click", async () => {
            await saveSetupState();
            window.location.href = "/analysis";
        });
    }
}

async function loadCircuits() {
    const [fixedResponse, customResponse] = await Promise.all([
        fetch("/api/circuits/fixed"),
        fetch("/api/circuits/custom"),
    ]);

    state.fixedCircuits = await fixedResponse.json();
    state.customCircuits = await customResponse.json();
    renderCircuitLists();
}


function updateControlsFromState() {
    el.globalNoise.value = Number(state.environment.global_noise ?? 0.15);
    el.fieldStrength.value = Number(state.environment.field_strength ?? 0.60);
    el.phaseShift.value = Number(state.environment.phase_shift ?? 0.50);
    el.globalNoiseValue.textContent = Number(el.globalNoise.value).toFixed(2);
    el.fieldStrengthValue.textContent = Number(el.fieldStrength.value).toFixed(2);
    el.phaseShiftValue.textContent = Number(el.phaseShift.value).toFixed(2);

    el.enableCircuitNoise.checked = state.environment.circuit_noise_enabled ?? true;
    el.enableEnvironmentNoise.checked = state.environment.environment_noise_enabled ?? true;
    el.enableSpatialNoise.checked = state.environment.spatial_noise_enabled ?? true;
    el.enableSourceEffects.checked = state.environment.source_effects_enabled ?? true;
    if (el.collaborationMode) el.collaborationMode.value = state.collaboration_mode || "independent";
}

function buildSetupStatePayload() {
    return {
        environment: state.environment,
        sensors: state.sensors,
        sources: state.sources,
        selected_sensor_id: state.selected_sensor_id,
        selected_source_id: state.selected_source_id,
        deleted_source_ids: state.deleted_source_ids,
        deleted_sensor_ids: state.deleted_sensor_ids,
        next_sensor_id: state.next_sensor_id,
        collaboration_mode: state.collaboration_mode,
    };
}

async function saveSetupState() {
    await fetch("/api/save_state", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ setup_state: buildSetupStatePayload() }),
    });
}

async function restoreSavedSetupState() {
    const response = await fetch("/api/load_state");
    const payload = await response.json();
    const saved = payload.setup_state;

    if (!saved || !saved.sensors || !saved.environment) {
        return false;
    }

    state.environment = { ...state.environment, ...saved.environment };
    state.sensors = saved.sensors || [];
    state.sources = saved.sources || [];
    state.deleted_source_ids = saved.deleted_source_ids || [];
    state.deleted_sensor_ids = saved.deleted_sensor_ids || [];
    state.selected_sensor_id = saved.selected_sensor_id ?? state.sensors[0]?.id ?? null;
    state.selected_source_id = saved.selected_source_id ?? null;
    state.next_sensor_id = saved.next_sensor_id || ((state.sensors.length ? Math.max(...state.sensors.map(sensor => sensor.id)) : 0) + 1);
    state.collaboration_mode = saved.collaboration_mode || "independent";

    updateControlsFromState();
    await simulate();
    setTimeout(centerWorkspaceView, 80);
    return true;
}

function centerWorkspaceView() {
    const viewport = el.workspaceViewport;
    const workspace = el.workspaceScaleWrap;
    if (!viewport || !workspace) return;

    const zoom = Number(el.workspaceZoom?.value || 90) / 100;
    const scaledWidth = workspace.offsetWidth * zoom;
    const scaledHeight = workspace.offsetHeight * zoom;

    const left = Math.max(0, (scaledWidth - viewport.clientWidth) / 2);
    const top = Math.max(0, (scaledHeight - viewport.clientHeight) / 2);

    viewport.scrollLeft = left;
    viewport.scrollTop = top;
}

function renderCircuitLists() {
    renderCircuitGroup(state.fixedCircuits, el.fixedCircuitList);
    renderCircuitGroup(state.customCircuits, el.customCircuitList, true);
}

function renderCircuitGroup(circuits, container, isCustom = false) {
    container.innerHTML = "";
    if (!circuits.length) {
        container.innerHTML = `<div class="circuit-item"><p>${isCustom ? "No custom circuits saved yet." : "No circuits available."}</p></div>`;
        return;
    }

    circuits.forEach((circuit) => {
        const item = document.createElement("div");
        item.className = "circuit-item";
        const preview = (circuit.gate_sequence || []).slice(0, 5).map(g => g.parameter == null ? g.type : `${g.type}(${g.parameter})`).join(" → ");
        item.innerHTML = `
            <h4>${circuit.name}</h4>
            <div class="circuit-meta">
                <span class="mini-pill">${circuit.mode}</span>
                <span class="mini-pill">${circuit.number_of_qubits} qubit${circuit.number_of_qubits > 1 ? "s" : ""}</span>
                <span class="mini-pill">${(circuit.gate_sequence || []).length} gates</span>
            </div>
            <p>${circuit.description || "Custom sensing circuit."}</p>
            <p><strong>Preview:</strong> ${preview || "No gates"}</p>
            <button class="btn btn-primary assign-btn" type="button">Use this circuit</button>
        `;
        item.querySelector(".assign-btn").addEventListener("click", async () => {
            await assignCircuitToSelectedSensor(circuit.id);
        });
        container.appendChild(item);
    });
}

function syncEnvironmentFromControls() {
    state.environment.global_noise = parseFloat(el.globalNoise.value);
    state.environment.field_strength = parseFloat(el.fieldStrength.value);
    state.environment.phase_shift = parseFloat(el.phaseShift.value);
    state.environment.circuit_noise_enabled = el.enableCircuitNoise.checked;
    state.environment.environment_noise_enabled = el.enableEnvironmentNoise.checked;
    state.environment.spatial_noise_enabled = el.enableSpatialNoise.checked;
    state.environment.source_effects_enabled = el.enableSourceEffects.checked;
}

async function simulate() {
    syncEnvironmentFromControls();

    const payload = {
        environment: state.environment,
        selected_sensor_id: state.selected_sensor_id,
        sensors: state.sensors.filter(sensor => !state.deleted_sensor_ids.includes(sensor.id)),
        sources: state.sources.filter(source => !state.deleted_source_ids.includes(source.id)),
        circuits_by_id: buildCircuitsById(),
    };

    const response = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const result = await response.json();
    applySimulationResult(result);
}

function applySimulationResult(result) {
    state.environment = result.environment;
    state.sensors = (result.sensors || state.sensors).filter(sensor => !state.deleted_sensor_ids.includes(sensor.id));
    state.sources = (result.sources || state.sources).filter(source => !state.deleted_source_ids.includes(source.id));
    const maxId = state.sensors.length ? Math.max(...state.sensors.map(sensor => sensor.id)) : 0;
    state.next_sensor_id = Math.max(state.next_sensor_id || 1, maxId + 1);
    if (result.selected_sensor && !state.deleted_sensor_ids.includes(result.selected_sensor.id)) {
        state.selected_sensor_id = result.selected_sensor.id;
    } else {
        state.selected_sensor_id = state.sensors[0]?.id || null;
    }

    renderSources();
    renderSensors();
    updateSensorCount();
    updateSelectedPanel(result.selected_sensor);
    updateGlobalPanel(result.global_results);
    updateWorkspaceEnvironmentVisual();
}

function renderSources() {
    el.sourceLayer.innerHTML = "";

    state.sources.forEach((source) => {
        const ring = document.createElement("div");
        ring.className = `source-ring ${source.type}`;
        ring.style.width = `${source.radius * 2}px`;
        ring.style.height = `${source.radius * 2}px`;
        ring.style.left = `${source.x - source.radius}px`;
        ring.style.top = `${source.y - source.radius}px`;

        const node = document.createElement("div");
        node.className = `source-node ${source.type} ${state.selected_source_id === source.id ? "selected" : ""}`;
        node.style.left = `${source.x - 14}px`;
        node.style.top = `${source.y - 14}px`;
        node.title = `${capitalize(source.type)} • radius ${source.radius} • strength ${source.strength}`;
        node.addEventListener("click", (event) => {
            event.stopPropagation();
            state.selected_source_id = source.id;
            renderSources();
        });

        const label = document.createElement("div");
        label.className = `source-label ${source.type}`;
        label.style.left = `${source.x + 20}px`;
        label.style.top = `${source.y - 10}px`;
        label.textContent = `${capitalize(source.type)} • r=${Math.round(source.radius)}`;

        window.DragDropManager.makeSensorDraggable(
            node,
            el.workspace,
            (left, top) => {
                source.x = left + 14;
                source.y = top + 14;
                ring.style.left = `${source.x - source.radius}px`;
                ring.style.top = `${source.y - source.radius}px`;
                label.style.left = `${source.x + 20}px`;
                label.style.top = `${source.y - 10}px`;
            },
            null,
            async () => {
                await fetch("/api/source/update-position", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ source, x: source.x, y: source.y }),
                });
                await simulate();
            }
        );

        el.sourceLayer.appendChild(ring);
        el.sourceLayer.appendChild(node);
        el.sourceLayer.appendChild(label);
    });
}

function renderSensors() {
    el.sensorLayer.innerHTML = "";

    state.sensors.forEach((sensor) => {
        const card = document.createElement("div");
        card.className = `sensor-card ${sensor.status} ${sensor.id === state.selected_sensor_id ? "selected" : ""}`;
        card.style.left = `${sensor.x}px`;
        card.style.top = `${sensor.y}px`;

        const fillWidth = Math.max(4, Math.min(100, sensor.effective_noise * 100));

        card.innerHTML = `
            <div class="sensor-top">
                <div class="sensor-name">${sensor.name}</div>
                <span class="status-badge ${sensor.status}">${sensor.status}</span>
            </div>
            <div class="sensor-metric">Sensor: ${Number(sensor.sensor_noise).toFixed(3)}</div>
            <div class="sensor-metric">Eff: ${Number(sensor.effective_noise).toFixed(3)}</div>
            <div class="sensor-noise-bar"><div class="sensor-noise-fill" style="width:${fillWidth}%"></div></div>
        `;

        card.addEventListener("click", async () => {
            state.selected_sensor_id = sensor.id;
            state.selected_source_id = null;
            syncSelectedSensorControls(sensor);
            await simulate();
        });

        window.DragDropManager.makeSensorDraggable(
            card,
            el.workspace,
            (left, top) => {
                const target = state.sensors.find(item => item.id === sensor.id);
                if (target) {
                    target.x = left;
                    target.y = top;
                }
            },
            () => {
                state.selected_sensor_id = sensor.id;
                renderSensors();
            },
            async () => {
                const target = state.sensors.find(item => item.id === sensor.id);
                if (!target) return;
                await fetch("/api/sensor/update-position", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sensor: target, x: target.x, y: target.y }),
                });
                await simulate();
            }
        );

        el.sensorLayer.appendChild(card);
    });
}

function updateSelectedPanel(sensor) {
    if (!sensor) return;

    el.selectedName.textContent = sensor.name;
    el.selectedStatus.textContent = capitalize(sensor.status);
    el.selectedStatus.className = `status-text ${sensor.status}`;
    el.selectedCircuitName.textContent = sensor.assigned_circuit_name || "Unassigned";
    el.selectedCircuitMode.textContent = capitalize(sensor.circuit_mode || "fixed");
    el.selectedEstimate.textContent = Number(sensor.estimate).toFixed(3);
    el.selectedFI.textContent = Number(sensor.fisher_info).toFixed(3);
    el.selectedCRB.textContent = Number(sensor.crb).toFixed(3);
    el.selectedGamma.textContent = Number(sensor.noise_rate_gamma || sensor.effective_noise).toFixed(3);
    el.selectedTime.textContent = Number(sensor.sensing_time || 1.0).toFixed(1);

    el.gateNoise.textContent = Number(sensor.gate_noise).toFixed(3);
    el.measurementNoise.textContent = Number(sensor.measurement_noise).toFixed(3);
    el.deviceNoise.textContent = Number(sensor.device_noise).toFixed(3);
    el.sensorNoise.textContent = Number(sensor.sensor_noise).toFixed(3);
    el.environmentNoise.textContent = Number(sensor.environment_noise).toFixed(3);
    el.circuitNoise.textContent = Number(sensor.circuit_noise).toFixed(3);
    el.spatialNoise.textContent = Number(sensor.spatial_noise).toFixed(3);
    el.sourceModifier.textContent = Number(sensor.source_noise_modifier).toFixed(3);
    el.baseNoise.textContent = Number(sensor.base_noise).toFixed(3);
    el.effectiveNoise.textContent = Number(sensor.effective_noise).toFixed(3);

    const preview = sensor.gate_preview || [];
    el.circuitPreview.innerHTML = preview.length
        ? preview.map(gate => `<span class="gate-chip">${gate}</span>`).join("")
        : "No gates assigned.";

    if (sensor.source_effects && sensor.source_effects.length) {
        el.sourceEffectsPanel.innerHTML = sensor.source_effects.map(effect => {
            const sign = effect.modifier >= 0 ? "+" : "";
            return `<span class="source-mini-badge">${capitalize(effect.source_type)} ${sign}${effect.modifier}</span>`;
        }).join("");
    } else {
        el.sourceEffectsPanel.textContent = "No active source effects.";
    }

    syncSelectedSensorControls(sensor);
    setProgressBar(el.effectiveNoiseBar, el.effectiveNoiseBarLabel, sensor.effective_noise);
}

function syncSelectedSensorControls(sensor) {
    el.selectedGateNoise.value = Number(sensor.gate_noise).toFixed(2);
    el.selectedMeasurementNoise.value = Number(sensor.measurement_noise).toFixed(2);
    el.selectedDeviceNoise.value = Number(sensor.device_noise).toFixed(2);

    el.selectedGateNoiseValue.textContent = Number(sensor.gate_noise).toFixed(2);
    el.selectedMeasurementNoiseValue.textContent = Number(sensor.measurement_noise).toFixed(2);
    el.selectedDeviceNoiseValue.textContent = Number(sensor.device_noise).toFixed(2);
}

function updateGlobalPanel(globalResults) {
    el.avgEstimate.textContent = Number(globalResults.avg_estimate).toFixed(3);
    el.avgFI.textContent = Number(globalResults.avg_fisher_info).toFixed(3);
    el.avgCRB.textContent = Number(globalResults.avg_crb).toFixed(3);
    el.avgEffectiveNoise.textContent = Number(globalResults.avg_effective_noise).toFixed(3);
    el.stableCount.textContent = globalResults.stable_count;
    el.degradedCount.textContent = globalResults.degraded_count;
    setProgressBar(el.avgNoiseBar, el.avgNoiseBarLabel, globalResults.avg_effective_noise);
}

function setProgressBar(bar, label, value) {
    const pct = Math.max(0, Math.min(100, Number(value) * 100));
    bar.style.width = `${pct}%`;
    label.textContent = Number(value).toFixed(3);
}

function updateWorkspaceEnvironmentVisual() {
    const opacity = Math.max(0.12, Math.min(0.72, state.environment.global_noise + 0.12));
    el.environmentOverlay.style.opacity = opacity;
}

async function assignCircuitToSelectedSensor(circuitId) {
    const selectedSensor = state.sensors.find(sensor => sensor.id === state.selected_sensor_id);
    if (!selectedSensor) return;

    const response = await fetch("/api/circuits/assign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ circuit_id: circuitId, sensor: selectedSensor }),
    });

    const result = await response.json();
    if (result.sensor) {
        const index = state.sensors.findIndex(sensor => sensor.id === result.sensor.id);
        if (index >= 0) {
            state.sensors[index] = {
                ...state.sensors[index],
                assigned_circuit_id: result.sensor.assigned_circuit_id,
                assigned_circuit_name: result.sensor.assigned_circuit_name,
                circuit_mode: result.sensor.circuit_mode,
            };
        }
        await simulate();
    }
}

async function updateSelectedSensorNoise() {
    const selectedSensor = state.sensors.find(sensor => sensor.id === state.selected_sensor_id);
    if (!selectedSensor) return;

    const response = await fetch("/api/noise/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sensor: selectedSensor,
            gate_noise: parseFloat(el.selectedGateNoise.value),
            measurement_noise: parseFloat(el.selectedMeasurementNoise.value),
            device_noise: parseFloat(el.selectedDeviceNoise.value),
        }),
    });

    const result = await response.json();
    if (result.sensor) {
        const index = state.sensors.findIndex(sensor => sensor.id === result.sensor.id);
        if (index >= 0) {
            state.sensors[index] = {
                ...state.sensors[index],
                gate_noise: result.sensor.gate_noise,
                measurement_noise: result.sensor.measurement_noise,
                device_noise: result.sensor.device_noise,
                noise: result.sensor.noise,
            };
        }
        await simulate();
    }
}

async function addSource(type) {
    const defaults = {
        cooling: { x: 430, y: 320, radius: 120, strength: 0.08 },
        heating: { x: 760, y: 500, radius: 110, strength: 0.07 },
        shielding: { x: 360, y: 560, radius: 130, strength: 0.06 },
        interference: { x: 860, y: 320, radius: 120, strength: 0.06 },
    };
    const preset = defaults[type] || defaults.cooling;

    const response = await fetch("/api/source/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, ...preset }),
    });
    const result = await response.json();
    if (result.source) {
        state.sources.push(result.source);
        await simulate();
        setTimeout(centerWorkspaceView, 30);
    }
}

async function resetDashboard(fullReset = true) {
    if (fullReset) {
        if (el.sensorCount) el.sensorCount.value = 4;
        el.globalNoise.value = 0.15;
        el.fieldStrength.value = 0.60;
        el.phaseShift.value = 0.50;
        el.workspaceZoom.value = 90;
        el.workspaceZoomValue.textContent = "90%";
        el.workspaceScaleWrap.style.transform = "scale(0.9)";
        el.enableCircuitNoise.checked = true;
        el.enableEnvironmentNoise.checked = true;
        el.enableSpatialNoise.checked = true;
        el.enableSourceEffects.checked = true;
    }

    const response = await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sensor_count: 4 }),
    });

    const result = await response.json();

    updateSensorCount();
    el.globalNoiseValue.textContent = Number(el.globalNoise.value).toFixed(2);
    el.fieldStrengthValue.textContent = Number(el.fieldStrength.value).toFixed(2);
    el.phaseShiftValue.textContent = Number(el.phaseShift.value).toFixed(2);

    state.environment = result.environment;
    state.sensors = result.sensors;
    state.sources = (result.sources || []).filter(source => !state.deleted_source_ids.includes(source.id));
    state.selected_sensor_id = result.selected_sensor?.id || 1;
    state.selected_source_id = null;
    state.deleted_source_ids = [];
    state.deleted_sensor_ids = [];

    if (fullReset) {
        syncEnvironmentFromControls();
        await simulate();
        setTimeout(centerWorkspaceView, 60);
    } else {
        applySimulationResult(result);
        el.workspaceScaleWrap.style.transform = "scale(0.9)";
        setTimeout(centerWorkspaceView, 60);
    }
}

function buildCircuitsById() {
    const all = [...state.fixedCircuits, ...state.customCircuits];
    return Object.fromEntries(all.map(circuit => [circuit.id, circuit]));
}

async function ensureSensorCount() {
    return;
}


function getNextSensorId() {
    const nextId = state.next_sensor_id || 1;
    state.next_sensor_id = nextId + 1;
    return nextId;
}

function getNextSensorName() {
    const nums = state.sensors
        .map(sensor => {
            const match = String(sensor.name || "").match(/Sensor\s+(\d+)/i);
            return match ? parseInt(match[1], 10) : null;
        })
        .filter(v => Number.isInteger(v));
    let nextNum = 1;
    while (nums.includes(nextNum)) nextNum += 1;
    return `Sensor ${nextNum}`;
}

function getNextSensorPosition() {
    const presets = [
        { x: 290, y: 250 }, { x: 610, y: 265 }, { x: 345, y: 465 }, { x: 675, y: 485 },
        { x: 860, y: 320 }, { x: 845, y: 610 }, { x: 515, y: 650 }, { x: 225, y: 600 },
    ];
    for (const pos of presets) {
        const occupied = state.sensors.some(sensor => Math.abs(sensor.x - pos.x) < 50 && Math.abs(sensor.y - pos.y) < 50);
        if (!occupied) return pos;
    }
    return { x: 200 + state.sensors.length * 35, y: 220 + state.sensors.length * 28 };
}

function createSensor() {
    const id = getNextSensorId();
    const name = getNextSensorName();
    const position = getNextSensorPosition();
    const gateNoise = Number((0.01 + (state.sensors.length % 8) * 0.005).toFixed(3));
    const measurementNoise = Number((0.02 + (state.sensors.length % 8) * 0.004).toFixed(3));
    const deviceNoise = Number((0.03 + (state.sensors.length % 8) * 0.006).toFixed(3));
    return {
        id,
        name,
        x: position.x,
        y: position.y,
        noise: Number((gateNoise + measurementNoise + deviceNoise).toFixed(3)),
        gate_noise: gateNoise,
        measurement_noise: measurementNoise,
        device_noise: deviceNoise,
        assigned_circuit_id: null,
        assigned_circuit_name: "Unassigned",
        circuit_mode: "fixed",
        estimate: 0,
        fisher_info: 0,
        crb: 0,
        status: "stable",
    };
}

function updateSensorCount() {
    if (el.sensorCountValue) {
        el.sensorCountValue.textContent = String(state.sensors.length);
    }
}

async function addSensor() {
    if (state.sensors.length >= 100) return;
    const sensor = createSensor();
    state.deleted_sensor_ids = state.deleted_sensor_ids.filter(id => id !== sensor.id);
    state.sensors.push(sensor);
    state.selected_sensor_id = sensor.id;
    state.selected_source_id = null;
    updateSensorCount();
    renderSensors();
    await simulate();
}

async function removeCircuitFromSelectedSensor() {
    const selectedSensor = state.sensors.find(sensor => sensor.id === state.selected_sensor_id);
    if (!selectedSensor) return;

    selectedSensor.assigned_circuit_id = null;
    selectedSensor.assigned_circuit_name = "Unassigned";
    selectedSensor.circuit_mode = "fixed";
    await simulate();
}

async function deleteSelectedSource() {
    if (!state.selected_source_id) return;

    const sourceId = state.selected_source_id;

    await fetch("/api/source/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_id: sourceId }),
    });

    if (!state.deleted_source_ids.includes(sourceId)) {
        state.deleted_source_ids.push(sourceId);
    }

    state.sources = state.sources.filter(source => source.id !== sourceId);
    state.selected_source_id = null;
    renderSources();
    await simulate();
}

async function deleteSelectedSensor() {
    if (!state.selected_sensor_id) return;

    const sensorId = state.selected_sensor_id;
    if (!state.deleted_sensor_ids.includes(sensorId)) {
        state.deleted_sensor_ids.push(sensorId);
    }

    state.sensors = state.sensors.filter(sensor => sensor.id !== sensorId);
    state.selected_sensor_id = state.sensors[0]?.id || null;
    state.selected_source_id = null;
    updateSensorCount();
    renderSensors();
    await simulate();
}

function capitalize(value) {
    return value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
}
