# Hostile Reviewer Response

## Likely Rejection

The paper proves a local one-step obstruction in a synthetic contact model. It depends on action-feasibility labels and sufficiently rich task/action probes. It does not show that a real learned robot world model fails this way, nor that CCSC is practical on hardware.

## Honest Response

We agree. The contribution is a representation-level failure certificate and repair audit, not a deployable contact planner or tactile estimator. The theorem explains when a compressed contact state has already discarded information needed for the first control action.

The v3 suite expands the evidence to 85,674 rows. It also keeps the boundary explicit: one-probe/two-sector signatures under-separate, noisy labels must be audited, and active probing only helps when it is safe and available before the task action.

## Required Upgrade For A Stronger Robotics Submission

- Validate the alias certificate in high-fidelity simulation or hardware.
- Learn action-feasibility signatures from tactile/action data.
- Compare against belief-space probing, robust MPC, contact-implicit planning, and bisimulation-style abstractions.
- Test action discretization, task distribution, friction uncertainty, and delayed probing.
