# Shadow 06 "Noise Floor" — Codex Task 01 (figures, first batch)

You are building figures for an evidence-based research issue published as "Foresight Future Institute". Work in one pass and report back with the list of files produced.

## Inputs
- `shadow06-figures-spec-v0.1.md` — the specification. Follow it literally.
- `shadow06-figdata/*.csv` — the only data you may plot.
- The Shadow 04 design system (palette, fonts, components, figure kit) used by the published Shadow 04 and Shadow 05 issues. Reuse it exactly; do not introduce colours, fonts or layouts that are not in it. If you cannot locate the Shadow 04 tokens in the repository, stop and say so — do not invent a palette.

## Repository
Create the figures in the Shadow 06 repository the author designates (working name `shadow-noise-floor`, under the author's personal GitHub account). If it does not exist yet, produce the files locally in `figures/` and list them; do not create a public repository.

## Build F1, F2, F3, F5, F9, F10, F11
For each figure produce:
1. `figures/F#.svg` (vector, for the landing) and `figures/F#.pdf` (for the PDF report), light theme; plus a dark-theme SVG if the Shadow 04 landing supports dark mode.
2. `figures/F#.py` (or equivalent) — the script that generates it from the CSV, deterministic, no network access.
3. Title, caption and source line exactly as in the spec. Source line under the plot area.

## Hard rules
- Plot only values present in the CSV. No interpolation, smoothing, fitted trends or extra points.
- F2: do not add data points that are not in the CSV (the spec explicitly excludes Jun 2025 and Jan 2026).
- F10: the 2024 "assessed work" value is blank — leave a gap with the note "just over half (no exact figure)".
- Direct labels on series; colour is never the only carrier of meaning.
- Every figure must read correctly in greyscale print.
- Write a `figures/CHECK.md` table: figure ID → CSV used → every plotted value → matches CSV (yes/no). Fill it by reading back from the generated files, not from memory.

## Do not
- Do not edit the CSVs or the spec. If something in the spec is ambiguous, choose the stricter reading and note it in CHECK.md.
- Do not build F4, F6, F7, F8 — they are deferred.
