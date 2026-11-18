# PathSnap team checklist — shared master copy

Planning baseline: 18 November 2026, 10:36 AM IST.
First evaluation: 11:30 AM. Submission and final evaluation: 3:00 PM.
Form closes 4:30 PM; event ends 5:00 PM. Plan to submit by 3:00 PM.

This shared checklist lives in `docs/TEAM_CHECKLIST.md`. Lakshya coordinates updates; teammates report completed task IDs with evidence. Publishing this checklist does not mark any project submission task complete.

## How to use this checklist

- `[x]` means completed with local evidence or confirmed by its owner. `[ ]` means pending or not yet verified, not necessarily that nobody has started it.
- IDs identify tasks. An item mentioning “after X” waits for X; other items in the same time block can run in parallel.
- Lakshya maintains this master copy. Report “ID done + evidence” or “ID blocked + reason”. Add actual completion time when checking an item.
- Codex updates this file during our work and when teammate progress is reported. It cannot observe other laptops automatically. No background monitoring is configured.
- At each checkpoint, each member reports: completed IDs, next ID, blocker. If blocked for 10 minutes, bring the blocker to Lakshya rather than silently waiting.
- Code existing on one machine is not integration complete. Test the receiving component before closing a handoff.
- Keep scope simple until the complete two-laptop flow works. Changes to candidates, feature order, model artifacts or API fields require a coordinated handoff.

## Owners and machines

- **L — Lakshya + Codex:** data loader, candidate generation, reference alignment, features, models, tuning, artifact handoff and ML explanations.
- **N — Nakul + Claude Code:** graph routing, HMM/Viterbi, FastAPI, server-side evaluation and backend integration.
- **D — Nikhil (Member 3):** data checks, experiment verification, EDA, plots, development maps and failure analysis. Pair with L for scripts when needed.
- **U — Mahesh (Member 4):** evaluator UI, report assembly, screenshots, network testing, submission coordination. Pair with N for UI coding when needed.
- **Laptop 1:** model/API host. Owner and physical laptop: TO CONFIRM in S1.
- **Laptop 2:** UI host. Owner and physical laptop: TO CONFIRM in S1.

## Already completed — initial ML work

- [x] C1 — L: imported 360 development data files locally; inventory confirms 80 training trips and 10 student-test trips. Evidence: `results/data_inventory.csv`, `data/`.
- [x] C2 — L: separate inference trip loading from reference-route loading. Evidence: `pathsnap/data.py`.
- [x] C3 — L: implemented nearby-road candidates and nine numerical features. Evidence: `pathsnap/features/candidates.py`.
- [x] C4 — L: implemented initial nearest-reference-geometry surrogate labels; documented limitations. Evidence: `pathsnap/features/reference.py`, `docs/ML_NOTES.md`. Visual validation remains pending in D4.
- [x] C5 — L: trained Logistic Regression, Gaussian NB, Decision Tree, Random Forest and Histogram Gradient Boosting using up to 200 observations per trip.
- [x] C6 — L: compared models with three folds grouped by trip; retained fold trip IDs and seed. Evidence: `results/model_comparison.json`.
- [x] C7 — L: evaluated all five on 2,000 sampled student-test observations, including candidate miss rate and explicitly named log losses.
- [x] C8 — L: ran 12 Bayesian TPE trials on the selected model. Evidence: `results/tuning_trials.json`, `results/tuning.sqlite3`.
- [x] C9 — L: saved baseline and tuned Histogram Gradient Boosting artifacts and ML dependency versions. Evidence: `artifacts/models/`, `requirements-ml.txt`.
- [x] C10 — L: tested saved-model scoring on complete 262-point trip 00000052: aligned lengths/order, finite scores, sums equal to one. This was model-interface testing, not HMM/API integration.
- [x] C11 — L: documented methods, sampling, metric definitions and tuning outcome in `docs/ML_NOTES.md`; shared interfaces in `docs/CONTRACT.md`.

Current evidence: baseline Top-1 85.85%; tuned 85.70%; candidate miss rate 0.2%, on sampled student-test observations and surrogate labels. Tuned grouped-CV binary macro F1 improved from 0.90158 to 0.90252. These are not final route metrics or independently verified pointwise ground truth.

## Start now: 10:36–10:45 — remove coordination blockers

