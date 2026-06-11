# Child Status: Paper 27

Stage: PDF built; ready to publish

Current facts:
- Literature sweep completed with `docs/related_work_matrix.csv` containing 1000 rows and `docs/hostile_prior_work.md` containing 100 hostile priors.
- Experiment artifacts generated in `results/` and `figures/`.
- Official ICLR 2026 template downloaded from `https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026.zip`.
- Paper generated at `paper/main.tex`.
- LaTeX build completed with direct `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Final PDF copied to `C:/Users/wangz/Downloads/27.pdf`.
- Transient `paper/main.pdf` removed so the final PDF exists only at the required Downloads path.
- Required docs exist except `docs/final_audit.md`, which will be written after GitHub publish attempt.

Commands run:
- `python scripts/literature_sweep.py` twice; second run succeeded via Crossref fallback.
- `python scripts/run_experiments.py` twice; second run is final.
- `python scripts/write_paper.py`
- `powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1`
- Safe probes for build status, files, matrix row count, and PDF existence.
- Removed generated duplicate `paper/template_download` after verifying it was inside repo root.

Failures:
- OpenAlex returned HTTP 429 for all live queries.
- Initial repair signature overfit and separated every mode.
- First LaTeX build failed because the PowerShell build script passed no args to `pdflatex`.
- Second LaTeX build failed on an unbalanced indicator formula.

Recovery steps:
- Added Crossref fallback retrieval.
- Coarsened control-cone signature probes.
- Renamed PowerShell function argument parameter from `Args` to `ArgList` in build and publish scripts.
- Patched the indicator formula and regenerated `paper/main.tex`.
- Rebuilt successfully.

Next:
- Run `powershell -ExecutionPolicy Bypass -File scripts/publish_repo.ps1`.
- Write `docs/final_audit.md`.
