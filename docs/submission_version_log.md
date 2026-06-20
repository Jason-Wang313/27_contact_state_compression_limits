# Submission Version Log

## v4 visual link-box hardening - 2026-06-20

- Added explicit VLA role-model `hyperref` boxed-link policy to
  `paper/main.tex`.
- Rebuilt twice with the canonical build script so cross-reference logs are
  clean after link anchors were introduced.
- Exported the final PDF to `C:/Users/wangz/Downloads/27.pdf`.
- Verified final PDF: 25 pages, 382832 bytes, SHA256
  `D87F6B88C548175E7B4BABB05B2AF07B3AB70B2CA4AC170D1CC3774C777CD467`.
- Verified link annotation colors: green = 24, red = 1, cyan = 0, with
  one-point borders on all 25 link annotations.
- Removed local `paper/main.pdf` after canonical export.

## v3 - 2026-06-15

- Wrote `docs/full_scale_execution_plan.md` before substantive v3 work.
- Added `scripts/full_scale_contact.py`.
- Generated `results/full_scale/` with 85,674 rows, 1,290 cases, seed 27027, and zero plot failures.
- Generated final figures under `figures/full_scale/`.
- Generated final TeX tables under `results/full_scale/tex/`.
- Rewrote `paper/main.tex` as a 25-page v3 final manuscript.
- Exported final PDF to `C:/Users/wangz/Downloads/27.pdf`.
- Verified v3 PDF before the 2026-06-20 visual-hardening rebuild: 25 pages,
  333998 bytes, SHA256 `33273D7AEDE66A426953DD00D1BE14D571B78C42D83F9B3AF0B8B41465949179`.
- Removed local `paper/main.pdf` after canonical export.

## v2 - 2026-06-13

- Added signature-budget stress generation to `scripts/run_experiments.py`.
- Generated `results/signature_budget_stress.csv`.
- Generated `results/signature_budget_stress_table.tex`.
- Updated `docs/experiment_report.md` with the v2 stress table.
- Updated the manuscript with a visible v2 note, abstract caveat, stress table, narrowed limitations, and reproducibility pointer.

## v1 - 2026-06-11

- Initial contact-state compression limits paper package with literature sweep, local friction-cone experiment, ICLR-style manuscript, final audit, canonical Downloads PDF, and public GitHub repo.
