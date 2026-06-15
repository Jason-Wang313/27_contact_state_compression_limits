# Reviewer Attacks

1. **This is just partial observability.** The paper narrows the generic POMDP issue to a contact-specific algebraic certificate: empty intersections of feasible action cones inside an alias class.
2. **Contact planners already keep modes.** Correct. The target is compressed contact states in learned world models, tactile encoders, compact policies, and symbolic abstractions.
3. **The experiments are synthetic.** Correct. The paper is a local mechanism audit, not hardware validation.
4. **A probe can reveal the mode.** Only if it is safe, reliable, and before the task action. Family E quantifies this exception.
5. **Bisimulation already covers abstraction.** The paper instantiates the abstraction question as a physically interpretable contact-cone intersection test.
6. **The repair needs labels.** Correct. Feasibility-label quality is an assumption, and Family C attacks it.
7. **Empty intersection is conservative.** Yes, deliberately. The claim is robust first-action control, not average reward.
8. **CCSC may approach raw identity.** Yes. The suite reports group counts and bits so this cost is visible.
9. **Low-budget CCSC can fail.** Yes. Family B and the manuscript make this a core boundary.
