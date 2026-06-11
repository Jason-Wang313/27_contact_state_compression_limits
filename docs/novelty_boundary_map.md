# Novelty Boundary Map

## Already Covered
- Contact-rich manipulation mechanics and planar pushing controllability.
- Complementarity and hybrid-mode formulations for contact dynamics.
- Contact-invariant or contact-implicit trajectory optimization when the optimizer retains contact variables.
- Tactile/contact state estimation as a perception problem.
- Generic state abstraction, bisimulation, and MDP model minimization.
- Physics engines and differentiable simulators that expose contact variables.

## Not Enough For Novelty
- A larger dynamics model.
- A contact prediction benchmark alone.
- Adding uncertainty, active learning, a verifier, or an ensemble around the same compressed state.
- Combining a known estimator with a known planner without changing the compression criterion.
- Using an LLM or reinforcement learning as the planner.

## Claimed Boundary
The new boundary is a representation-level condition for contact dynamics: a compression is control-faithful for a task family only if every alias class retains a nonempty robust intersection of feasible action sets. The repair is not a bigger estimator; it is a refinement rule that splits contact states by action-cone signatures.

## Closest Hostile Families
1. Pushing mechanics and controllability: already show contact mechanics can be central, but usually assume the state variables needed for the mechanics are represented.
2. Contact-implicit optimization: can choose contact sequences or forces, but the optimizer is not restricted to a destroyed compressed contact state.
3. MDP/bisimulation abstraction: gives equivalence ideas, but does not expose frictional contact action cones as the representation primitive.
4. Tactile state estimation: estimates contact, but often optimizes semantic or predictive labels rather than minimal control-separating predicates.
