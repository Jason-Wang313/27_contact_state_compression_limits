# Reviewer Attacks

1. Attack: This is just partial observability. Response: The paper narrows the generic POMDP point to a contact-specific algebraic certificate: empty intersections of feasible action cones inside an alias class. The repair is representation refinement by control signatures, not belief-space planning.
2. Attack: Contact planners already keep modes. Response: Correct; the novelty is a limit on compressed contact states used by learned world models and compact policies, plus a minimal repair criterion.
3. Attack: The experiments are toy. Response: They are intentionally local to match the theorem. The claim is a mechanism demonstration, not full robot deployment.
4. Attack: A probing action can reveal the mode. Response: Only if the task permits unsafe or non-progress probing. The theorem covers one-step/local viability and deadlines where the first action must already satisfy the task/safety cone.
5. Attack: Bisimulation already solves abstraction. Response: Standard equivalences are not usually instantiated as frictional feasible-action cone preservation; the paper offers the contact-specific test and repair.
6. Attack: The repair needs a contact model. Response: Yes. The paper marks this as a weakness and suggests tactile/action-labeled estimation as future work, but does not hide it behind a learned black box.
7. Attack: Empty intersection is too conservative. Response: Conservative by design for robust control. The paper also reports average-action baselines to show where non-robust compression fails.
8. Attack: The repair may approach raw mode identity. Response: Experiments report bit counts; in the tested library the signature groups are smaller than raw identity but larger than contact count.
9. Attack: CCSC works only because the signature probes are hand-picked and rich. Response: The v2 stress accepts this boundary. With one probe task and two action sectors, success falls to 0.931 and empty-alias rate rises to 0.260; the paper now claims CCSC only as a probe-rich representation test, not as a free compression guarantee.
