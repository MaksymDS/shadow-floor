![Noise Floor — Shadow 06](assets/noise-floor-social.png)

<h1 align="center">Noise Floor</h1>

<p align="center"><strong>Shadow 06 · Figure set v0.3</strong><br>Foresight Future Institute</p>

<p align="center"><a href="https://github.com/MaksymDS/shadow-floor-landing">Landing preview</a> · <a href="figures/CHECK.md">Figure checks</a> · <a href="shadow06-figures-spec-v0.3.md">Current specification</a></p>

---

This repository contains the data, source code, and export files for ten figures in *Noise Floor*. The accompanying [HTML landing](https://github.com/MaksymDS/shadow-floor-landing) is a working visual preview; the manuscript and report download are still being assembled. The planned public address is **noise.foresightflow.org**.

## Figures

| ID | Subject | Exports |
|:--|:--|:--|
| F1 | Signs of AI authorship by web domain | [SVG](figures/F1.svg) · [dark](figures/F1.dark.svg) · [PDF](figures/F1.pdf) |
| F2 | Music uploads and streams | [SVG](figures/F2.svg) · [dark](figures/F2.dark.svg) · [PDF](figures/F2.pdf) |
| F3 | arXiv monthly submissions | [SVG](figures/F3.svg) · [dark](figures/F3.dark.svg) · [PDF](figures/F3.pdf) |
| F4 | Counting, screening, judging | [SVG](figures/F4.svg) · [dark](figures/F4.dark.svg) · [PDF](figures/F4.pdf) · [table](figures/F4.table.html) |
| F6 | Providers, one table | [SVG](figures/F6.svg) · [dark](figures/F6.dark.svg) · [PDF](figures/F6.pdf) · [table](figures/F6.table.html) |
| F7 | Who must mark what | [SVG](figures/F7.svg) · [dark](figures/F7.dark.svg) · [PDF](figures/F7.pdf) · [table](figures/F7.table.html) |
| F8 | Why ad-fraud figures do not add up | [SVG](figures/F8.svg) · [dark](figures/F8.dark.svg) · [PDF](figures/F8.pdf) · [table](figures/F8.table.html) |
| F9 | Practice versus exam | [SVG](figures/F9.svg) · [dark](figures/F9.dark.svg) · [PDF](figures/F9.pdf) |
| F10 | UK undergraduates and AI, 2024–2026 | [SVG](figures/F10.svg) · [dark](figures/F10.dark.svg) · [PDF](figures/F10.pdf) |
| F11 | 88 to 1 | [SVG](figures/F11.svg) · [dark](figures/F11.dark.svg) · [PDF](figures/F11.pdf) |

F5 was withdrawn in specification v0.3. Its material was incorporated into F6; there is no F5 export in this release.

## Reproduce the figures

Python 3 and the two packages in [`requirements.txt`](requirements.txt) are required. Generation and checks run offline from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 figures/render.py
python3 figures/check.py
```

Each [`figures/F#.py`](figures) reads its matching CSV from [`shadow06-figdata/`](shadow06-figdata) and produces a light SVG, a dark SVG, and a vector PDF. F4, F6, F7, and F8 also produce standalone HTML tables. [`figures/CHECK.md`](figures/CHECK.md) records the values read back from the generated output, along with the source gaps and stricter interpretations used in the charts.

The plotted values come from the supplied, frozen CSV snapshots. The scripts do not fetch or augment data, interpolate missing values, or make external requests. A successful build confirms that the exports match those CSVs; it is not independent verification of every underlying source claim.

## Specification and provenance

Read [v0.2](shadow06-figures-spec-v0.2.md) together with the [v0.3 changes](shadow06-figures-spec-v0.3.md). The latter is the current figure specification. F4 and F7 still need complete primary-source citation metadata in parts of their supplied CSVs; the present source lines identify the supplied records and ledger IDs where available. See the [check notes](figures/CHECK.md) before quoting those tables.

The palette and typography follow the published [Shadow 04 landing](https://github.com/MaksymDS/shadow-crack-landing) design system (commit `2a3e144d76c3ffb66c44e1d6196df81a06087c9d`). The light and dark SVGs use that system's figure styling. Inter and JetBrains Mono are bundled for offline rendering, with provenance and licences in [`figures/fonts/`](figures/fonts/README.md).

The [landing repository](https://github.com/MaksymDS/shadow-floor-landing) contains the HTML preview and copies of the web-ready figure SVGs and tables. This repository remains the source for data, scripts, PDF exports, and checks.
