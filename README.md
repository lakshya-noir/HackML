# PathSnap

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
