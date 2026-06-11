# Contact State Compression Limits

Anonymous ICLR-style paper package for Paper 27 in the robotics/embodied-intelligence batch.

## Thesis

Compressed contact state can destroy controllability when it aliases contact modes whose task-feasible action sets have empty intersection. The proposed repair is contact-cone separating compression: retain the minimal action-separating contact predicates needed to preserve a robust feasible-action intersection.

## Reproduce

From this repository root on Windows PowerShell:

```powershell
python scripts/literature_sweep.py
python scripts/run_experiments.py
python scripts/write_paper.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The build script copies the final PDF to:

```text
C:/Users/wangz/Downloads/27.pdf
```

## Main Artifacts

- `docs/related_work_matrix.csv`: 1000-paper landscape matrix.
- `docs/literature_map.md`: field box, assumptions, directions, and chosen thesis.
- `docs/hostile_prior_work.md`: 100-paper hostile prior-work set.
- `docs/novelty_boundary_map.md`: novelty boundaries and weak moves rejected.
- `docs/claims.md`: formal and empirical claim status.
- `docs/reviewer_attacks.md`: likely reviewer objections and responses.
- `src/contact_compression.py`: local friction-cone contact model.
- `scripts/run_experiments.py`: regenerates results and figures.
- `paper/main.tex`: anonymous ICLR-style manuscript.

## Notes

The experiment is intentionally local and auditable. It is not a high-fidelity robot simulator or a hardware claim. The central evidence is the mechanism: once a representation merges modes with disjoint feasible action sets, no downstream deterministic compressed-state controller can choose one action that works for all of them.
