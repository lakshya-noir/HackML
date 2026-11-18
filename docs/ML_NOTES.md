# PathSnap: ML implementation, results and viva guide

Updated 18 November 2026 before the 11:30 evaluation. This records work verified on Lakshya's machine. It does not claim Nakul's decoder/API or the distributed demo is complete.

## 1. Read first

### Integration update before 11:30

Nakul's `nakul-backend` branch has now been integrated into main. His decoder, FastAPI app and bundled Leaflet UI are present. The six synthetic decoder checks passed on Lakshya's machine, and HTTP smoke testing processed all ten student-test trips. See `docs/TWO_LAPTOP_DEMO.md` and `results/api_verification_local.json` for exact setup and the latest local verification. Earlier “not complete” statements below describe the ML-only stage; physical two-laptop/browser rendering and evaluator demonstration still need team confirmation.

The UI now has connection readiness/error handling, fresh-inference requests, metric-label descriptions and an optional API URL query parameter. Fresh POST requests bypass previously computed responses; they execute actual inference. Health checks and successful local HTTP requests are not proof of Mahesh's LAN/browser connection.

API evaluation uses monotone reference-route alignment on full trips, while the initial five-model comparison below used nearest-reference labels on sampled points. The API macro F1 includes reference arc classes; the initial comparison namespaces arc classes across trips. Do not directly compare these numbers. Route F1 is length-weighted arc-set overlap, not an order-sensitive sequence metric. The branch's earlier evaluation files may differ from current host results; use the dated local verification evidence and retain provenance.

We built the data and classifier part of a system that recovers likely roads from noisy GPS. Completed work includes raw loading, candidate generation, nine features, approximate labels, five-model comparison, trip-grouped validation, Bayesian tuning, saved-model scoring, Folium maps, all-trip audits and readable charts.

The main limitation: reference routes have no per-point timestamps. Our labels select the geometrically closest supplied reference road. Accuracy measures agreement with these **surrogate labels**, not independently verified physical ground truth.

Useful links: [simple work log](WORK_LOG_SIMPLE.md), [team checklist](TEAM_CHECKLIST.md), [integration contract](CONTRACT.md), [plain-language evidence pack](../outputs/evaluation_1130/READ_FIRST.md), [exact model results](../results/model_comparison.json).

## 2. Dataset and file meanings

- 80 training trips: **208,417 GPS observations**.
- 10 student-test trips: **19,160 observations**.
- Total: **227,577 observations**, 360 raw files. The ten reserved evaluator trips were not used.
- `.track`: longitude, latitude, timestamp in seconds.
- `.nodes`: longitude, latitude; zero-based row index is node ID.
- `.arcs`: from-node and to-node IDs; zero-based row index is trip-local arc ID.
- `.route`: chronological reference arc sequence, not one label per GPS row.

Raw data remains unchanged under `data/train/` and `data/student_test/`, excluded from Git. `results/data_inventory.csv` is only a file/size/row-count index. Sampling for training did not delete raw observations. Each teammate imports the organiser ZIP locally.

## 3. Full audit: actual findings

Sources: [per-trip audit](../outputs/evaluation_1130/trip_audit.csv), [partition summary](../outputs/evaluation_1130/data_summary.json), [EDA plot](../outputs/evaluation_1130/01_data_overview.png).

- All 90 trips loaded with expected column counts and valid node/route index ranges.
- No nonfinite GPS/node values, invalid GPS coordinate ranges, duplicate timestamps or non-increasing timestamps found.
- **7,550 gaps exceed one second**: 7,286 training, 264 student-test.
- Largest training gap: **153,064 seconds**, trip `00000090`, observations 534–535, timestamps 970 and 154034.
- Largest student-test gap: **210 seconds**, trip `00000065`, observations 114–115, timestamps 122 and 332.
- **106 zero-length arcs**: 100 training, six student-test. Direction is uninformative there.
- **89 graphs have multiple weakly connected components**: 79 training, all ten student-test. No isolated nodes found. Weak connectivity ignores direction; disconnected graphs do not prove the driven route itself crosses components.
- **14 reference transitions fail direct endpoint adjacency in the recorded direction**: 13 training, one student-test. This flags reference encoding/interpretation, not proof of an impossible journey.
- Shortest/longest training trips: `00000026` / `00000054`; student-test: `00000052` / `00000056`.

Summed graph sizes count trip-specific records, not unique physical roads across the dataset. Data issues are documented; raw files were not silently cleaned or imputed.

