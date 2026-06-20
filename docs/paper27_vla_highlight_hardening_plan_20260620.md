# Paper27 VLA Highlight Hardening Plan

Date: 2026-06-20

## Objective

Make `C:/Users/wangz/Downloads/27.pdf` match the visible VLA-v4 role model's
boxed-link behavior while preserving the final 25-page contact-compression
paper:

- citation links should use green one-point boxes;
- internal figure/table/section links should use red one-point boxes;
- no cyan URL boxes should appear;
- the final PDF should be rebuilt, copied only to Downloads, visually checked,
  and leave no local `paper/main.pdf`.

## Plan-Start Evidence

Baseline artifact:

- Canonical PDF: `C:/Users/wangz/Downloads/27.pdf`
- Pages: 25
- Size: 333,998 bytes
- SHA256: `33273D7AEDE66A426953DD00D1BE14D571B78C42D83F9B3AF0B8B41465949179`
- Local `paper/main.pdf`: absent
- Repository state: clean against `origin/main`

Baseline link inventory from the current Downloads PDF:

- Link pages: `[]`
- Annotation colors: green = 0, red = 0, cyan = 0
- Link annotations: 0

Source finding:

- `paper/main.tex` is the active manuscript source.
- The active preamble does not currently load `hyperref`.
- `paper/iclr2026_conference.sty` loads `natbib` but not `hyperref`.
- The manuscript already contains `\citep` citations and `Table~\ref{...}`
  references, so enabling hyperref should create real green citation boxes and
  red internal-reference boxes without adding content.

## Role-Model Target

Install the same explicit hyperref policy as the visible VLA-v4 role model:

```tex
\usepackage{hyperref}
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

## Execution Plan

1. Add `hyperref` and the VLA `\hypersetup` block in `paper/main.tex` after the
   normal layout/math packages and before `\graphicspath`.
2. Rebuild with `scripts/build_pdf.ps1`, including BibTeX, so the final PDF is
   copied to Downloads and local `paper/main.pdf` is removed.
3. If the first rebuild asks for another LaTeX pass, rerun the canonical build
   and use only the final artifact metadata.
4. Recompute page count, SHA256, annotation colors, border widths, and link
   pages from the rebuilt PDF.
5. Render all affected link pages from the rebuilt Downloads PDF into
   `tmp/pdfs/paper27_after`.
6. Visually inspect the rendered affected pages:
   - green citation boxes are crisp and aligned;
   - red internal-reference boxes are crisp and aligned;
   - no cyan boxes appear;
   - layout, figures, tables, headers, and page count remain stable.
7. Update README/status/audit/version/validation metadata with the new hash and
   visual-hardening result.
8. Scan LaTeX logs for fatal errors, undefined citations/references, rerun
   warnings, and overfull boxes.
9. Remove Paper27 temp renders, leaving only the shared role-model render
   directory.
10. Stage only Paper27 source and metadata files, commit, push, and verify a
    clean repository.

## Non-Goals

- Do not alter experiment results, claims, figures, tables, bibliography
  content, or page count.
- Do not add or remove citations merely to change link counts.
- Do not edit the ICLR template/example source unless the active build requires
  it.
- Do not leave intermediate PDFs or render folders behind.

## Completion Evidence

- Rebuilt Downloads artifact: `C:/Users/wangz/Downloads/27.pdf`
- Pages: 25
- Size: 382832 bytes
- SHA256: `D87F6B88C548175E7B4BABB05B2AF07B3AB70B2CA4AC170D1CC3774C777CD467`
- Local `paper/main.pdf`: absent after export
- Link pages after rebuild: `[(2, 22), (3, 2), (5, 1)]`
- Annotation colors after rebuild: green = 24, red = 1, cyan = 0
- Border widths after rebuild: `(0, 0, 1)` for all 25 link annotations
- Rendered affected pages inspected from `tmp/pdfs/paper27_after`; green
  citation boxes and the red internal-reference box are crisp and aligned, and
  no cyan boxes are present.
