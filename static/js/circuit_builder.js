const builderState = {
    selectedGate: "H",
    gateSequence: [],
};

const builderEl = {};

document.addEventListener("DOMContentLoaded", async () => {
    cacheBuilderElements();
    bindBuilderUI();
    highlightSelectedGate();
    renderBuilderSequence();
    await loadSavedCircuits();
});

function cacheBuilderElements() {
    builderEl.gateButtons = document.querySelectorAll(".gate-btn");
    builderEl.circuitName = document.getElementById("circuitName");
    builderEl.numQubits = document.getElementById("numQubits");
    builderEl.targetQubit = document.getElementById("targetQubit");
    builderEl.controlQubit = document.getElementById("controlQubit");
    builderEl.gateParameter = document.getElementById("gateParameter");
    builderEl.addGateBtn = document.getElementById("addGateBtn");
    builderEl.removeLastGateBtn = document.getElementById("removeLastGateBtn");
    builderEl.clearCircuitBtn = document.getElementById("clearCircuitBtn");
    builderEl.saveCircuitBtn = document.getElementById("saveCircuitBtn");
    builderEl.builderSequence = document.getElementById("builderSequence");
    builderEl.savedCircuitList = document.getElementById("savedCircuitList");
}

function bindBuilderUI() {
    builderEl.gateButtons.forEach((button) => {
        button.addEventListener("click", () => {
            builderState.selectedGate = button.dataset.gate;
            highlightSelectedGate();
        });
    });

    builderEl.addGateBtn.addEventListener("click", addGateToSequence);
    builderEl.removeLastGateBtn.addEventListener("click", () => {
        builderState.gateSequence.pop();
        renderBuilderSequence();
    });
    builderEl.clearCircuitBtn.addEventListener("click", () => {
        builderState.gateSequence = [];
        renderBuilderSequence();
    });
    builderEl.saveCircuitBtn.addEventListener("click", saveCircuit);
}

function highlightSelectedGate() {
    builderEl.gateButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.gate === builderState.selectedGate);
    });
}

function addGateToSequence() {
    const gateType = builderState.selectedGate;
    const targetQubit = parseInt(builderEl.targetQubit.value || "0", 10);
    const controlQubit = parseInt(builderEl.controlQubit.value || "0", 10);
    const parameter = parseFloat(builderEl.gateParameter.value || "0");

    const gate = {
        type: gateType,
        target_qubit: targetQubit,
        control_qubit: gateType === "CX" ? controlQubit : null,
        parameter: ["RX", "RY", "RZ"].includes(gateType) ? Number(parameter.toFixed(2)) : null,
    };

    builderState.gateSequence.push(gate);
    renderBuilderSequence();
}

function renderBuilderSequence() {
    if (!builderState.gateSequence.length) {
        builderEl.builderSequence.className = "sequence-board empty-state";
        builderEl.builderSequence.textContent = "No gates added yet.";
        return;
    }

    builderEl.builderSequence.className = "sequence-board";
    builderEl.builderSequence.innerHTML = `
        <div class="sequence-row">
            ${builderState.gateSequence.map((gate, index) => {
                const suffixParts = [`q${gate.target_qubit}`];
                if (gate.control_qubit !== null && gate.control_qubit !== undefined) {
                    suffixParts.push(`ctrl q${gate.control_qubit}`);
                }
                if (gate.parameter !== null && gate.parameter !== undefined) {
                    suffixParts.push(`θ=${gate.parameter}`);
                }
                return `<div class="builder-gate-chip">${index + 1}. ${gate.type} <span>${suffixParts.join(" • ")}</span></div>`;
            }).join("")}
        </div>
    `;
}

async function saveCircuit() {
    const name = builderEl.circuitName.value.trim();
    const numberOfQubits = parseInt(builderEl.numQubits.value || "1", 10);

    if (!name) {
        alert("Please enter a circuit name.");
        return;
    }
    if (!builderState.gateSequence.length) {
        alert("Please add at least one gate.");
        return;
    }

    const payload = {
        name,
        mode: "custom",
        number_of_qubits: Math.max(1, numberOfQubits),
        gate_sequence: builderState.gateSequence,
        description: "Custom circuit created in QuSenseSim builder.",
    };

    const response = await fetch("/api/circuits/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (result.error) {
        alert(result.error);
        return;
    }

    builderEl.circuitName.value = "";
    builderState.gateSequence = [];
    renderBuilderSequence();
    await loadSavedCircuits();
    alert("Circuit saved successfully.");
}

async function loadSavedCircuits() {
    const response = await fetch("/api/circuits/custom");
    const circuits = await response.json();

    if (!circuits.length) {
        builderEl.savedCircuitList.innerHTML = `
            <div class="saved-circuit-card">
                <p>No custom circuits saved yet.</p>
            </div>
        `;
        return;
    }

    builderEl.savedCircuitList.innerHTML = circuits.map((circuit) => {
        const preview = (circuit.gate_sequence || []).map((gate) => gate.parameter == null ? gate.type : `${gate.type}(${gate.parameter})`).join(" → ");
        return `
            <div class="saved-circuit-card">
                <h4>${circuit.name}</h4>
                <p>${circuit.number_of_qubits} qubit${circuit.number_of_qubits > 1 ? "s" : ""} • ${(circuit.gate_sequence || []).length} gates</p>
                <p>${preview}</p>
            </div>
        `;
    }).join("");
}
