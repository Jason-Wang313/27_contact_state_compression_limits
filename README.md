# Contact State Compression Limits

Anonymous ICLR-style paper package for Paper 27 in the robotics/embodied-intelligence batch.

## Final V3 State

- Canonical PDF: `C:/Users/wangz/Downloads/27.pdf`.
- Page count: 25.
- PDF bytes: 333998.
- PDF SHA256: `33273D7AEDE66A426953DD00D1BE14D571B78C42D83F9B3AF0B8B41465949179`.
- Local `paper/main.pdf`: intentionally absent after export.
- Full-scale suite: 85,674 streamed rows over 1,290 deterministic cases, seed 27027, zero plot failures.

## Thesis

Compressed contact state can destroy controllability when it aliases contact modes whose task-feasible action sets have empty intersection. The repair is contact-cone separating compression (CCSC): retain action/task feasible-cone signatures rich enough to preserve robust feasible-action intersections.

## Main Artifacts

- `docs/full_scale_execution_plan.md`: detailed v3 execution plan written before substantive v3 edits.
- `scripts/full_scale_contact.py`: RAM-light full-scale v3 experiment runner.
- `results/full_scale/`: streamed rows, summaries, metadata, generated TeX tables.
- `figures/full_scale/`: generated final figures.
- `paper/main.tex`: final 25-page manuscript.
- `docs/validation_report.json`: final export and verification record.

Legacy v1/v2 outputs remain for audit history, but the final manuscript is based on the v3 full-scale suite.

## Reproduce

```powershell
python scripts/full_scale_contact.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Headline Findings

- Family A contact-count success: 0.759; empty-alias rate: 0.969.
- Family A CCSC 6x8 success: 0.999954; empty-alias rate: 0.000389.
- Family H task-conditioned rows: 80,640 rows; contact-count success 0.764 versus CCSC 6x8 success 0.999932.
- Signature-budget boundary: one probe task/two sectors leaves success near 0.956 and empty-alias rate near 0.115.
- Active probing helps only when a reliable probe is allowed before the task action.

The final claim is synthetic and local. It does not claim hardware validation, learned tactile signature extraction, production contact-implicit planning superiority, general POMDP optimality, or safety certification.
