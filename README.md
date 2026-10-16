# Shadow 06 — Noise Floor, first figure batch

This repository contains the frozen Figure Specification v0.1 and seven source CSVs from the supplied Codex pack. The first batch covers F1, F2, F3, F5, F9, F10 and F11. F4, F6, F7 and F8 are deferred by that task.

## Build offline

Requires Python 3, `reportlab` and `pypdf` (`pip install -r requirements.txt`). The generating scripts make no network requests. From the repository root:

```sh
python3 figures/render.py
python3 figures/check.py
```

Each `figures/F#.py` regenerates one figure. Every figure has a light SVG, a dark SVG and a vector PDF. `figures/CHECK.md` lists every plotted value read back from the generated SVG and compared with the CSV, along with source discrepancies. The PDF generator draws from the same SVG primitives using the bundled Shadow fonts.

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

See `figures/CHECK.md` for the differences between source prose and the frozen CSVs.
