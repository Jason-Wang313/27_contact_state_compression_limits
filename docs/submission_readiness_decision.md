# Submission Readiness Decision

Decision: workshop-only / strong-revise.

## Why Not Submit-Ready

- Evidence is local and analytic rather than high-fidelity simulated or robotic.
- The theorem is one-step and deterministic.
- The repair assumes action-feasibility labels or a contact model.
- V2 shows low-budget signatures under-separate control cones.
- There is no belief-space probing, robust MPC, or contact-implicit planning baseline.

## Why Not Kill

- The feasible-action-intersection certificate is crisp and physically interpretable.
- The experiment directly matches the theorem's mechanism.
- CCSC recovers near-raw success under a transparent, auditable signature.
- The v2 stress makes the repair boundary explicit rather than hiding it.

## Required Next Work

- Validate on realistic manipulation contacts with noisy friction and geometry.
- Learn action-cone signatures from data.
- Add active probing and belief-state baselines.
- Quantify how many task/action probes are needed across broader contact families.
