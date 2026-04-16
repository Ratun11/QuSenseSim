const appState = {
    setupState: null,
    analysisData: null,
    summary: null,
    tables: null,
    rankings: null,
    variants: null,
    charts: {},
    currentTableName: "global",
    currentFigureId: "fiTimeChart",
    personalizedVariantMap: {},
};

document.addEventListener("DOMContentLoaded", async () => {
    bindUI();
    await loadInitial();
});

function el(id) { return document.getElementById(id); }
function bindIf(id, event, handler) { const node = el(id); if (node) node.addEventListener(event, handler); }

function bindUI() {
    bindIf("runCollaborationBtn", "click", runAnalysis);
    bindIf("backToSetupBtn", "click", () => window.location.href = "/dashboard");
    bindIf("chartModeFilter", "change", refreshDerivedViews);
    bindIf("chartScopeFilter", "change", refreshDerivedViews);
    bindIf("modeSelect", "change", populateVariantSelect);
    bindIf("scopeSelect", "change", populateVariantSelect);
    bindIf("variantSelect", "change", renderSensorSection);
    bindIf("sensorSelect", "change", renderSensorDrilldown);
    bindIf("sensorMetricSelect", "change", renderSensorDrilldown);
    bindIf("exportSummaryJsonBtn", "click", exportSummaryJson);
    bindIf("downloadCurrentTableBtn", "click", downloadCurrentTableCsv);
    bindIf("exportCurrentFigureBtn", "click", exportCurrentFigurePng);
    bindIf("exportSnapshotBtn", "click", exportSnapshot);

    document.querySelectorAll('input[name="mitigationScope"]').forEach((radio) => {
        radio.addEventListener("change", toggleScopePanels);
    });

    document.querySelectorAll(".analysis-block").forEach((block) => {
        block.addEventListener("mouseenter", () => {
            appState.currentTableName = block.dataset.table || "global";
            appState.currentFigureId = block.dataset.figure || "fiTimeChart";
        });
    });
}

async function loadInitial() {
    await loadSavedState();
    await loadVariants();
    renderSetupSummary();
    renderUniformVariantList();
    renderPersonalizedTable();
    toggleScopePanels();

    if (!appState.setupState) {
        setStatus("No saved setup found yet. Go back to the dashboard first.");
        return;
    }

    const existing = await fetch("/api/get_analysis").then(r => r.json());
    if (existing && existing.results) {
        appState.analysisData = existing;
        populateFilterOptions();
        await loadDerivedData();
        renderAll();
    }
}

async function loadSavedState() {
    const payload = await fetch("/api/load_state").then(r => r.json());
    appState.setupState = payload.setup_state || null;
}

async function loadVariants() {
    appState.variants = await fetch("/api/mitigation/variants").then(r => r.json());
}

function renderSetupSummary() {
    const target = el("setupSummary");
    if (!target) return;
    if (!appState.setupState) {
        target.innerHTML = '<div class="summary-pill">No saved setup found</div>';
        return;
    }
    const sensors = appState.setupState.sensors || [];
    const sources = appState.setupState.sources || [];
    const env = appState.setupState.environment || {};
    target.innerHTML = `
        <div class="summary-pill">Sensors: ${sensors.length}</div>
        <div class="summary-pill">Sources: ${sources.length}</div>
        <div class="summary-pill">Field: ${Number(env.field_strength || 0).toFixed(2)}</div>
        <div class="summary-pill">Phase shift: ${Number(env.phase_shift || 0).toFixed(2)}</div>
        <div class="summary-pill">Env noise: ${Number(env.global_noise || 0).toFixed(2)}</div>
    `;
}

function renderUniformVariantList() {
    const executionTarget = el("executionVariantList");
    const postTarget = el("postVariantList");
    if (executionTarget) executionTarget.innerHTML = "";
    if (postTarget) postTarget.innerHTML = "";

    const families = appState.variants?.families || {};
    const renderGroup = (target, groups) => {
        if (!target) return;
        (groups || []).forEach((group) => {
            const card = document.createElement("div");
            card.className = "analysis-card nested-card";
            const options = group.variants.map((variant) => `
                <label class="method-option">
                    <input type="checkbox" value="${variant.key}" class="uniform-variant-checkbox">
                    <div class="method-copy">
                        <strong>${variant.label}</strong>
                        <span>${variant.parameter_name} = ${variant.parameter_value}</span>
                    </div>
                </label>
            `).join("");
            card.innerHTML = `<div class="card-header"><h3>${group.family}</h3><p>Choose one or more variants.</p></div>${options}`;
            target.appendChild(card);
        });
    };

    renderGroup(executionTarget, families.execution);
    renderGroup(postTarget, families.post);
}

