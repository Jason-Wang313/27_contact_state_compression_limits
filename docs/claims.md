# Claims

| Claim | Type | Current support | Risk |
|---|---|---|---|
| If two contact modes share a compressed state but have disjoint task-feasible action sets, no deterministic policy using only that compressed state can guarantee the one-step task progress for both modes. | Formal theorem | Proved in paper from set intersection contradiction. | One-step/local; history or probing may help when safety allows. |
| Contact-count or coarse-normal compression frequently creates empty feasible-action intersections in frictional contact. | Empirical | Measured in the runnable cone simulator. | Simulator is deliberately local and simplified. |
| Control-cone signature repair recovers most raw-mode success with fewer bits than exact mode identity. | Empirical/mechanistic | Measured by grouping modes by feasible-action signatures. | Depends on action/task discretization and known cone model. |
| Control-cone signature repair needs sufficiently rich task/action probes. | Empirical negative boundary | V2 signature-budget stress: one probe task/two action sectors gives success 0.931 and empty-alias rate 0.260, versus 0.999 success and 0.007 empty-alias rate for six probe tasks/eight sectors. | Still a local analytic-contact simulator; does not prove the same threshold on hardware. |
| Prediction-faithful compression is not sufficient for control-faithful contact compression. | Conceptual/formal example | Supported by constructed aliases with identical compressed observation and different control cones. | Needs broader real-robot validation. |
| The contribution is not a new contact simulator or tactile estimator. | Scope claim | Supported by novelty boundary map and hostile prior work. | Reviewers may ask for real hardware. |