## 4. Geometry and candidate generation

`load_trip()` loads GPS/nodes/arcs only. `load_reference()` is separate for training labels/evaluation. Reference routes must never enter prediction features.

We approximate local metres around the first observation:

```text
x = (longitude − origin_longitude) × 111320 × cos(origin_latitude)
y = (latitude − origin_latitude) × 111320
```

Cosine uses radians. This is a regional approximation, not an exact geodesic/global projection. Arrays/GeoJSON use longitude–latitude; Folium markers use latitude–longitude.

Road arcs are line segments between endpoint nodes. We sample each segment every at most 30m including endpoints, build a KD-tree, retrieve up to 128 nearby samples, deduplicate arc IDs, then compute point-to-segment distances for those arcs. Segment sampling avoids midpoint-only search missing the end of a long road.

Keep up to eight nearest retrieved arcs within 100m. If none is within 100m, keep the nearest retrieved candidate. This is approximate retrieval: sample crowding and the eight-road cap can omit plausible roads. Fallback does not imply certainty. Candidate generation uses no reference membership.

## 5. Nine features in saved order

1. `distance_m`: GPS-to-road distance; nearer is often more plausible.
2. `heading_cos`: signed cosine between previous-to-next GPS motion and directed arc displacement.
3. `heading_abs_cos`: axis alignment regardless of direction.
4. `segment_length_m`: length of the road arc.
5. `projection_fraction`: clamped position along the road, 0 at start and 1 at end.
6. `speed_mps`: previous-to-next straight-line displacement divided by elapsed time, with a one-second denominator floor. This is an estimate, not measured vehicle speed.
7. `previous_distance_m`: previous observation's distance to the candidate.
8. `next_distance_m`: next observation's distance to the candidate.
9. `distance_rank`: zero-based nearest-candidate rank.

At endpoints, nearest available observations replace missing neighbours. Small geometric denominator floors keep features finite. Arc/node IDs and reference-route membership are excluded from feature vectors. Using the next observation makes this **offline trajectory matching**, not strictly causal live inference. Long gaps can weaken motion features.

## 6. Labels and ambiguity

For each GPS point, choose the nearest segment among the supplied reference-route arcs. Candidates matching that surrogate arc receive label 1; others receive 0. A missing surrogate candidate produces all-negative candidate rows and counts as a candidate miss; we do not inject reference roads into inference candidates.

This alignment ignores chronological progress along the reference route. Loops, adjacent arcs, parallel/overlapping directions and ties cause uncertainty. Ties can depend on reference order. Ambiguity means multiple distinct reference arc IDs have distances within 2m of the nearest distance. It is not a calibrated uncertainty score or proof of error.

After inspection we retained the initial baseline for the checkpoint, with explicit limits. Future general candidate/alignment changes require regenerated caches and retraining; do not manually correct known test answers. Official alignment clarification remains pending with the professor.

## 7. Experimental design

- Up to 200 equally spaced original observations per trip: 16,000 training observations and 2,000 student-test observations in the initial experiment. Each expands to a variable number of candidate rows.
- Features use original full-trajectory neighbours before subsampling.
- Three-fold `GroupKFold` groups by trip ID, so all candidate rows from a trip stay together.
- Scalers in the Logistic/NB pipelines fit inside each training fold. Tree models do not need scaling.
- Seed 42 where supported; explicit model configurations and fold trip IDs saved.
- Models fit permitted training trips; student-test data is for development comparison. Evaluator trips/results never choose features, thresholds, models or parameters.

`outputs/features-200.joblib` is an ignored cache keyed by sampling cap, not code/data hashes. Invalidate/version it after feature, label or raw-data changes. Do not resume an incompatible tuning study.

## 8. Models, configurations and reasoning

**Logistic Regression:** `StandardScaler` plus `LogisticRegression(max_iter=400, random_state=42)`, other pinned-version defaults. Regularised logistic loss, default L2 regularisation. Fast linear probability baseline; limited nonlinear interactions.

**Gaussian Naive Bayes:** `StandardScaler` plus default `GaussianNB()`. Fits Gaussian class-conditional distributions and priors. Correlated distance features challenge its conditional-independence assumption; fast but weakest CV fit here.

**Decision Tree:** depth 10, minimum leaf size 20, seed 42, default Gini splits. Learns nonlinear rules; depth/leaf limits constrain overfitting.

**Random Forest:** 100 trees, depth 14, minimum leaf size 5, `n_jobs=-1`, seed 42, default Gini splits. Averaging trees captures interactions at greater size/training cost.

