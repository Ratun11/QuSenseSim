# QuSenseSim Final Clean Production Build

This package is the cleaned production archive for the current QuSenseSim state.

Included in this build:
- backend-connected simulator workflow
- circuit system and theme toggle
- noise-aware modeling
- mitigation pipeline
- time-dependent physics with T1/T2-style behavior
- collaboration modes
- analysis layout with graph/table pairing
- mitigation variants
- execution-time vs post-processing grouping
- personalized sensor mitigation with multiple variants per sensor
- export helpers and summary tables

Recommended test flow:
1. Run the dashboard and save a setup state.
2. Open Analysis.
3. Try Uniform Mitigation with several variants.
4. Try Personalized Sensor Mitigation and add multiple variants to one sensor.
5. Run analysis and verify graphs, tables, and exports.

Run:
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
pip install flask
python app.py
```

Mac/Linux:
```bash
source venv/bin/activate
pip install flask
python app.py
```
