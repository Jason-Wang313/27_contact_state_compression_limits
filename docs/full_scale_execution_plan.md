# Paper27 Full-Scale Execution Plan

## Current Claim

The current paper argues that compressed contact state can destroy controllability when an alias class merges contact modes whose task-feasible action sets have empty intersection. The repair is contact-cone separating compression (CCSC): preserve enough action/task feasible-cone signature information to split aliases that have no common robust action.

The v2 paper is clear but small. It uses 64 contact modes, 180 action directions, 24 task directions, one deterministic contact generator, a handful of representation baselines, and a signature-budget stress test. The headline is strong in that setting: contact count succeeds on 0.720 of raw-controllable tasks while CCSC succeeds on 0.999, and one-probe/two-sector CCSC exposes the boundary with success 0.931 and empty-alias rate 0.260.

## Gaps To Close

- Scale: current evidence is one small contact library and one set of discretization choices.
- Contact diversity: current modes vary normals, friction, and gain but do not sweep mode counts, friction regimes, noise, margins, or clustered/adversarial mode geometry.
- Signature sensitivity: v2 varies only a few low-budget signatures; it does not map the full probe/task/action budget surface.
- Baselines: current baselines omit learned/proxy compression, random projections, prediction-only grouping, contact-count-plus-probe, belief/active-probe policies, and robust-safe refusal.
- Theorem boundary: current paper states that probing/history can help but does not quantify when active probing rescues aliasing or when probe cost makes it unattractive.
- Negative controls: current paper needs explicit cases where CCSC approaches raw identity, where signatures under-separate, where noisy feasibility labels split or merge wrongly, and where action discretization is too coarse.
- Final artifact: there is no current `Downloads/27.pdf`, and the manuscript is far below the required 25-page final threshold.

## Target V3 Experiment Families

### Family A: Main Contact-Library Scale Sweep

Vary contact mode count, task count, action count, friction regime, contact-margin/progress-margin, and seed. Compare contact count, normal bins, normal+friction bins, prediction-only grouping, random hash grouping, PCA/proxy grouping if feasible, CCSC, budgeted CCSC, and raw identity.

Primary outputs: success on raw-controllable tasks, empty-alias rate, destroyed episode rate, mean regret, groups, bits, max group size, and compression ratio.

### Family B: Signature Budget Surface

Sweep probe task count, action sector count, probe task placement, and action sector placement. Identify the success/empty-alias transition where CCSC becomes control-faithful enough. Include full signatures, underspecified signatures, random probe signatures, and adaptive greedy probe selection.

Primary outputs: heatmaps of success and empty-alias rate over probe budget; table of minimal budget to hit success >= 0.99 and empty-alias <= 0.01.

### Family C: Noise And Label Corruption

Inject feasibility-label false positives, false negatives, margin noise, normal noise, friction noise, and calibration modes. Compare raw CCSC, conservative CCSC, robust repeated-label CCSC, thresholded CCSC, and fallback/refusal policies.

Primary outputs: degradation curves and boundary rows where corrupted signatures become worse than normal/friction bins.

### Family D: Baselines And Ablations

Compare mechanism variants: no intersection check, no friction in signatures, no task probes, no action sectors, prediction-only compression, random compression at matched bit budgets, normal-only compression, normal+friction compression, CCSC, greedy CCSC, active-probe controller, belief-average controller, robust-safe refusal, and raw identity.

Primary outputs: ablation table showing which part of the repair matters.

### Family E: Active Probing And Probe Cost

Model a first-step deadline versus a probe-allowed setting. In the probe-allowed setting, a controller may spend a probe action to disambiguate the alias class before choosing the task action. Sweep probe cost, probe reliability, and first-action safety requirement.

Primary outputs: regimes where active probing rescues contact-count aliases and regimes where the theorem still bites because the first action must already be safe.

### Family F: Adversarial And Negative Controls

Construct clustered/adversarial mode libraries with near-identical predictions but disjoint action cones; libraries where CCSC needs almost raw identity; libraries where all modes truly share a robust action; and coarse-action settings where every method is limited by action discretization.

Primary outputs: counterexample library and reviewer-facing negative controls.

### Family G: Scalability And Compression Ledger

Sweep modes up to at least 512 or 1024 when feasible without high memory use. Use streaming rows and formula-light summaries to show how group count, bit count, and alias rate scale.

Primary outputs: scaling curves for groups/bits/success versus modes; memory-light metadata.

## Baselines

- Contact count.
- Normal bins at multiple resolutions.
- Normal+friction bins.
- Raw mode identity.
- Random bit-budget grouping.
- Prediction-only grouping based on transmitted velocities under average action/task probes.
- Budget-matched random signatures.
- CCSC with regular task/action grids.
- CCSC with random probes.
- Greedy adaptive CCSC probe selection.
- Conservative CCSC under noisy feasibility labels.
- Thresholded CCSC.
- Active-probe disambiguation.
- Belief-average action selection.
- Robust-safe refusal policy.

## Tables And Figures

- Inventory table with rows, cases, family purposes, and runtime.
- Main representation table for Family A.
- Scale curve: success/empty-alias/groups/bits versus mode count.
- Budget heatmap: probe tasks by action sectors.
- Noise curve: signature corruption versus success and empty-alias rate.
- Baseline/ablation table.
- Probe-cost table for active probing.
- Counterexample table.
- Compression ledger: bits, groups, max group size, compression ratio.
- Claim-to-evidence map.

## Manuscript Expansion Strategy

The final manuscript should become a full 25+ page paper because it contains real new content, not filler:

- Expand related work and novelty boundary around contact modes, contact-implicit planning, tactile representation, abstraction/bisimulation, and learned world models.
- Add formal definitions for robust action intersection, margin-aware control-faithfulness, noisy-label variants, and active-probe exceptions.
- Add proof discussion and implementation invariants.
- Present the seven experiment families with generated tables and figures.
- Add limitations that distinguish local theorem, probe-allowed recovery, noisy signatures, and hardware gaps.
- Add appendices for row schema, cost/probe model, simulator parameters, validation checks, counterexamples, reproducibility, and reviewer attack responses.

## RAM-Light Execution Strategy

- Stream experiment rows to CSV family by family.
- Store only aggregate counters and small counterexample records in memory.
- Avoid materializing large mode-pair/task/action tensors when possible; compute masks per case and discard.
- Run families sequentially.
- Use deterministic seeds and write `progress.json` after each family.
- Generate summary CSVs and TeX tables after each family.
- Keep plots small and generated from summaries.

## Final Acceptance Checklist

Before Paper27 is final:

- Detailed plan exists before experiment/manuscript edits.
- Full-scale runner compiles.
- Full-scale suite completes with at least 75,000 rows unless a clearly stronger case-count metric is justified.
- Metadata records seed, rows, cases, runtimes, and zero plot failures.
- Manuscript builds cleanly to at least 25 pages.
- PDF text contains `v3 final full-scale`, row/case counts, headline positive results, negative boundaries, and no-real-robot limitation.
- Final PDF is copied to `C:/Users/wangz/Downloads/27.pdf`.
- Final PDF has at least 25 pages and a recorded SHA256 hash.
- Local `paper/main.pdf` is removed after export.
- Docs record final evidence, validation, readiness, attack log, reproducibility, and hash.
- Repo is committed, pushed, clean, and `HEAD == @{u}` before Paper28 begins.
