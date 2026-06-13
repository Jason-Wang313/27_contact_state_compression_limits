# Hostile Reviewer Response

## Likely Rejection

The work proves a local one-step obstruction in a toy contact model, then proposes a repair that depends on action-feasibility labels and sufficiently rich probe tasks/action sectors. It does not show that a real learned robot world model fails this way, nor that CCSC is practical on hardware.

## Honest Response

We agree. The contribution is a representation-level failure certificate, not a deployable contact planner or tactile estimator. The theorem explains when a compressed contact state has already discarded information needed for the first control action.

The v2 stress quantifies the repair boundary. With one probe task and two action sectors, CCSC success is 0.931 and empty-alias rate is 0.260. With six probe tasks and eight action sectors, success is 0.999 and empty-alias rate is 0.007. The paper should claim only the probe-rich, action-labeled regime.

## Required Upgrade For Main-Track Submission

- Validate the alias certificate in a high-fidelity simulator or robot manipulation setup.
- Learn or estimate action-feasibility signatures from tactile/action data.
- Compare against belief-space probing, robust MPC, contact-implicit planning, and bisimulation-style abstractions.
- Show sensitivity to action discretization, task distribution, friction uncertainty, and delayed probing.