**Histogram Gradient Boosting:** 100 iterations, 15 leaf nodes, initial learning rate 0.1, seed 42, log-loss objective. Histogram-based boosted trees learn nonlinear relationships efficiently. Narrow CV winner, not universally proven best. Library-default internal early stopping may apply; no epoch history was recorded.

Exact explicit configurations: `scripts/train_models.py` and `results/model_comparison.json`. Installed-version defaults are fixed by `requirements-ml.txt`.

## 9. Metrics and meanings

- **Candidate binary macro F1:** F1 for match and nonmatch classes, averaged equally. Used for model selection/tuning on grouped CV. Not an observation-ranking metric.
- **Observation Top-1 agreement:** choose highest-scoring candidate, compare its arc with the surrogate arc. Candidate misses count as wrong.
- **Observation arc macro F1:** macro F1 over `(trip ID, arc ID)` classes; trip namespacing prevents unrelated local IDs being merged. Equal arc-class weighting differs from Top-1's observation weighting.
- **Candidate miss rate:** fraction of observations missing the surrogate road from their candidate set.
- **Binary log loss:** independent candidate 0/1 probability loss.
- **Conditional candidate log loss:** normalise candidate scores per observation and take negative log probability of the surrogate road only when present. Excludes misses, so report miss rate beside it. Not comparable as the same quantity to binary log loss.
- **Precision/recall diagnostics:** candidate-binary macro averages; threshold `positive_probability >= 0.5` matches recorded original test diagnostics. Estimator `predict()` can break exact 0.5 ties differently; CV consistently uses estimator `predict()`.

Scoring clips positive probabilities to at least 1e-9 and normalises within each observation. These are relative decoder scores, not established calibrated posteriors over mutually exclusive roads.

Training time includes three CV fits plus final fit. Scoring time includes flattening/evaluation, excludes candidate generation, reference alignment, HMM, API/network time. It is not end-to-end latency.

## 10. Actual results and selection

Source: `results/model_comparison.json`; [comparison plot](../outputs/evaluation_1130/02_model_comparison.png). All sampled student-test results below use surrogate labels, 2,000 observations and 0.2% candidate miss rate (four observations).

- Logistic: mean CV binary macro F1 **0.87972**; Top-1 **85.15%**; arc macro F1 **0.75773**; conditional log loss **0.60358**.
- Gaussian NB: CV **0.78825**; Top-1 **84.10%**; arc F1 **0.75800**; conditional loss **0.88076**.
- Decision Tree: CV **0.89562**; Top-1 **85.45%**; arc F1 **0.76321**; conditional loss **0.65997**.
- Random Forest: CV **0.90113**; Top-1 **85.55%**; arc F1 **0.77863**; conditional loss **0.41379**.
- Histogram Gradient Boosting: CV **0.90158**; Top-1 **85.85%**; arc F1 **0.78276**; conditional loss **0.39682**.

Boosting was selected by grouped-CV binary macro F1, not training accuracy. Its margin over Random Forest is small; statistical significance was not established.

Recorded training-including-CV seconds: approximately 0.11, 0.05, 1.36, 5.98 and 1.00 respectively. Sampled test scoring: roughly 0.019–0.033 seconds. Timings are machine/run-specific and exclude most of the pipeline.

### Additional fit diagnostics

Source: [model diagnostics CSV](../outputs/evaluation_1130/model_diagnostics.csv). All values are candidate-binary macro metrics.

- Logistic: train F1 0.88143, test F1 0.89479; test precision 0.90020, recall 0.88960.
- Gaussian NB: train 0.78711, test 0.78614; precision 0.74855, recall 0.87845.
- Decision Tree: train 0.90886, test 0.91103; precision 0.91685, recall 0.90545.
- Random Forest: train 0.93136, test 0.91214; precision 0.91986, recall 0.90482.
- Histogram boosting: train 0.90787, test 0.91595; precision 0.92090, recall 0.91117.
- Tuned boosting: train 0.91183, test 0.91558; precision 0.91860, recall 0.91263.

Random Forest shows some training optimism. Gaussian NB's similarly low training/test fit is consistent with limited fit under its assumptions. Small/reversed gaps elsewhere do not prove absence of overfitting: trip difficulty and approximate labels limit conclusions. No artificial epoch curves were generated.

## 11. Bayesian tuning

Optuna TPE maximised mean three-fold trip-grouped candidate-binary macro F1 using training data only. Twelve recorded trials. TPE starts with random exploration: default ten startup trials here, so the final two were model-guided.