function renderPersonalizedTable() {
    const tbody = document.querySelector("#personalizedTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    appState.personalizedVariantMap = {};
    if (!appState.setupState?.sensors?.length) return;

    const groupedFamilies = appState.variants?.families || {};
    appState.setupState.sensors.forEach((sensor) => {
        appState.personalizedVariantMap[String(sensor.id)] = [];
        const tr = document.createElement("tr");
        const familyOptions = [
            '<option value="No mitigation">No mitigation</option>',
            '<optgroup label="Execution-Time Mitigation Techniques">',
            ...((groupedFamilies.execution || []).map((family) => `<option value="${family.family}">${family.family}</option>`)),
            '</optgroup>',
            '<optgroup label="Post-Processing Mitigation Techniques">',
            ...((groupedFamilies.post || []).map((family) => `<option value="${family.family}">${family.family}</option>`)),
            '</optgroup>'
        ].join("");

        tr.innerHTML = `
            <td>${sensor.name}</td>
            <td>
                <select class="sensor-select personalized-family" data-sensor-id="${sensor.id}">
                    ${familyOptions}
                </select>
            </td>
            <td>
                <select class="sensor-select personalized-variant" data-sensor-id="${sensor.id}">
                    <option value="baseline">No mitigation</option>
                </select>
            </td>
            <td>
                <button type="button" class="btn btn-secondary add-personalized-variant" data-sensor-id="${sensor.id}">
                    Add
                </button>
            </td>
            <td>
                <div class="selected-variant-chips" id="chips-${sensor.id}"></div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.querySelectorAll(".personalized-family").forEach((select) => {
        select.addEventListener("change", () => populatePersonalizedVariant(select.dataset.sensorId, select.value));
    });

    document.querySelectorAll(".add-personalized-variant").forEach((button) => {
        button.addEventListener("click", () => addPersonalizedVariant(button.dataset.sensorId));
    });
}

function populatePersonalizedVariant(sensorId, family) {
    const select = document.querySelector(`.personalized-variant[data-sensor-id="${sensorId}"]`);
    if (!select) return;

    if (family === "No mitigation" || family === "None") {
        select.innerHTML = '<option value="baseline">No mitigation</option>';
        return;
    }

    const grouped = appState.variants?.families || {};
    const allGroups = [...(grouped.execution || []), ...(grouped.post || [])];
    const familyGroup = allGroups.find((f) => f.family.toLowerCase() === family.toLowerCase());

    if (!familyGroup) {
        select.innerHTML = '<option value="baseline">No mitigation</option>';
        return;
    }

    const options = familyGroup.variants.map((variant) => `<option value="${variant.key}">${variant.label}</option>`).join("");
    select.innerHTML = options || '<option value="baseline">No mitigation</option>';
}

function addPersonalizedVariant(sensorId) {
    const variantSelect = document.querySelector(`.personalized-variant[data-sensor-id="${sensorId}"]`);
    if (!variantSelect) return;
    const variantKey = variantSelect.value;
    if (!variantKey || variantKey === "baseline") return;

    if (!appState.personalizedVariantMap[sensorId]) appState.personalizedVariantMap[sensorId] = [];
    if (!appState.personalizedVariantMap[sensorId].includes(variantKey)) {
        appState.personalizedVariantMap[sensorId].push(variantKey);
    }
    renderPersonalizedChips(sensorId);
}

function renderPersonalizedChips(sensorId) {
    const chipBox = document.getElementById(`chips-${sensorId}`);
    if (!chipBox) return;
    const selected = appState.personalizedVariantMap[sensorId] || [];
    chipBox.innerHTML = selected.map((variantKey) => {
        const variant = (appState.variants?.all_variants || []).find(v => v.key === variantKey);
        const label = variant ? variant.label : variantKey;
        return `<span class="variant-chip">${label}<button type="button" class="chip-remove" onclick="removePersonalizedVariant('${sensorId}', '${variantKey}')">×</button></span>`;
    }).join("");
}

window.removePersonalizedVariant = function(sensorId, variantKey) {
    if (!appState.personalizedVariantMap[sensorId]) return;
    appState.personalizedVariantMap[sensorId] = appState.personalizedVariantMap[sensorId].filter(v => v !== variantKey);
    renderPersonalizedChips(sensorId);
};

function toggleScopePanels() {
    const scope = document.querySelector('input[name="mitigationScope"]:checked')?.value || "uniform";
    el("uniformVariantPanel")?.classList.toggle("hidden", scope !== "uniform");
    el("personalizedPanel")?.classList.toggle("hidden", scope !== "personalized");
}

function selectedModes() {
    const modes = Array.from(document.querySelectorAll('#modeList input:checked')).map(elm => elm.value);
    return modes.length ? modes : ["independent"];
}

function selectedUniformVariants() {
    return Array.from(document.querySelectorAll(".uniform-variant-checkbox:checked")).map(elm => elm.value);
}

function personalizedAssignments() {
    return appState.personalizedVariantMap;
}

function buildTimeConfig() {
    return {
        total_time: Number(el("totalTimeInput")?.value || 6),
        num_steps: Number(el("numStepsInput")?.value || 60),
        t1: Number(el("t1Input")?.value || 7),
        t2: Number(el("t2Input")?.value || 4),
    };
}

async function runAnalysis() {
    if (!appState.setupState) {
        setStatus("No setup state found. Please go back to the dashboard first.");
        return;
    }
    setStatus("Running analysis...");
    const response = await fetch("/api/run_collaboration_analysis", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            modes: selectedModes(),
            state: appState.setupState,
            time_config: buildTimeConfig(),
            uniform_variants: selectedUniformVariants(),
            personalized_assignments: personalizedAssignments(),
        }),
    });
    const data = await response.json();
    if (data.error) {
        setStatus(data.error);
        return;
    }
    appState.analysisData = data;
    populateFilterOptions();
    await loadDerivedData();
    renderAll();
    setStatus("Analysis complete.");
}

function populateFilterOptions() {
    const modeFilter = el("chartModeFilter");
    if (!modeFilter || !appState.analysisData) return;
    const prevMode = modeFilter.value || "all";
    modeFilter.innerHTML = '<option value="all">All Modes</option>' + (appState.analysisData.mode_order || []).map((mode) => `<option value="${mode}">${appState.analysisData.mode_metadata[mode].label}</option>`).join("");
    if ([...modeFilter.options].some(o => o.value === prevMode)) modeFilter.value = prevMode;
}

async function loadDerivedData() {
    const mode = el("chartModeFilter")?.value || "all";
    const scope = el("chartScopeFilter")?.value || "all";
    const [summary, tables, rankings] = await Promise.all([
        fetch("/api/analysis/summary").then(r => r.json()),
        fetch(`/api/analysis/tables?mode=${encodeURIComponent(mode)}&scope=${encodeURIComponent(scope)}`).then(r => r.json()),
        fetch("/api/analysis/rankings").then(r => r.json()),
    ]);
    appState.summary = summary;
    appState.tables = tables;
    appState.rankings = rankings;
}

async function refreshDerivedViews() {
    if (!appState.analysisData) return;
    await loadDerivedData();
    renderAll();
}

function renderAll() {
    if (!appState.analysisData) return;
    populateFilterOptions();
    populateSectionSelectors();
    renderInsightCards();
    renderInterpretation();
    renderFigureTableSections();
    renderSensorSection();
    renderSensorDrilldown();
}

function populateSectionSelectors() {
    const modeSelect = el("modeSelect");
    if (modeSelect) {
        const prevMode = modeSelect.value;
        modeSelect.innerHTML = (appState.analysisData.mode_order || []).map((mode) => `<option value="${mode}">${appState.analysisData.mode_metadata[mode].label}</option>`).join("");
        if ([...modeSelect.options].some(o => o.value === prevMode)) modeSelect.value = prevMode;
    }

    const sensorSelect = el("sensorSelect");
    if (sensorSelect) {
        const prevSensor = sensorSelect.value;
        sensorSelect.innerHTML = (appState.analysisData.sensor_names || []).map((sensor) => `<option value="${sensor.id}">${sensor.name}</option>`).join("");
        if ([...sensorSelect.options].some(o => o.value === prevSensor)) sensorSelect.value = prevSensor;
    }

    populateVariantSelect();
}

function populateVariantSelect() {
    if (!appState.analysisData) return;
    const modeKey = el("modeSelect")?.value || appState.analysisData.mode_order?.[0];
    const scope = el("scopeSelect")?.value || "none";
    const variantSelect = el("variantSelect");
    if (!variantSelect) return;
    const prev = variantSelect.value;
    const modePack = appState.analysisData.results?.[modeKey];
    const options = (modePack?.config_order || []).map((configKey) => modePack.results[configKey]).filter((res) => res.scope === scope);
    variantSelect.innerHTML = options.map((res) => `<option value="${res.variant_key}">${res.label}</option>`).join("");
    if ([...variantSelect.options].some(o => o.value === prev)) variantSelect.value = prev;
    if (!variantSelect.value && variantSelect.options.length) variantSelect.value = variantSelect.options[0].value;
    renderSensorSection();
}

function renderInsightCards() {
    const r = appState.rankings || {};
    setInsight("bestOverall", r.best_overall_method ? `${r.best_overall_method.mode_label} · ${r.best_overall_method.variant}` : "—", r.best_overall_method ? `Final FI ${Number(r.best_overall_method.final_avg_fi).toFixed(3)}` : "Run analysis");
    setInsight("bestVariant", r.best_variant ? r.best_variant.variant : "—", r.best_variant ? `${r.best_variant.mode_label} · ${Number(r.best_variant.final_avg_fi).toFixed(3)}` : "Run analysis");
    setInsight("bestMode", r.best_mode ? r.best_mode.mode_label : "—", r.best_mode ? `Best variant: ${r.best_mode.variant}` : "Run analysis");
    setInsight("bestPersonalized", r.best_personalized_setup ? r.best_personalized_setup.mode_label : "—", r.best_personalized_setup ? `${Number(r.best_personalized_setup.final_avg_fi).toFixed(3)} final FI` : "Run analysis");
    setInsight("personalizedGain", r.personalized_gain_over_uniform != null ? `${Number(r.personalized_gain_over_uniform).toFixed(2)}%` : "—", "Gain over best uniform variant");
}

function setInsight(prefix, title, subtitle) {
    const card = el(`${prefix}Card`);
    const sub = el(`${prefix}Sub`);
    if (card) card.textContent = title;
    if (sub) sub.textContent = subtitle;
}

function renderInterpretation() {
    const panel = el("interpretationPanel");
    if (panel) panel.textContent = appState.rankings?.interpretation || "Run analysis to generate an interpretation.";
}

function filteredResults() {
    const modeFilter = el("chartModeFilter")?.value || "all";
    const scopeFilter = el("chartScopeFilter")?.value || "all";
    const combos = [];
    (appState.analysisData.mode_order || []).forEach((mode) => {
        if (modeFilter !== "all" && mode !== modeFilter) return;
        const modePack = appState.analysisData.results[mode];
        (modePack.config_order || []).forEach((configKey) => {
            const res = modePack.results[configKey];
            if (scopeFilter !== "all" && res.scope !== scopeFilter) return;
            combos.push({
                mode,
                modeLabel: appState.analysisData.mode_metadata[mode].label,
                res,
                label: `${appState.analysisData.mode_metadata[mode].label} · ${res.label}`,
            });
        });
    });
    return combos;
}

function renderFigureTableSections() {
    if (!appState.analysisData) return;
    const combos = filteredResults();
    const time = appState.analysisData.time_points || [];

    createOrUpdateLineChart("fiTimeChart", time, combos.map(c => ({label: c.label, data: c.res.global_time_series.fisher_info})));
    createOrUpdateLineChart("crbTimeChart", time, combos.map(c => ({label: c.label, data: c.res.global_time_series.crb})));
    createOrUpdateLineChart("noiseTimeChart", time, combos.map(c => ({label: c.label, data: c.res.global_time_series.effective_noise})));

    const globalRows = appState.tables?.global || [];
    createOrUpdateBarChart("modeBarChart", unique(globalRows.map(r => r.mode)), [
        {label: "Best Final FI", data: bestPerCategory(globalRows, "mode", "final_fi", true)},
        {label: "Lowest Final CRB", data: bestPerCategory(globalRows, "mode", "final_crb", false)},
    ]);
    const mitigationRows = aggregateMitigationGain(globalRows);
    createOrUpdateBarChart("mitigationGainChart", mitigationRows.labels, [
        {label: "FI Improvement", data: mitigationRows.fi},
        {label: "Noise Improvement", data: mitigationRows.noise},
    ]);

    renderTable("globalTable", globalRows, "final_fi", true);
    renderTable("estimateTable", appState.tables?.estimate || [], "error", false);
    renderTable("noiseTable", appState.tables?.noise || [], "final", false);

    const fiBadge = el("fiBestBadge");
    const estimateBadge = el("estimateBestBadge");
    const noiseBadge = el("noiseBestBadge");
    const modeBadge = el("modeBestBadge");
    if (fiBadge) fiBadge.textContent = bestBadge(globalRows, "final_fi", true, "Best variant");
    if (estimateBadge) estimateBadge.textContent = bestBadge(appState.tables?.estimate || [], "error", false, "Lowest error");
    if (noiseBadge) noiseBadge.textContent = bestBadge(appState.tables?.noise || [], "final", false, "Lowest noise");
    if (modeBadge) modeBadge.textContent = appState.rankings?.best_mode ? `Best mode: ${appState.rankings.best_mode.mode_label}` : "Best mode: —";

    const fiInsight = el("fiInsight");
    const estimateInsight = el("estimateInsight");
    const noiseInsight = el("noiseInsight");
    const modeInsight = el("modeInsight");
    if (fiInsight) fiInsight.textContent = insightText(globalRows, "final_fi", true, "Fisher Information");
    if (estimateInsight) estimateInsight.textContent = insightText(appState.tables?.estimate || [], "error", false, "estimate error");
    if (noiseInsight) noiseInsight.textContent = insightText(appState.tables?.noise || [], "final", false, "effective noise");
    if (modeInsight) modeInsight.textContent = appState.rankings?.best_mode ? `${appState.rankings.best_mode.mode_label} currently gives the strongest mode-level final FI.` : "Run analysis to compare modes.";
}

function renderSensorSection() {
    if (!appState.analysisData) return;
    const modeKey = el("modeSelect")?.value || appState.analysisData.mode_order?.[0];
    const scope = el("scopeSelect")?.value || "none";
    const variantKey = el("variantSelect")?.value;
    const modePack = appState.analysisData.results?.[modeKey];
    if (!modePack) return;

    const result = (modePack.config_order || []).map((key) => modePack.results[key]).find((res) => res.scope === scope && res.variant_key === variantKey) ||
                   (modePack.config_order || []).map((key) => modePack.results[key]).find((res) => res.scope === scope) ||
                   modePack.results[modePack.config_order[0]];
    if (!result) return;

    const sensorRows = result.sensors.map((sensor) => ({
        sensor: sensor.name,
        mode: appState.analysisData.mode_metadata[modeKey].label,
        scope: result.scope_label,
        family: sensor.family,
        variant: Array.isArray(sensor.all_variant_keys) && sensor.all_variant_keys.length
            ? sensor.all_variant_keys.map((key) => {
                const v = (appState.variants?.all_variants || []).find(item => item.key === key);
                return v ? v.label : key;
            }).join(" + ")
            : sensor.label,
        fi: sensor.final.fisher_info,
        crb: sensor.final.crb,
        noise: sensor.final.effective_noise,
        reliability: sensor.reliability_weight || 0,
    }));
    renderTable("sensorTable", sensorRows, "reliability", true);

    createOrUpdateBarChart("sensorContributionChart", sensorRows.map(r => r.sensor), [
        {label: "Final FI", data: sensorRows.map(r => r.fi)},
    ]);
    createOrUpdateBarChart("sensorReliabilityChart", sensorRows.map(r => r.sensor), [
        {label: "Reliability", data: sensorRows.map(r => r.reliability)},
    ]);

    const sensorBest = el("sensorBestBadge");
    const sensorInsight = el("sensorInsight");
    if (sensorBest) sensorBest.textContent = appState.rankings?.best_personalized_setup ? `Best personalized setup: ${appState.rankings.best_personalized_setup.mode_label}` : "Best personalized setup: —";
    if (sensorInsight) sensorInsight.textContent = appState.rankings?.best_personalized_setup ? `Personalized mitigation is strongest in ${appState.rankings.best_personalized_setup.mode_label}.` : "Run analysis to inspect sensor-level behavior.";
}

function renderSensorDrilldown() {
    if (!appState.analysisData) return;
    const sensorId = Number(el("sensorSelect")?.value || appState.analysisData.sensor_names?.[0]?.id);
    const metric = el("sensorMetricSelect")?.value || "fisher_info";
    const combos = filteredResults();

    const datasets = combos.map((combo) => {
        const sensor = combo.res.sensors.find((s) => Number(s.id) === sensorId);
        return sensor ? {label: combo.label, data: sensor.time_series[metric]} : null;
    }).filter(Boolean);

    createOrUpdateLineChart("sensorMetricChart", appState.analysisData.time_points || [], datasets);
}

function renderTable(tableId, rows, metricKey, higherIsBetter) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;
    tbody.innerHTML = "";
    if (!rows.length) return;

    const sorted = [...rows].sort((a, b) => higherIsBetter ? Number(b[metricKey]) - Number(a[metricKey]) : Number(a[metricKey]) - Number(b[metricKey]));
    const best = Number(sorted[0][metricKey]);
    const second = sorted.length > 1 ? Number(sorted[1][metricKey]) : best;
    const worst = Number(sorted[sorted.length - 1][metricKey]);

    rows.forEach((row) => {
        const tr = document.createElement("tr");
        const current = Number(row[metricKey]);
        if (current === best) tr.classList.add("best-row");
        else if (rows.length > 2 && current === second) tr.classList.add("second-row");
        else if (rows.length > 2 && current === worst) tr.classList.add("worst-row");

        tr.innerHTML = Object.entries(row).filter(([k]) => !k.endsWith("_key")).map(([k, v]) => {
            let cls = "";
            if (k === metricKey) {
                if (current === best) cls = "value-best";
                else if (rows.length > 2 && current === second) cls = "value-second";
                else if (rows.length > 2 && current === worst) cls = "value-worst";
            }
            return `<td class="${cls}">${formatValue(v)}</td>`;
        }).join("");
        tbody.appendChild(tr);
    });
}

function formatValue(v) { return typeof v === "number" ? Number(v).toFixed(3) : String(v); }

function bestBadge(rows, metricKey, higherIsBetter, prefix) {
    if (!rows.length) return `${prefix}: —`;
    const best = [...rows].sort((a, b) => higherIsBetter ? b[metricKey] - a[metricKey] : a[metricKey] - b[metricKey])[0];
    return `${prefix}: ${best.mode ? `${best.mode} · ` : ""}${best.variant || best.sensor || "—"}`;
}

function insightText(rows, metricKey, higherIsBetter, noun) {
    if (!rows.length) return `Run analysis to summarize ${noun}.`;
    const best = [...rows].sort((a, b) => higherIsBetter ? b[metricKey] - a[metricKey] : a[metricKey] - b[metricKey])[0];
    return `${best.mode || "Current view"} with ${best.variant || best.sensor} is the strongest configuration for ${noun}.`;
}

function unique(arr) { return [...new Set(arr)]; }

function bestPerCategory(rows, categoryKey, metricKey, higherIsBetter) {
    const categories = unique(rows.map(r => r[categoryKey]));
    return categories.map((category) => {
        const subset = rows.filter(r => r[categoryKey] === category);
        const sorted = subset.sort((a, b) => higherIsBetter ? b[metricKey] - a[metricKey] : a[metricKey] - b[metricKey]);
        return sorted.length ? sorted[0][metricKey] : 0;
    });
}

function aggregateMitigationGain(rows) {
    const byVariant = {};
    rows.filter(r => r.scope !== "No Mitigation").forEach((row) => {
        if (!byVariant[row.variant]) byVariant[row.variant] = {fi: [], noise: []};
        byVariant[row.variant].fi.push(Number(row.improvement || 0));
        byVariant[row.variant].noise.push(Math.max(0, 1 - Number(row.avg_noise || 0)));
    });
    const labels = Object.keys(byVariant);
    return {
        labels,
        fi: labels.map(l => avg(byVariant[l].fi)),
        noise: labels.map(l => avg(byVariant[l].noise)),
    };
}

function avg(values) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0; }

function chartColors(index) {
    const palette = ["#2563eb", "#16a34a", "#dc2626", "#7c3aed", "#ea580c", "#0891b2", "#4f46e5", "#ca8a04", "#be185d", "#0f766e", "#9333ea", "#0ea5e9"];
    return palette[index % palette.length];
}

function chartTheme() {
    const dark = document.body.classList.contains("dark-theme");
    return {
        tickColor: dark ? "#cbd5e1" : "#334155",
        gridColor: dark ? "rgba(148,163,184,0.18)" : "rgba(51,65,85,0.10)",
        legendColor: dark ? "#e2e8f0" : "#0f172a",
    };
}

function createOrUpdateLineChart(canvasId, labels, datasetsInput) {
    if (!window.Chart) return;
    const ctx = el(canvasId);
    if (!ctx) return;
    if (appState.charts[canvasId]) appState.charts[canvasId].destroy();
    const theme = chartTheme();
    const datasets = datasetsInput.map((item, idx) => ({
        label: item.label,
        data: item.data,
        borderColor: chartColors(idx),
        backgroundColor: chartColors(idx),
        borderWidth: 2,
        fill: false,
        tension: 0.25,
        pointRadius: 0,
    }));
    appState.charts[canvasId] = new Chart(ctx, {
        type: "line",
        data: {labels, datasets},
        options: chartOptions(theme, false),
    });
}

function createOrUpdateBarChart(canvasId, labels, datasetsInput) {
    if (!window.Chart) return;
    const ctx = el(canvasId);
    if (!ctx) return;
    if (appState.charts[canvasId]) appState.charts[canvasId].destroy();
    const theme = chartTheme();
    const datasets = datasetsInput.map((item, idx) => ({
        label: item.label,
        data: item.data,
        borderColor: chartColors(idx),
        backgroundColor: chartColors(idx),
        borderWidth: 1,
        borderRadius: 8,
    }));
    appState.charts[canvasId] = new Chart(ctx, {
        type: "bar",
        data: {labels, datasets},
        options: chartOptions(theme, true),
    });
}

function chartOptions(theme, beginAtZero) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {mode: "nearest", intersect: false},
        layout: {padding: 6},
        plugins: {
            legend: {
                position: "bottom",
                labels: {color: theme.legendColor, boxWidth: 12, boxHeight: 12, padding: 10, font: {size: 11}},
            },
        },
        scales: {
            x: {ticks: {color: theme.tickColor, maxRotation: 0, autoSkip: true, maxTicksLimit: 8}, grid: {color: theme.gridColor}},
            y: {beginAtZero, ticks: {color: theme.tickColor}, grid: {color: theme.gridColor}},
        },
    };
}

async function exportSummaryJson() {
    const payload = await fetch("/api/analysis/summary").then(r => r.json());
    downloadBlob("analysis_summary.json", JSON.stringify(payload, null, 2), "application/json");
}

async function downloadCurrentTableCsv() {
    const mode = el("chartModeFilter")?.value || "all";
    const scope = el("chartScopeFilter")?.value || "all";
    const response = await fetch("/api/export/table", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({table: appState.currentTableName, mode, scope}),
    });
    const payload = await response.json();
    downloadBlob(payload.filename || "table.csv", payload.content || "", "text/csv");
}

async function exportCurrentFigurePng() {
    await fetch("/api/export/figure", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({figure: appState.currentFigureId}),
    });
    const canvas = el(appState.currentFigureId);
    if (!canvas) return;
    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = `${appState.currentFigureId}.png`;
    link.click();
}

async function exportSnapshot() {
    const payload = await fetch("/api/export/report").then(r => r.json());
    downloadBlob(payload.filename || "analysis_report_snapshot.json", payload.content || "{}", "application/json");
}

function downloadBlob(filename, content, mimeType) {
    const blob = new Blob([content], {type: mimeType});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function setStatus(message) {
    const target = el("analysisStatus");
    if (target) target.textContent = message;
}

window.addEventListener("beforeunload", () => {
    Object.values(appState.charts).forEach((chart) => chart?.destroy?.());
});
