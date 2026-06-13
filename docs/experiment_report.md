# Experiment Report

## Setup
- 64 local frictional contact modes with different contact normals and friction coefficients.
- 180 action directions and 24 task-progress directions.
- Evaluation is conditioned on raw-mode controllability, so failures are due to compression rather than impossible tasks.
- A compressed controller chooses one action for every mode in an alias class; success requires that action to satisfy the true mode's contact and task cone.

## Summary
| Representation | Groups | Bits | Success | Empty-intersection rate | Destroyed episode rate | Mean regret |
|---|---:|---:|---:|---:|---:|---:|
| contact_count | 1 | 0 | 0.720 | 1.000 | 1.000 | 0.216 |
| normal_2 | 2 | 1 | 0.879 | 0.562 | 0.692 | 0.192 |
| normal_4 | 4 | 2 | 0.980 | 0.105 | 0.074 | 0.190 |
| normal_8 | 8 | 3 | 0.994 | 0.039 | 0.016 | 0.104 |
| normal_16 | 16 | 4 | 0.994 | 0.022 | 0.016 | 0.059 |
| normal8_mu2 | 16 | 4 | 0.999 | 0.004 | 0.002 | 0.065 |
| cone_signature_repair | 52 | 6 | 0.999 | 0.007 | 0.002 | 0.008 |
| raw_mode | 64 | 6 | 1.000 | 0.000 | 0.000 | 0.000 |

## V2 Signature-Budget Stress

The submission-hardening stress test reruns the CCSC repair with fewer probe tasks and coarser action sectors. It shows that CCSC is conditional on a sufficiently rich action/task signature, not a free compression guarantee.

| Signature budget | Probe tasks | Action sectors | Groups | Bits | Success | Empty-intersection rate | Mean regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| one_task_two_sectors | 1 | 2 | 4 | 2 | 0.931 | 0.260 | 0.167 |
| one_task_four_sectors | 1 | 4 | 7 | 3 | 0.943 | 0.184 | 0.137 |
| two_tasks_two_sectors | 2 | 2 | 8 | 3 | 0.956 | 0.112 | 0.162 |
| two_tasks_four_sectors | 2 | 4 | 14 | 4 | 0.977 | 0.067 | 0.097 |
| v1_six_tasks_eight_sectors | 6 | 8 | 52 | 6 | 0.999 | 0.007 | 0.008 |

## Interpretation
Contact-count compression merges all local modes and frequently leaves no action that is feasible for every possible true contact. Coarser normal bins reduce but do not remove the problem. The cone-signature repair splits modes only when their feasible-action signatures differ, which recovers most raw-mode success without using exact mode identity. The v2 stress test also exposes the repair's own boundary: a low-budget signature under-separates control cones and leaves many empty aliases.

## Generated Artifacts
- `results/summary.json`
- `results/summary.csv`
- `results/episode_results.csv`
- `results/policy_results.csv`
- `results/signature_budget_stress.csv`
- `results/signature_budget_stress_table.tex`
- `figures/success_vs_bits.pdf`
- `figures/empty_intersection_rate.pdf`
- `figures/aliasing_heatmap.pdf`
- `figures/contact_cones_alias.pdf`
