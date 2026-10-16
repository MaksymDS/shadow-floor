![Noise Floor](assets/noise-floor-social.png)

<h1 align="center">Noise Floor</h1>
<p align="center">Data and figures for Shadow 06 · Foresight Future Institute</p>

<p align="center"><a href="https://github.com/MaksymDS/shadow-floor-landing">Landing HTML</a> · <a href="REFERENCES.md">References</a> · <a href="figures/CHECK.md">Figure checks</a></p>

---

This repository holds the source CSVs, rendering scripts and export files for the ten active figures in *Noise Floor*. Each figure is available as a light and dark SVG and a vector PDF. Four comparison figures also have standalone HTML tables. The [reference register](REFERENCES.md) connects the figure data to the available original publications and records what still needs a direct citation.

## Data and figures

| Figure | Subject | Data | Exports |
|:--|:--|:--|:--|
| F1 | Signs of AI authorship by web domain | [CSV](shadow06-figdata/F1_pew_domain_share.csv) | [SVG](figures/F1.svg) · [dark SVG](figures/F1.dark.svg) · [PDF](figures/F1.pdf) |
| F2 | Music uploads and streams | [CSV](shadow06-figdata/F2_deezer_uploads_vs_streams.csv) | [SVG](figures/F2.svg) · [dark SVG](figures/F2.dark.svg) · [PDF](figures/F2.pdf) |
| F3 | arXiv monthly submissions | [CSV](shadow06-figdata/F3_arxiv_submissions.csv) | [SVG](figures/F3.svg) · [dark SVG](figures/F3.dark.svg) · [PDF](figures/F3.pdf) |
| F4 | Counting, screening, judging | [CSV](shadow06-figdata/F4_institutions_decisions.csv) | [SVG](figures/F4.svg) · [dark SVG](figures/F4.dark.svg) · [PDF](figures/F4.pdf) · [HTML table](figures/F4.table.html) |
| F5 | 1.5 million registrations, 17,000 owners | [CSV](shadow06-figdata/F5_moltbook.csv) | [SVG](figures/F5.svg) · [dark SVG](figures/F5.dark.svg) · [PDF](figures/F5.pdf) |
| F6 | Providers, one table | [CSV](shadow06-figdata/F6_providers.csv) · [source list](shadow06-figdata/F6_sources.csv) | [SVG](figures/F6.svg) · [dark SVG](figures/F6.dark.svg) · [PDF](figures/F6.pdf) · [HTML table](figures/F6.table.html) |
| F7 | Who must mark what | [CSV](shadow06-figdata/F7_obligations.csv) | [SVG](figures/F7.svg) · [dark SVG](figures/F7.dark.svg) · [PDF](figures/F7.pdf) · [HTML table](figures/F7.table.html) |
| F8 | Different samples, periods and units | [CSV](shadow06-figdata/F8_vendor_methods.csv) | [SVG](figures/F8.svg) · [dark SVG](figures/F8.dark.svg) · [PDF](figures/F8.pdf) · [HTML table](figures/F8.table.html) |
| F9 | Practice versus exam | [CSV](shadow06-figdata/F9_learning_study.csv) | [SVG](figures/F9.svg) · [dark SVG](figures/F9.dark.svg) · [PDF](figures/F9.pdf) |
| F10 | UK undergraduates and AI, 2024–2026 | [CSV](shadow06-figdata/F10_hepi.csv) | [SVG](figures/F10.svg) · [dark SVG](figures/F10.dark.svg) · [PDF](figures/F10.pdf) |

Figure IDs follow the current editorial numbering.

## How to read this repository

The CSVs are fixed input snapshots. Source names in the tables connect to publications in the [reference register](REFERENCES.md). Vendor figures and detector outputs retain the scope, units and limitations stated in their sources. In particular, F8's vendor estimates are not directly comparable, and F7 includes records whose original text was located but not cleared for a detailed English description. See the notes in the figures and the [check report](figures/CHECK.md) before reusing a value.

The check report compares every plotted value and table cell with its CSV and checks the PDF exports. It verifies the rendering pipeline, not the underlying claims independently.

## Rebuild

Use Python 3 and the packages in [`requirements.txt`](requirements.txt):

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 figures/render.py
python3 figures/check.py
```

Generation is offline and reads only the checked-in CSVs. [`figures/render.py`](figures/render.py) writes the exports; [`figures/check.py`](figures/check.py) reads values back and regenerates [`figures/CHECK.md`](figures/CHECK.md). Selected exact captions and labels are recorded in [`figures/TEXT.md`](figures/TEXT.md). The bundled figure fonts and their licences are documented in [`figures/fonts/README.md`](figures/fonts/README.md).
