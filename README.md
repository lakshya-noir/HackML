# PathSnap

**Frozen final release: `pathsnap-monotone-v1`.** Default API, evaluation and decoded Folium maps use `artifacts/models/final_monotone_v1` with `artifacts/decoder_config.json`. [Final report results](docs/report/FINAL_RESULTS.md) · [Release manifest](artifacts/final_release.json) · [Final chart](results/final_results.png).

Selection evidence: [order-aware model improvement](outputs/model-improvement/20261118-120758/READ_FIRST.md). That verified candidate has now been promoted. Earlier sampled results and screenshots are historical, not current demo results.

## Run the two-laptop demo

See [Mahesh's exact Laptop 2 instructions](docs/TWO_LAPTOP_DEMO.md). Laptop 1 runs `python -m pathsnap.api.app --host 0.0.0.0 --port 8000`. Mahesh runs `python -m http.server 5500 --bind 127.0.0.1 --directory ui` from his clone and opens `http://localhost:5500`. In the API box he enters Laptop 1's LAN URL (not his own localhost). No ML dependencies or data are needed on his machine.

## First-evaluation revision and evidence

- [Complete ML notes and 40 viva questions with answers](docs/ML_NOTES.md)
- [Simple work log](docs/WORK_LOG_SIMPLE.md)
- [Team checklist](docs/TEAM_CHECKLIST.md)
- [Read the measured findings first](outputs/evaluation_1130/READ_FIRST.md)
- [Model comparison chart](outputs/evaluation_1130/02_model_comparison.png)
- [Data audit chart](outputs/evaluation_1130/01_data_overview.png)
- [Map disagreement close-ups](outputs/evaluation_1130/04_disagreement_closeups.png)

Generated evidence is included in `outputs/evaluation_1130/` and `outputs/inspection/`. GitHub displays PNG images; download/open Folium HTML in a browser to interact with maps. Raw data and feature caches remain local. Published classifier metrics use approximate reference labels; HMM and distributed-demo results require separate verification.

GPS map matching and route reconstruction for the PES University ML hackathon, 18 November 2026.

## Start

```bash
git clone https://github.com/lakshya-noir/HackML.git
cd HackML.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/import_dataset.py '/path/to/Student folder.zip'
python scripts/inventory.py
```

Raw data stays local under `data/`. Each teammate imports the same organiser ZIP. Do not add evaluator data during development.

## Ownership

- Lakshya + Codex: `pathsnap/data.py`, `pathsnap/features/`, `pathsnap/models/`, training scripts and saved inference artifacts.
- Nakul + Claude Code: `pathsnap/decoder/`, `pathsnap/api/`, road-network routing and backend integration.
- Member 3: `analysis/`, experiment execution, data quality checks, maps and recorded results in `results/`.
- Member 4: `ui/`, `docs/report/`, README updates, two-laptop testing and submission evidence.

Read `docs/CONTRACT.md` before implementing interfaces. Do not edit another owner's modules without coordinating. Commit working increments and integrate every 30 minutes.

## Immediate priorities

1. Verify data inventory and inspect a complete trip together.
2. Establish observation-to-reference alignment: `.route` is a sequence of arc IDs, not observation-level labels.
3. Agree on candidate generation and features; keep local arc IDs out of universal classifier labels.
4. Train five distinct models using the same features and trip-grouped splits; retain configurations and actual results.
5. Start a health endpoint and verify Laptop 2 can reach Laptop 1.

## Milestones (IST)

- 11:20: EDA, feature explanation, initial five-model results ready for 11:30 evaluation.
- 12:15: Bayesian tuning underway; classifier and decoder integrated.
- 13:00: Full two-laptop flow works on student-testing data.
- 14:00: Feature freeze; report, repository and demo verification.
- 14:30: Begin submission checks; submit by 15:00.

## Submission

Public GitHub repository with all source, experiment configurations/results, optimisation history, inference assets (within size constraints), Folium generation code/HTML, installation and deployment instructions. One consolidated PDF report with measured results and demonstration evidence. Never commit credentials or fabricate results.

Decoder, API and UI are developed separately by the assigned owners.

## ML experiments

Candidate generation, surrogate reference alignment, five-model training and Bayesian tuning are now implemented. See `docs/ML_NOTES.md` for methodology, metric definitions, limitations and backend integration. Decoder, API and UI remain assigned to their owners.

```bash
python -m pip install -r requirements-ml.txt
python scripts/train_models.py --max-observations 200
python scripts/train_models.py --max-observations 200 --trials 12
```

Results are saved under `results/`; feature caches under ignored `outputs/`. The initial selected and tuned artifacts are included under `artifacts/models/hist_gradient_boosting/` and `artifacts/models/tuned/`; other experimental artifacts stay local. Use the pinned ML dependencies when loading the saved model on Laptop 1.
