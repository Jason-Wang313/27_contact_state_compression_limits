# Plan: Paper 27 - Contact State Compression Limits

## Objective
Create a complete, runnable, anonymous ICLR-style robotics paper package for "Contact State Compression Limits" in this repository, ending with a compiled PDF at `C:/Users/wangz/Downloads/27.pdf`, a public GitHub repository named `27_contact_state_compression_limits`, and a final audit.

## Safety Rules for This Run
- Keep all work inside this repository except the required final PDF output path.
- Use safe, bounded PowerShell commands and Python scripts rather than fragile inline probes.
- Give long-running experiments/builds explicit timeouts.
- Preserve and reuse any existing artifacts if present.
- Keep `child_status.md` compact and current; status update failures must not abort the run.

## Execution Phases
1. Initialize status and inspect existing repository state.
2. Create scripts and directories for literature retrieval, analysis, experiments, figures, and paper building.
3. Run a 1000-paper landscape sweep and save `docs/related_work_matrix.csv`.
4. Produce a 300-paper serious skim, 200-250-paper deep read, and 100-paper hostile prior-work set.
5. Write required literature and novelty artifacts:
   - `docs/literature_map.md`
   - `docs/hostile_prior_work.md`
   - `docs/novelty_boundary_map.md`
   - `docs/novelty_decision.md`
   - `docs/claims.md`
   - `docs/reviewer_attacks.md`
6. Choose the strongest paper direction only after the literature sweep.
7. Build runnable evidence: formal examples plus simulation experiments showing when contact-state compression destroys controllability and how the proposed repair restores it.
8. Generate figures and tables from cached results.
9. Fetch or recreate the latest official ICLR template available at runtime, then write the full anonymous paper.
10. Sanitize bibliography and LaTeX text for pdfLaTeX safety.
11. Compile with direct `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` using generous timeouts.
12. Save final PDF to `C:/Users/wangz/Downloads/27.pdf`.
13. Create/push public GitHub repo `27_contact_state_compression_limits`, or document any failure.
14. Write `docs/final_audit.md` with all required answers.

## Initial Research Hypothesis
Compressed contact state can merge mechanically distinct contact modes that require different feasible action cones. When that aliasing collapses controllability-relevant distinctions, no downstream controller can recover the lost action-conditioned reachability. A possible repair is to compress contact state only through action-separating invariants: retain the minimal contact predicates needed to distinguish local control cones, not every geometric detail.

This hypothesis is provisional and must be challenged against the literature before becoming the paper thesis.
