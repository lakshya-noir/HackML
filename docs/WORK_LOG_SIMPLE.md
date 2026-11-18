# What we did — plain-language revision notes

For Lakshya's preparation before the 11:30 AM evaluation, 18 November 2026.

## Earlier: our first model experiment

We loaded 80 training trips and 10 student-test trips. For each GPS point, our code finds nearby roads and describes each possible road using nine features such as distance, direction agreement and local speed. The model learns whether each candidate is a suitable match.

The reference route lists roads in order but does not give a road for each timestamp. Our initial labels use the closest road within the supplied reference route. These are approximate labels. Loops, intersections and opposite-direction roads can make the label uncertain.

We compared five models with validation splits that keep whole trips together. For speed, training/evaluation used up to 200 observations per trip. Histogram Gradient Boosting led the chosen cross-validation score. Its student-test agreement with approximate labels was 85.85%. Twelve Bayesian tuning trials slightly improved the validation objective but student-test agreement fell to 85.70%. We saved both models and the actual results. See `docs/ML_NOTES.md` for exact definitions.

## Current task: make the model's behaviour visible

We added `scripts/inspect_maps.py`. It selects the shortest student-test trip, the longest student-test trip, and a different trip with high recorded label ambiguity. This gives us small, large and potentially confusing examples rather than choosing only an easy-looking trip.

The script runs the saved tuned classifier on every GPS point in each selected trip. It generates interactive Folium maps and a CSV of point-level information. This is a new full-trip inspection; its numbers must not be mixed with the earlier sampled experiment.

On each map: blue points are noisy GPS measurements; green segments are the supplied reference route; orange segments are the classifier's selected roads. Optional layers highlight disagreements, ambiguous approximate labels, and cases where the approximate reference road was absent from the candidate list. Click a point to see its index and timestamp.

Orange roads are independent classifier selections. They have not been connected by HMM/Viterbi in this script. We draw each selected road segment separately so jumps are visible without inventing a route between them.

The script also measures irregular timestamps, reference offsets and label ambiguity. These numbers flag places to investigate; they do not establish that the reference or classifier is correct.

## What Nikhil and Lakshya must do together

Open `outputs/inspection/index.html` after running the script. Toggle the green/orange layers; then enable ambiguity/disagreement layers. Inspect junctions, loops and parallel roads. Nikhil records the trip, observation index, what looks questionable and a screenshot. Lakshya investigates whether a change is needed. Do not call visual validation complete until someone actually inspects the maps.

## Commands

```bash
.venv/bin/python -m pip install folium
.venv/bin/python scripts/inspect_maps.py
```

Map generation and human visual inspection are separate checklist tasks. Execution results and observations will be appended below as they become available.

## Completed in this work session: maps generated

The script successfully processed 4,988 GPS observations across these three full trips:

- Trip `00000052`: 262 points, 95.04% agreement with approximate labels, 19.08% ambiguous labels, no candidate misses.
- Trip `00000056`: 3,958 points, 80.92% agreement, 41.61% ambiguous labels, six candidate misses.
- Trip `00000065`: 768 points, 79.95% agreement, 41.80% ambiguous labels, one candidate miss.

“Ambiguous” means multiple distinct reference arcs are within two metres of the nearest reference arc's distance. It does not mean those points are necessarily wrong. Neighbouring segments at junctions and overlapping directed arcs can both cause this flag.

Trip `00000065` contains a 210-second timestamp gap. This is a concrete example to discuss with Nakul: a decoder must handle a long interval where we do not know the vehicle's intermediate movement. Drawing a straight line between GPS observations would not prove the vehicle followed that line.

The short trip has four gaps over one second; the long trip has 41; trip 65 has 11. None of these three trips has a nonpositive timestamp step. These are checks on the three inspected trips only, not yet an audit of all 90 trips.

Generated HTML layer content and audit CSV row counts/order were checked. The Python script passed syntax compilation. Actual map appearance and label correctness still require human browser inspection. External map JavaScript and street tiles require internet access.

Next: open the index with Nikhil, start with the short trip, then inspect candidate misses and the long gap on the other maps. Record findings in `outputs/inspection/HUMAN_FINDINGS.md`. No model, labels or training results were changed in this session.

## Next session: finished data audit and first-evaluation evidence

Because Nikhil was unavailable and the editor displayed raw HTML, we added `scripts/prepare_evaluation.py` to generate plain PNG images, numerical audit tables, model diagnostics and a readable handoff. The complete explanation is `outputs/evaluation_1130/READ_FIRST.md`.

We checked all 90 development trips, covering 227,577 GPS points. We found no nonfinite coordinates/timestamps or duplicate/non-increasing timestamps. We found 106 zero-length arcs, disconnected graph components in 89 trips, and 14 reference transitions whose directed endpoints do not meet. These are documented rather than silently changed. A training trip has a 153,064-second timestamp gap, much larger than the 210-second gap previously found in student testing.

We visually inspected generated images of all three trips and three specific disagreements. Two investigated candidate misses are explained by the eight-candidate cutoff: one involves tied-distance road segments and one has nine closer arcs. The third example is a model scoring disagreement even though the reference candidate is present. These are concrete examples for Nikhil to explain; they do not validate every label.

We retained the existing model/labels for the first evaluation and documented the limits. We generated actual EDA, model comparison and tuning charts, and measured additional candidate-level precision/recall and training-versus-test F1. We adjusted the diagnostics to use the same probability threshold as the original metrics, including exact 0.5 ties. No model retraining or GitHub push was performed in this session.

## Documentation and publication follow-up

Lakshya subsequently requested publishing these changes. We restructured `docs/ML_NOTES.md` into a complete implementation/results/revision guide with 40 viva questions and answers. The guide includes the measured audit, geometry, candidates/features, surrogate labels, grouped validation, model configurations/results, mixed tuning outcome, inspection findings, commands and remaining integration work. README links and pinned plotting/map dependencies were added. Only selected evidence directories are allowed through Git ignore rules; raw data, environments and feature caches remain excluded. The earlier no-push statement above describes the analysis session, before this later publication request.
