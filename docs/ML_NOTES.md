# ML implementation and limitations

## First completed experiment

80 training trips, 10 student-test trips, up to 200 observations per trip, seed 42, three trip-grouped folds. Student-test evaluation contains 2,000 observations. All values below use the surrogate alignment described below.

- Logistic Regression: Top-1 0.8515; observation arc macro F1 0.7577.
- Gaussian Naive Bayes: Top-1 0.8410; observation arc macro F1 0.7580.
- Decision Tree: Top-1 0.8545; observation arc macro F1 0.7632.
- Random Forest: Top-1 0.8555; observation arc macro F1 0.7786.
- Histogram Gradient Boosting: Top-1 0.8585; observation arc macro F1 0.7828.

Histogram Gradient Boosting was selected by mean grouped-CV candidate-binary macro F1 (0.90158). Twelve TPE trials improved that CV objective to 0.90252. Student-test Top-1 declined slightly to 0.8570 and arc macro F1 to 0.7820; tuning did not improve these held-out pointwise metrics. Conditional candidate log loss improved from 0.39682 to 0.39275. Candidate miss rate was 0.002. Both baseline and tuned artifacts are retained. The tuned artifact is the development handoff based on the predeclared CV selection objective.

Full logs, exact values, trip splits and configurations are in `results/model_comparison.json`; trial history is in `results/tuning_trials.json` and the Optuna SQLite database. These are initial experiments, not final HMM or end-to-end performance.

## Run

Use the project virtual environment. Initial model comparison:

```bash
.venv/bin/python scripts/train_models.py --max-observations 200
```

Then run Bayesian optimisation (reuses local feature cache):

```bash
.venv/bin/python scripts/train_models.py --max-observations 200 --trials 12
```

This trains all five models with three trip-grouped folds. The initial experiment samples at most 200 equally spaced observations per trip; candidate features retain original temporal neighbours. Increase the cap for a larger follow-up experiment. This is offline matching: the next observation is available and used in heading/distance features.

## Candidate generation

Project locally to metres using the first observation as origin and a latitude-adjusted longitude scale. This is a local approximation, not an exact geodesic projection. Sample every road segment at intervals no greater than 30 metres, query 128 nearby samples with a KD-tree, deduplicate arc IDs and measure exact point-to-segment distances for the retrieved arcs. Keep up to eight candidates within 100 metres. If none is within 100 metres, keep the nearest retrieved candidate. The search is approximate: 128 samples can omit plausible segments in dense areas. Measure candidate miss rate.

Features: observation-to-segment distance; signed and absolute heading cosine; segment length; projection fraction; local speed; previous/next observation distances to the same segment; distance rank. Raw arc IDs and reference-route membership are excluded from features.

## Reference alignment

Each observation receives the geometrically nearest arc in the supplied reference route. This is a surrogate alignment, not independently verified observation ground truth. It ignores chronological order in loops and can confuse parallel/oppositely directed overlapping segments. Record the fraction of observations with multiple distinct reference arcs within two metres of the best distance. Do not describe surrogate-based metrics as verified physical accuracy. Improve alignment and inspect maps before drawing strong conclusions.

## Metrics

Selection and Bayesian tuning optimise candidate-binary macro F1 on three folds grouped by trip. Binary labels indicate whether a candidate matches the surrogate arc. This metric differs from observation-level arc macro F1. Student-test Top-1 accuracy and observation-level macro F1 include candidate misses; arc identities are namespaced by trip. Candidate log loss is conditional on the reference candidate being present and is explicitly named accordingly. Binary log loss measures a separate classification task. Do not compare these two log losses as equivalent.

Student-test metrics use the sampled observations, not every observation. Training time includes CV and final fit. Scoring time includes flattening/evaluation but excludes candidate generation and reference alignment; it is not end-to-end API latency.

The decoder team must add continuity/sequence metrics and compare classifier-only versus decoded predictions. Current training does not implement or claim those results.

## Backend handoff

```python
from pathsnap.data import load_trip
from pathsnap.features.candidates import generate_candidates
from pathsnap.models.predict import score_candidates

trip = load_trip('data/student_test/00000000')
candidates = generate_candidates(trip)
scores = score_candidates(trip, candidates, 'artifacts/models/random_forest')
```

Choose the model directory using `results/model_comparison.json`, not the example name above. Nested candidates and scores preserve original observation order. Model artifacts carry feature names and label methodology. Reference loading is separate from prediction.