- [ ] S1 — ALL: assign physical Laptop 1 and Laptop 2; record IP, OS, Python version, owners and network below. Done when everyone knows which machines will demonstrate.
- [ ] S2 — N: confirm receipt of current candidate/model code and both artifacts on Laptop 1; install compatible dependencies. Confirm feature schema and model loading work on that machine.
- [ ] S3 — L + N: read `docs/CONTRACT.md` together; agree on candidate scores, decoder output, coordinate order, units and API fields. Record any agreed changes.
- [ ] S4 — N + U: start real `/health` endpoint on Laptop 1, bound to `0.0.0.0:8000`; call it from Laptop 2 over the actual network. Save response and IP. Depends on S1, not on a completed decoder.
- [ ] S5 — U: create report outline with required sections; reserve places for measured figures and UI/API evidence. Start assembling existing results immediately.
- [ ] S6 — L: confirm whether professor provides an official observation-label alignment/evaluation method. If none, explicitly justify the team's surrogate method; record answer/assumption before interpreting pointwise accuracy.

Machine record:

- Laptop 1 / owner / OS / Python: pending
- Laptop 1 LAN IP and API base URL: pending
- Laptop 2 / owner / OS / Python: pending
- Shared network / backup hotspot: pending
- Agreed model artifact path/version: pending

## 10:45–11:10 — evidence for the first evaluation

These lanes run concurrently. Within each lane, follow the listed order.

### Data lane — D with L

- [x] D1 — D/L: audited all 90 development trips for column counts, finite values, coordinate ranges, timestamp order/duplicates/gaps and observation counts. Evidence: `outputs/evaluation_1130/trip_audit.csv`, `data_summary.json`; generated by L with Codex for Nikhil's review.
- [x] D2 — D/L: audited graph sizes, weak components, isolated nodes, node/route ID validity, zero-length arcs and directed reference transitions. Findings and assumptions in `outputs/evaluation_1130/READ_FIRST.md`.
- [x] D3 — D + L: generated Folium development maps for short trip 00000052, long trip 00000056, and ambiguous trip 00000065 (also contains a 210-second GPS gap). Includes GPS, road network, reference and classifier layers. Evidence: `scripts/inspect_maps.py`, `outputs/inspection/index.html`, `outputs/inspection/summary.json`. HTML content and CSV counts checked; browser review remains D4.
- [x] D4 — L/Codex: inspected three full-trip static map images and three close-ups; recorded points 52/4, 56/214 and 65/267 with measured arc comparisons. Also checked directed reference adjacency across all trips. Evidence: `outputs/evaluation_1130/READ_FIRST.md`, `04_disagreement_closeups.png`, `disagreement_details.json`. Nikhil has not yet personally reviewed; geometric labels remain approximate, including route-order ambiguity.
- [x] D5 — L: retain existing reproducible baseline for first evaluation; document surrogate/order ambiguity and top-eight candidate limitations. No feature/label changes or retraining made. Future general changes require cache invalidation and rerunning experiments; no manual test-answer corrections.

### Model explanation lane — L

- [x] M1 — L: plain-language feature/label/metric explanation in `outputs/evaluation_1130/READ_FIRST.md`; personal understanding still requires reading/rehearsal.
- [x] M2 — L/D: actual CV, student-test Top-1/arc F1, conditional log loss and tuning plots in `outputs/evaluation_1130/`; source definitions and sampling labelled.
- [x] M3 — L/D: additional train/test binary F1 and test macro precision/recall saved in `model_diagnostics.csv`; configuration/timing evidence retained in original results; interpretation in READ_FIRST. No artificial epoch curves.
- [ ] M4 — L: audit the pinned environment/setup instructions on the model host. Document scoring time separately from candidate generation and end-to-end API latency.

### Decoder lane — N

- [ ] H1 — N: build graph connectivity and distance/routing helpers from trip-local nodes/arcs. Confirm directed/undirected interpretation from data and document it.
- [ ] H2 — N: implement HMM hidden states as candidate road segments, emissions from classifier scores, and transitions based on reachable road paths and observed motion. Explain probabilities and assumptions.
- [ ] H3 — N: implement Viterbi with stable log scores, backtracking, preserved candidate/arc correspondence, one output per original observation, and explicit warnings/gap policy. After H1–H2.

### Interface/report lane — U with N

- [ ] U1 — U + N: build simple trip selector, run button, status/errors, predicted-route map and metric display using the agreed response format. UI shell can precede a working prediction endpoint.
- [ ] U2 — U: add verified dataset/ML results and explanations to report draft. Include every model actually tried, model choice, configuration/objective, results and limitations.
- [ ] U3 — U: collect first-evaluation evidence in one folder: inventory, EDA plots, feature explanation, five-model comparison and executable command list. After D1 and M1–M2.

## 11:10–11:30 — first-evaluation gate

