# Reproducibility Checklist

- [x] Main model: `src/contact_compression.py`.
- [x] Full-scale runner: `scripts/full_scale_contact.py`.
- [x] Full-scale outputs: `results/full_scale/`.
- [x] Final figures: `figures/full_scale/`.
- [x] Final paper source: `paper/main.tex`.
- [x] Canonical PDF: `C:/Users/wangz/Downloads/27.pdf`.
- [x] Canonical PDF pages: 25.
- [x] Canonical PDF bytes: 382832.
- [x] Canonical PDF SHA256: `D87F6B88C548175E7B4BABB05B2AF07B3AB70B2CA4AC170D1CC3774C777CD467`.
- [x] Local `paper/main.pdf` removed after canonical copy.
- [x] VLA-style link boxes verified with pypdf inventory and rendered-page
  visual inspection.

Verification commands:

```powershell
python -m py_compile .\scripts\full_scale_contact.py .\src\contact_compression.py
python scripts\full_scale_contact.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdfinfo C:\Users\wangz\Downloads\27.pdf
Get-FileHash C:\Users\wangz\Downloads\27.pdf -Algorithm SHA256
```
