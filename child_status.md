# Child Status: Paper 27

Stage: complete; final follow-up commit pending

Current facts:
- Literature sweep completed with `docs/related_work_matrix.csv` containing 1000 rows and `docs/hostile_prior_work.md` containing 100 hostile priors.
- Experiment artifacts generated in `results/` and `figures/`.
- Official ICLR 2026 template downloaded from `https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026.zip`.
- Paper generated at `paper/main.tex`.
- LaTeX build completed with direct `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Final PDF copied to `C:/Users/wangz/Downloads/27.pdf`.
- Transient `paper/main.pdf` removed so the final PDF exists only at the required Downloads path.
- Public GitHub repo created and pushed: `https://github.com/Jason-Wang313/27_contact_state_compression_limits`.
- `docs/final_audit.md` exists and reports build/publish status as complete.

Commands run:
- `python scripts/literature_sweep.py` twice; second run succeeded via Crossref fallback.
- `python scripts/run_experiments.py` twice; second run is final.
- `python scripts/write_paper.py`
- `powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1`
- `powershell -ExecutionPolicy Bypass -File scripts/publish_repo.ps1`
- `python scripts/write_final_audit.py`
- Safe probes for build status, files, matrix row count, PDF existence, git status, and final audit contents.

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

Next:
- Commit and push `docs/final_audit.md`, `data/git_push_status.json`, updated scripts, and this status file.

Exit code: 0
End time: 2026-06-11 21:21:46 +01:00
PDF exists: True
