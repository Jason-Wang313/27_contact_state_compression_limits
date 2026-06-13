# Experiment Rigor Checklist

- [x] Main local contact simulator is `src/contact_compression.py`.
- [x] Main experiment script is `scripts/run_experiments.py`.
- [x] Main sweep evaluates 64 contact modes, 180 action directions, and 24 task directions.
- [x] Evaluation is conditioned on raw-mode controllability.
- [x] Baselines include contact count, normal bins, normal-plus-friction bins, CCSC, and raw mode identity.
- [x] V2 signature-budget stress attacks the probe-rich-signature assumption.
- [x] Negative boundary is explicit: one probe task/two action sectors gives success 0.931 and empty-alias rate 0.260.
- [ ] No high-fidelity robot simulator.
- [ ] No hardware validation.
- [ ] No learned tactile/contact signature estimator.
- [ ] No belief-space or active-probing controller baseline.

Decision: mechanism evidence only; terminal state is workshop-only / strong-revise.
