# Shadow 06 — Noise Floor, figure specification v0.3

This repository contains the frozen Figure Specification v0.2 and its v0.3 delta. Ten figures are active. Pack 03 withdraws F5, rebuilds F6 and F7, revises F1, F2, F4, F9 and F11, and leaves F3, F8 and F10 unchanged. The five CSVs supplied in Pack 03 replace their earlier versions; unchanged CSVs remain from Pack 02.

## Build offline

Requires Python 3, `reportlab` and `pypdf` (`pip install -r requirements.txt`). The generating scripts make no network requests. From the repository root:

```sh
python3 figures/render.py
python3 figures/check.py
```

Each active `figures/F#.py` regenerates one figure. Every active figure has a light SVG, a dark SVG and a vector PDF. F4, F6, F7 and F8 also have standalone accessible HTML tables (`figures/F#.table.html`). `figures/CHECK.md` lists every plotted or tabulated value read back from the generated SVG and compared with the CSV, along with source discrepancies; table values are also checked in HTML. The PDF generator draws from the same SVG primitives using the bundled Shadow fonts.

The light rendition uses only the Shadow 04 colour tokens. The dark rendition matches the published Shadow 04 landing palette. For use on a landing, embed the SVG inline or load the bundled fonts on the page so the text uses Inter and JetBrains Mono.

## Design source

Palette and typography come from `MaksymDS/shadow-crack-landing` (Shadow 04), commit `2a3e144d76c3ffb66c44e1d6196df81a06087c9d`, `README.md` and `index.html`. Shadow 05 (`MaksymDS/shadow-mandate-landing`) uses the same tokens and figure kit. The font binaries in `figures/fonts/` are included for offline PDF rendering; their licences and provenance are documented there.

## Source metadata checked separately

No values from these pages were used to draw the charts. They were used only to complete the source lines:

- [Pew Research Center, “How Much of the Internet Is Written With AI?” (20 Aug 2026)](https://www.pewresearch.org/data-labs/2026/08/20/how-much-of-the-internet-is-written-with-ai/)
- [Deezer, “AI-generated tracks now represent 44% of all new uploaded music” (20 Apr 2026)](https://newsroom-deezer.com/2026/04/ai-generated-tracks-represent-44-of-new-uploaded-music/)
- [Deezer, “AI music has surpassed 50% of new music uploads for the first time” (21 Jul 2026)](https://newsroom-deezer.com/2026/07/ai-music-exceeds-50-percent-daily-uploads-deezer/)
- [arXiv, “Fair Moderation, Equitable Access, and AI: arXiv’s Updated Rate Limit Policy” (1 Oct 2026)](https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/)
- [Bastani et al., “Generative AI without guardrails can harm learning: Evidence from high school mathematics” (PNAS 2025)](https://pubmed.ncbi.nlm.nih.gov/40560616/)

The F4 and F7 CSVs do not contain enough outlet, original document and date information for complete primary-source lines. Their source lines identify the supplied CSV and show ledger IDs where present. F6 uses the exact source line specified in v0.3. See `figures/CHECK.md` for strict readings and remaining source gaps.