Search: learning rate 0.02–0.3 (log scale); leaf nodes 7–31 (integer); L2 regularisation 0.0001–10 (log scale). These control boosting step size, tree complexity and regularisation.

Best parameters: learning rate **0.1360140223**, leaf nodes **27**, L2 **1.4867578983**. Refit on permitted training data.

Baseline → tuned:

- CV binary macro F1: 0.90158 → 0.90252.
- Student-test Top-1: 85.85% → 85.70%.
- Student-test arc macro F1: 0.78276 → 0.78198.
- Conditional candidate log loss: 0.39682 → 0.39275.
- Scoring seconds: approximately 0.02682 → 0.02807. Tuned fit alone ~0.323s, not comparable to baseline time including CV.

Mixed outcome: CV objective and conditional loss improved slightly; held-out pointwise metrics declined slightly. Tuned model is the development handoff based on the declared CV objective. Both artifacts retained. Evidence: `results/tuning_trials.json` and `results/tuning.sqlite3`.

Rerunning `--trials 12` adds twelve trials to the compatible existing study; it does not merely display old trials.

## 12. Maps and three investigated findings

`scripts/inspect_maps.py` scores every GPS point in three selected student-test trips:

- `00000052` (shortest): 262 points; surrogate agreement 95.04%; ambiguity 19.08%; zero misses.
- `00000056` (longest): 3,958 points; agreement 80.92%; ambiguity 41.61%; six misses.
- `00000065` (highest recorded ambiguity among remaining trips): 768 points; agreement 79.95%; ambiguity 41.80%; one miss.

Total 4,988 points. This is not full evaluation across all ten student-test trips, and its percentages must not replace the sampled comparison.

Blue points: GPS. Green: supplied reference segments. Orange: independent classifier choices, before HMM. Optional layers flag disagreements, ambiguity and missing candidates. We do not fabricate connecting lines between disconnected classifier selections.

Codex inspected static trip images and [three close-ups](../outputs/evaluation_1130/04_disagreement_closeups.png) while Nikhil was unavailable:

1. **Trip 52 / observation 4:** classifier arc 2407 versus surrogate 1680, reference offset ~11.18m. Reference is present, so this is a scoring disagreement. A short nearby segment competes with the reference road; whether HMM helps needs measurement.
2. **Trip 56 / observation 214:** reference arc 13975 (~12.24m) is absent from eight candidates. An all-road distance check finds seven strictly closer arcs and two tied at the reference distance. The cutoff can omit one; the reference label is also flagged ambiguous.
3. **Trip 65 / observation 267:** reference arc 1426 (~21.79m) has nine strictly closer arcs and is excluded by the eight-road cap. This is a candidate-budget limitation, not solely a classifier mistake. Distances vary slightly with projection origin.

These are measured geometric findings, not verification of physical ground truth or Nikhil's personal review. Source CSVs preserve point indices and timestamps.

## 13. Code, evidence and commands

Source files:

- `pathsnap/data.py`: inference trip and separate reference loading.
- `pathsnap/features/candidates.py`: geometry/candidates/features.
- `pathsnap/features/reference.py`: surrogate alignment/ambiguity.
- `pathsnap/models/predict.py`: artifact/schema loading and scoring.
- `scripts/import_dataset.py`, `scripts/inventory.py`: local raw import and inventory.
- `scripts/train_models.py`: model fitting, grouped CV, tuning/export.
- `scripts/inspect_maps.py`: Folium maps, full-trip CSVs and summary.
- `scripts/prepare_evaluation.py`: all-trip audit, diagnostics, seven PNGs and evidence index.

Evidence: `outputs/evaluation_1130/`, `outputs/inspection/`, `results/`. Selected artifacts: `artifacts/models/hist_gradient_boosting/model.joblib` and `artifacts/models/tuned/model.joblib`. Other baseline artifacts stay local and are reproducible by training. Raw data, virtual environments, feature caches and secrets remain excluded.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-ml.txt
python -m pip install folium==1.0.0 matplotlib==3.11.2
python scripts/import_dataset.py '/path/to/Student folder.zip'
python scripts/inventory.py
python scripts/train_models.py --max-observations 200 --trials 12
python scripts/inspect_maps.py
python scripts/prepare_evaluation.py
```

Import into a fresh destination: existing files are refused. Training/tuning changes result files and adds trials to a compatible study. To inspect already published charts/maps, no training is needed. Regenerating the full evidence pack needs the feature cache, all five baseline artifacts and recorded tuning results; the two published inference artifacts alone do not suffice.

Initial ML environment: Python 3.14, NumPy 2.5.5, SciPy 1.18.1, scikit-learn 1.9.1, joblib 1.6.0, Optuna 5.1.0. Use compatible pinned library versions when loading artifacts on another machine.

```python
from pathsnap.data import load_trip
from pathsnap.features.candidates import generate_candidates
from pathsnap.models.predict import score_candidates

