# Novelty Decision

## Decision
Proceed with a paper on contact-state compression limits and control-cone preserving repair.

## Chosen Thesis
Compressed contact state can destroy controllability when it aliases modes whose task-feasible action sets have empty intersection. The repair is to compress contact state by control-cone signatures: retain only the distinctions that separate feasible action cones for the task family.

## Why This Beats The Seed Alternatives
- It changes the central mechanism from prediction/estimation to feasible-action intersection.
- It can be stated as an impossibility theorem for compressed feedback policies.
- It produces runnable evidence in a contact-friction simulator.
- It gives a concrete repair that is neither bigger data nor an external verifier.

## Rejected Directions
- Benchmark-only aliasing tests: useful as evidence but not a contribution.
- Learned tactile encoder objective only: plausible, but the novelty would depend on training details.
- Uncertainty-aware planning: forbidden weak move unless the state itself is repaired.
- Full hybrid planner: too close to existing contact-implicit and mode-planning literature.
