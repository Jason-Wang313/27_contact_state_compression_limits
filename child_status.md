# Child Status: Paper 27

Stage: complete; v2 submission hardening ready to commit and push

Current facts:
- Literature sweep completed with `docs/related_work_matrix.csv` containing 1000 rows and `docs/hostile_prior_work.md` containing 100 hostile priors.
- Experiment artifacts generated in `results/` and `figures/`.
- V2 signature-budget stress generated `results/signature_budget_stress.csv` and `results/signature_budget_stress_table.tex`.
- V2 stress result: one probe task/two action sectors gives success 0.931 and empty-alias rate 0.260; the six-probe/eight-sector setting gives success 0.999 and empty-alias rate 0.007.
- Official ICLR 2026 template downloaded from `https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026.zip`.
- Paper generated at `paper/main.tex` with visible v2 note, stress table, and narrowed limitations.
- LaTeX build completed with direct `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Final PDF copied to `C:/Users/wangz/Downloads/27.pdf`.
- Transient `paper/main.pdf` removed so the final PDF exists only at the required Downloads path.
- Checked Desktop paths contain no `27.pdf`.
- Public GitHub repo created and pushed: `https://github.com/Jason-Wang313/27_contact_state_compression_limits`.
- `docs/final_audit.md` exists and reports build/publish status as complete, with Downloads-only artifact status.

Commands run:
- `python scripts/literature_sweep.py` twice; second run succeeded via Crossref fallback.
- `python scripts/run_experiments.py` for the v2 stress update.
- `python scripts/write_paper.py`
- `powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1`
- `powershell -ExecutionPolicy Bypass -File scripts/publish_repo.ps1`
- `python scripts/write_final_audit.py`
- `python -m py_compile src\contact_compression.py scripts\run_experiments.py scripts\write_paper.py scripts\write_final_audit.py`
- `pdftotext C:\Users\wangz\Downloads\27.pdf -`
- `git diff --check`
- Safe probes for build status, files, matrix row count, PDF existence, Desktop absence, local PDF absence, git status, and final audit contents.

Failures:
- OpenAlex returned HTTP 429 for all live queries.
- Initial repair signature overfit and separated every mode.
- First LaTeX build failed because the PowerShell build script passed no args to `pdflatex`.
- Second LaTeX build failed on an unbalanced indicator formula.
- First final-audit generation could not read PowerShell JSON statuses because of BOM handling.

Recovery steps:
- Added Crossref fallback retrieval.
- Coarsened control-cone signature probes.
- Renamed PowerShell function argument parameter from `Args` to `ArgList` in build and publish scripts.
- Patched the indicator formula and regenerated `paper/main.tex`.
- Patched `scripts/write_final_audit.py` to read status JSON with `utf-8-sig`.
- Rebuilt, pushed, and regenerated the final audit successfully.
- Added v2 signature-budget stress and narrowed the CCSC claim to probe-rich signatures.
- Added standard hardening docs: attack log, version log, hostile reviewer response, rigor checklist, reproducibility checklist, and readiness decision.

Next:
- Commit and push the v2 hardening update.

Exit code: 0
End time: 2026-06-11 21:21:46 +01:00
PDF exists: True