trip = load_trip('data/student_test/00000052')
candidates = generate_candidates(trip)
scores = score_candidates(trip, candidates, 'artifacts/models/tuned')
# scores[i][j] belongs to candidates[i][j]. No reference loaded.
```

Artifact loading checks feature-name order and caches by directory path. Restart/clear the cache if replacing a model at the same path. Candidate scores preserve original observation order.

PNG files open directly in Preview or an editor image viewer. Interactive HTML must open in Safari/Chrome using Finder → Open With; a code editor displays HTML source. Folium external JavaScript/styles/street tiles require internet. Static PNGs work offline but are not screenshots of browser-rendered Folium.

## 14. Verification and remaining work

Completed checks: synthetic parallel-road geometry; finite features and ordering; full 262-point trip scoring with baseline/tuned artifacts; finite/normalised scores; Folium layer content and CSV row counts; static trip/close-up visual inspection; chart layout review; 90 audit rows/227,577 point reconciliation; seven readable PNGs; Python syntax and Git whitespace checks.

Not established here: interactive Folium browser rendering, independently verified point labels, full-data retraining, official alignment clarification, HMM improvement, route continuity/sequence metrics, backend/UI/network integration, final report, final evaluation/submission or team rehearsal. Preserve that distinction in the viva.

## 15. Viva questions with answers

**1. What is our problem?** Recover likely road segments from noisy GPS, then use a sequential decoder to produce a plausible route. Our verified work covers data, classifier and evidence; decoder integration is separate.

**2. Why not pick the nearest road?** Noise can favour a side or parallel road. Direction and temporal neighbours provide additional evidence. Trip 52 point 4 illustrates competing nearby segments.

**3. Where did all the data go?** Nowhere: all 227,577 observations remain under `data/`. We sampled only for the initial experiment; the audit checks all trips.

**4. What is the inventory CSV?** A list of files, sizes and row counts, not raw GPS or training features.

**5. Why not classify universal arc IDs?** IDs are trip-local. We learn match/nonmatch suitability from general geometry and motion features.

**6. How did you obtain labels?** Choose the nearest supplied reference-route segment per observation, then label matching candidates 1 and other candidates 0. These are surrogate labels.

**7. Why not pair route and GPS rows directly?** Route rows are traversed segments; GPS rows are timestamped observations. One road can cover many GPS points; lengths/meanings differ.

**8. What is the biggest limitation?** Reference alignment ignores chronological route progress and can be uncertain at loops/junctions. Accuracy therefore cannot be treated as verified physical truth.

**9. Why project coordinates?** Degrees are angles, and longitude scale varies by latitude. Local metres support meaningful distance thresholds, within a regional approximation.

**10. Why sample road segments?** Midpoint-only lookup can overlook a long road's nearby endpoint. Sampling supplies a spatial index, followed by segment-distance calculation.

**11. Why eight candidates and 100m?** Practical initial cost/coverage choices, not proven optima. Measured candidate misses expose their limits. Any improvement must be general and evaluated reproducibly.

**12. What happens outside the radius?** Retain the nearest retrieved candidate as fallback, with no claim it is certain. Gap/poor-candidate handling belongs in decoder policy too.

**13. Is it real time?** Current features use the following observation, so it is offline. Strictly causal deployment needs changed features, training and evaluation.

**14. How is leakage avoided?** Group whole trips in CV, fit scalers within folds, separate reference loading from inference, and never use evaluator data for selection/tuning.

**15. Why these five models?** They test linear, probabilistic, single-tree, bagged-tree and boosted-tree approaches on identical features and splits.

**16. Why select histogram boosting?** Highest mean grouped-CV binary macro F1: 0.90158 versus Random Forest's 0.90113. The margin is small, and significance was not tested.

**17. Why macro F1?** Candidate negatives usually outnumber positives. Averaging both class F1 scores avoids a simple accuracy score being dominated by negatives. Ranking still needs Top-1 evaluation.

**18. Why two kinds of F1?** Binary F1 evaluates candidate match/nonmatch; arc macro F1 evaluates selected road classes per observation. They have different label spaces and weighting.

**19. What is a candidate miss?** The surrogate reference road is absent from candidates. Sampled test miss rate is 0.2%, four of 2,000 points. A classifier cannot choose an absent candidate.

**20. Are the scores calibrated probabilities?** We normalise independent binary positive scores across candidates. They are relative decoder inputs; calibration as mutually exclusive road probabilities was not demonstrated.

**21. Why log loss?** It penalises low probability assigned to the labelled outcome, especially confident mistakes. Conditional candidate loss excludes misses and must be read with miss rate; binary loss is separate.

**22. Did models overfit?** Forest train F1 ~0.931 versus test ~0.912 suggests some optimism. NB is similarly low on both (~0.787/~0.786). Trip difficulty/label uncertainty limit stronger claims.

**23. What is Bayesian tuning here?** Optuna TPE searches settings using grouped training CV; after initial random exploration, it uses previous trial results to guide suggestions.

**24. Which hyperparameters and why?** Learning rate controls boosting step size; leaf nodes control tree complexity; L2 regularisation penalises complexity. Ranges and trials are saved.

**25. Did tuning improve everything?** No. CV F1 and conditional loss improved slightly; test Top-1 fell from 85.85% to 85.70%. Report the mixed result.

**26. Are twelve trials enough?** A bounded initial hackathon search, not exhaustive optimisation. Default ten startup trials mean only the last two were TPE-guided. More permitted validation experiments could follow.

**27. Why is NB weaker?** Its measured CV F1 is lowest and conditional loss highest. Correlated distance features make independence questionable; that is a plausible explanation, not proven causality.

**28. What did map inspection reveal?** One scoring disagreement with the reference available and two candidate misses explained by top-eight cutoff/ties. Exact points and close-ups are documented above.

**29. Why care about gaps?** Intermediate movement is unknown. A 153,064-second gap makes ordinary short-step continuity assumptions inappropriate; decoder resets/penalties require explicit design.

**30. Does a disconnected graph invalidate the trip?** Not necessarily. The relevant route might lie in one component. Reachability between selected candidates must be checked, especially with directed arcs.

**31. What about zero-length arcs?** They provide no meaningful heading. Denominator floors prevent numerical failures, but an explicit decoder policy is still needed; silently deleting reference IDs would be unsafe for correspondence.

**32. What are HMM states, emissions and transitions?** Intended states are candidate roads/positions; observations are GPS/model evidence. Emissions express observation compatibility; transitions express plausible graph movement. Exact implementation must be confirmed with Nakul.

**33. What does Viterbi do?** Finds the highest-scoring state sequence by dynamic programming. In log space: `V[t,j] = log emission[t,j] + max_i(V[t-1,i] + log transition[i,j])`, then backtrack. This is design knowledge, not a claim our decoder was verified.

**34. Did HMM improve accuracy?** We cannot claim that yet. Compare classifier-only and decoded results on the same permitted observations, with pointwise and route metrics.

**35. What checks did you run?** Synthetic geometry, saved full-trip scoring, score/feature/order validation, map/CSV checks, all-trip audit, static image inspection and reproducibility checks. API/network checks are separate.

**36. How can someone reproduce this?** Install pinned dependencies, import the ZIP, run the scripts above. Preserve configurations, seeds, fold trip IDs, labels, cache version and trial history.

**37. What does the backend receive?** Inference trip, nested candidate dictionaries and identically ordered scores. Saved artifacts include feature names and label methodology. No reference labels enter scoring.

**38. Why do map percentages differ from model results?** Maps score all points in three trips; the initial comparison samples 200 points from each of ten trips. Different populations give different percentages.

**39. What is still pending?** Official alignment clarification, receiving-machine handoff, HMM/API/UI integration, route metrics, network demo, final report/submission and team rehearsal. The checklist tracks verified evidence.

**40. Did AI assist?** Yes: Codex assisted coding, checks, image inspection and notes. The team must review and understand the work and disclose assistance as required. Nikhil was unavailable for the latest analysis, so do not claim he personally conducted it.

## 16. Team handoff before 11:30

Lakshya: explain features, surrogate labels, grouped CV and selection. Nikhil: review the audit and three findings in his own words. Mahesh: use actual charts/results in the report. Nakul: confirm model loading, candidate correspondence and decoder/API progress. The evidence guide supports preparation; it does not replace personal understanding.
