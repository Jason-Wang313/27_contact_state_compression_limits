# Reproducibility Checklist

- [x] Main simulator is `src/contact_compression.py`.
- [x] Main experiment script is `scripts/run_experiments.py`.
- [x] Paper generator is `scripts/write_paper.py`.
- [x] Build script is `scripts/build_pdf.ps1`.
- [x] Main outputs are `results/summary.csv`, `results/summary.json`, `results/episode_results.csv`, and `results/policy_results.csv`.
- [x] V2 outputs are `results/signature_budget_stress.csv` and `results/signature_budget_stress_table.tex`.
- [x] Figures are in `figures/`.
- [x] Paper source is `paper/main.tex`.
- [x] Canonical PDF path is `C:/Users/wangz/Downloads/27.pdf`.
- [x] Local `paper/main.pdf` is removed after canonical copy.
- [x] Visible Desktop PDF copies are absent.

Recommended verification commands:

```powershell
python scripts\run_experiments.py
python scripts\write_paper.py
powershell -ExecutionPolicy Bypass -File scripts\build_pdf.ps1
```