- [x] E1 — L/D: local evidence pack assembled at `outputs/evaluation_1130/` with all-trip audit, EDA, model/tuning plots, map images and simple explanations. Sampled model evaluation and surrogate labels clearly identified. Team rehearsal remains E2.
- [ ] E2 — ALL: rehearse a five-minute explanation. L explains labels/features; D explains EDA and model evidence; N explains route reconstruction design; U opens the evidence and records feedback.
- [ ] E3 — L: verify scripts/results open locally and models can be loaded; have screenshots ready if network access fails.
- [ ] E4 — ALL: attend 11:30 evaluation; U records professor feedback, required changes and marks-related omissions here. No completion inferred from the clock.

First-evaluation feedback: pending.

## 11:30–12:15 — integrate classifier, decoder and API

- [ ] H4 — N + L: test a synthetic connected route, impossible transition, missing candidate, repeated point, GPS gap and disconnected graph. Check output arc IDs and geometry are valid. After H3.
- [ ] H5 — N + L: pass actual candidate scores through decoder on at least one full student-test trip. Preserve original point indices and count. After S2, H4.
- [ ] A1 — N: implement `/trips` and `/predict`; use configured allowed trip IDs, actual prediction pipeline, appropriate errors and model-loading logic. After H5 for complete inference.
- [ ] A2 — N + L: add server-side evaluation, separated from prediction. Keep reference labels/routes out of model features and evaluator UI response. Record alignment method and metric definitions.
- [ ] A3 — N: construct road-following geometry from valid graph arcs, retaining disconnected pieces as separate lines; no invented straight connections across gaps.
- [ ] A4 — N: log trip ID, actual request, processing outcome and timings on the receiving laptop; verify errors for unknown trip and missing assets.
- [ ] U4 — U + N: connect UI to the actual API and show returned route, measured metrics, runtime and useful errors. After A1–A3.
- [ ] G1 — ALL: one complete student-test trip works from Laptop 2 through Laptop 1 to displayed prediction. After S4, A4, U4. Capture evidence.

## 12:15–1:00 — evaluate the reconstructed routes

- [ ] V1 — N + D: run classifier-only and classifier-plus-HMM on all ten student-test trips with the same observations and labels. Save per-trip and aggregate outputs.
- [ ] V2 — N + L: define and measure route continuity and sequence performance (for example, documented route-sequence overlap/edit measure). Avoid an undefined “continuity” score. Include timing and failures.
- [ ] V3 — D: compare where decoding helps, hurts or fails using maps, metrics and concrete trip examples. After V1–V2.
- [ ] V4 — L: review whether 200 points per trip is sufficient; if time allows, run a versioned larger-data experiment and full student-test evaluation. Clearly distinguish initial sampled and later full-trip results; preserve both.
- [ ] V5 — L + N: freeze the development model, feature schema and decoder configuration using permitted development evidence. Record artifact/version and all selected parameters. Retrain after feature/label changes before freezing.
- [ ] V6 — N + U: verify full development UI/API flow across all ten student-test trips, including slow/long trips; measure complete latency. No cached hardcoded predictions as substitutes for inference.
- [ ] G2 — ALL: confirm all development trips work and the two machines can restart and reconnect. After V5–V6.

Evaluator partition: do not train, tune, choose thresholds, or develop against evaluator trips/results. When organisers release/authorise final evaluation, configure its ten trips on the server; reserve labels for scoring only. If released earlier, keep them untouched during development.

## 1:00–2:00 — complete report and reproducibility

- [ ] R1 — U + D: finish dataset/preprocessing section with partition names, missing-value analysis, GPS plots, road graphs, feature justification and at least one Folium map view.
- [ ] R2 — U + L: finish all five model subsections: suitability, strengths/limitations, actual configuration/hyperparameters, objective, student-test metrics, and evidence of over/underfitting. Include all additional models actually attempted.
- [ ] R3 — U + L: finish consolidated model comparison and plots; use N/A with reasons when a metric does not apply. Include observation Top-1, macro F1, log loss with definitions, CV, route continuity and inference time as applicable.
- [ ] R4 — U + L: tuning section includes search ranges, objective, fold grouping, 12 recorded trials (plus any later trials), best configuration and measured tuned-versus-untuned comparison, including mixed outcomes.
- [ ] R5 — U + N: HMM section explains hidden states, emissions, transitions, Viterbi, missing candidates, GPS gaps/disconnections and classifier-only versus decoded metrics/maps.
- [ ] R6 — U: add final Folium screenshot with clear layers/legend and ensure interactive HTML or reproducible generation code is included. Reference-route layers belong in development analysis, not evaluator UI.
- [ ] R7 — U + N: capture working UI and actual successful API requests/logs on Laptop 1. Include screenshots in deployment/report section.
- [ ] R8 — L + N: document exact install/start commands, model/config paths, network URL, supported Python/package versions and required local dataset layout. Check README matches final implementation.
- [ ] R9 — ALL: verify each reported metric/figure traces to an actual result file and code. Remove placeholder/fabricated claims. Describe AI assistance accurately if required by event policy.
- [ ] R10 — U: export one consolidated report PDF; open it and inspect every page for clipped plots, missing figures, illegible labels and broken tables.

