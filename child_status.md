# Child Status: Paper 27

Stage: v3 final full-scale complete; VLA link-box hardening exported and
verified; ready for commit and push.

Latest actions:
- Wrote `docs/full_scale_execution_plan.md` before substantive v3 work.
- Added `scripts/full_scale_contact.py`.
- Ran the v3 suite to completion: 85,674 rows, 1,290 cases, seed 27027, zero plot failures.
- Rewrote `paper/main.tex` into a 25-page final manuscript with full-scale experiments, task-conditioned audit, budget surface, noise analysis, active probing, ablations, negative controls, limitations, and reproducibility appendices.
- Built with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Copied the verified final PDF to `C:/Users/wangz/Downloads/27.pdf`.
- Removed local `paper/main.pdf` after canonical export.
- Added explicit VLA-style `hyperref` boxed-link policy and rebuilt twice so
  cross-reference logs are clean after anchors were introduced.

Verification:
- Downloads PDF exists: true.
- Downloads PDF pages: 25.
- Downloads PDF bytes: 382832.
- Downloads PDF SHA256: `D87F6B88C548175E7B4BABB05B2AF07B3AB70B2CA4AC170D1CC3774C777CD467`.
- Required PDF text markers found: `v3 final full-scale`, `85,674`, `1,290`, `one probe task`, `active probing`, and `does not claim hardware validation`.
- `python -m py_compile .\scripts\full_scale_contact.py .\src\contact_compression.py` passed.
- Final LaTeX log has no undefined references, undefined citations, or overfull boxes.
- Link annotation inventory is green = 24, red = 1, cyan = 0, with one-point
  borders on all 25 link annotations.
- Rendered link pages 2, 3, and 5 were visually inspected.
- Local `paper/main.pdf` is absent.

Next:
- Commit and push Paper27 v3 final full-scale.
- Verify clean worktree and `HEAD == @{u}`.
- Only then proceed to Paper28.

End time: 2026-06-15 08:19:00 +01:00