## 2:00–2:30 — freeze and rehearsal

- [ ] F1 — ALL: stop new features; fix only correctness, integration and submission blockers. Record final code/model/config versions.
- [ ] F2 — N + U: restart API and UI from documented commands; model loading and network access succeed without relying on a notebook's hidden state.
- [ ] F3 — N + U: rehearse selecting arbitrary development trips; show actual inference request reaching Laptop 1 and predicted route/results returning to Laptop 2.
- [ ] F4 — L + D: verify final results, saved artifacts, tuning history, source code, Folium code/HTML and dependencies are present. Ensure backend loads the intended final artifact.
- [ ] F5 — ALL: practise viva explanations of data, features, all models, tuning, HMM/Viterbi and distributed setup. Each person can explain the complete pipeline and their own implementation.
- [ ] F6 — U: prepare chargers, stable network and backup hotspot; record IP/base URL and keep both machines awake for demo.

## 2:30–3:00 — submission and final evaluation

These are future tasks. Publishing the checklist does not authorise final submission or mark final source/results as reviewed. Coordinate final publication with the team.

- [ ] Q1 — L + U: perform final repository review for secrets, missing source, stale model/config paths and mismatched demo code; confirm permission to publish final project updates.
- [ ] Q2 — L: when authorised, publish all required source/results/artifacts to the final GitHub repository and verify evaluator access/public visibility. Keep the shared checklist current.
- [ ] Q3 — U: verify Google Form requirements and exact links/files; open final PDF and repository from the submission location. Do not assume the existing repo is publicly accessible.
- [ ] Q4 — U + L: submit the repository and consolidated PDF through the form by 3:00 PM; verify receipt/confirmation and save evidence.
- [ ] Q5 — N + U: on authorised final evaluation only, expose the ten reserved trip choices and process any selected trip through the complete pipeline. Compute metrics server-side; keep reference labels/routes private to evaluation.
- [ ] Q6 — ALL: complete final demonstration, show receiving-laptop API logs and answer technical questions. U records evaluator feedback.
- [ ] Q7 — U: verify submission receipt/links once more. Use the period before the 4:30 PM form closure only for permitted corrections; event ends at 5:00 PM.

## Handoffs — close these only after receiver verification

- [ ] X1 — L → N: candidate schema, scoring function, model artifact and dependencies; N loads and scores on Laptop 1. Evidence: receiving-machine output. Related S2–S3.
- [ ] X2 — L → D/U: measured model results, plots, feature explanation and surrogate-label caveat; D/U confirm figures and report wording match evidence.
- [ ] X3 — N → U: actual endpoint/base URL, request/response and error examples; U calls from Laptop 2. Related U4/G1.
- [ ] X4 — N/D → U: classifier/HMM comparison, continuity/sequence metrics, maps and timings; U incorporates verified final results.
- [ ] X5 — ALL → U: final source/artifact inventory, deployment screenshots and viva explanations; U verifies complete report/submission package.

## Status log

- 10:36 AM planning baseline: C1–C11 complete based on local files and prior execution. Visual label validation, full EDA, plots, HMM, API, UI, network demo, report and submission remain unverified. Teammate work on other laptops has not been inspected.
- Subsequent map-generation session: D3 complete; 4,988 full-trip points scored across three selected student-test trips. D4 remains pending human review. Simple notes: `docs/WORK_LOG_SIMPLE.md`. Member names confirmed: Nikhil (D), Mahesh (U).
- Approximately 11:10 AM: local all-trip audit, static image inspection, three documented findings, model diagnostics and first-evaluation evidence pack completed by L/Codex while Nikhil unavailable. D1/D2/D4/D5/M1/M2/M3/E1 closed with evidence. Nikhil's personal review, official alignment clarification, teammate integration, rehearsal and final deployment remain unverified. No pushes.

## Next four actions

1. L + D: D3–D4 — create development maps and inspect surrogate alignment; L handles script gaps while D records findings.
2. N: S2–S4 — confirm model loading and start reachable health endpoint; then H1–H3.
3. D: D1–D2 — finish data-quality/connectivity evidence while map generation is prepared.
4. U: S1/S5 — confirm demo machines/network, start report, and test health endpoint with N as soon as available.
