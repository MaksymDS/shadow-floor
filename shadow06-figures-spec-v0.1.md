# Noise Floor — Figure Specifications v0.1 (Ch. 1, 3, 6, 7)

**Data folder:** `shadow06-figdata/` (one CSV per figure, values copied from PRIMARY ledger rows only)
**Style:** reuse the Shadow 04 landing/PDF design system exactly (palette, fonts, components). No new colours.
**Rules for every figure:**
- Source line under each figure: outlet/author, document title, date, ledger row IDs.
- Vendor-sourced data labelled "vendor data" in the source line.
- No figure shows a value that is not in its CSV. No interpolation, no smoothing, no trend lines unless stated.
- Accessible: direct labels on lines/bars; do not rely on colour alone.

---

## F1 — Signs of AI authorship by web domain, 2021–2026 (Ch. 1.1)
**Data:** `F1_pew_domain_share.csv` — Pew Research Center, 11 Common Crawl snapshots, % of sampled pages with significant signs of AI authorship (rows A01–A05).
**Form:** line chart, x = crawl date (Jan 2021 → Jan 2026, half-yearly), y = % (0–10). Four lines: .com, .org, .edu, .gov. Direct end-labels: ".com 9.35%", ".org 4.59%", ".edu 1.03%", ".gov 0.76%".
**Annotation:** vertical marker at Nov 2022 — "ChatGPT released".
**Caption:** "Before ChatGPT, every domain sat near 1%. By January 2026, almost one in ten .com pages showed signs of AI authorship — ten times the rate on .edu and .gov."
**Caveat line (mandatory):** "Pew's detector flags pages written *or substantially edited* with AI and misclassifies individual pages in both directions; Pew notes a higher false-positive rate on pre-AI pages." (A05, A06)
**Note:** Pew states plotted points are six-month averages — say so in the source line.

## F2 — Music: half of what is uploaded, a sliver of what is heard (Ch. 1.2)
**Data:** `F2_deezer_uploads_vs_streams.csv` — Deezer newsroom (rows A26–A28). PRIMARY points only: Jan 2025, Apr 2026, Jun 2026.
**Form:** paired horizontal bars for Jun 2026: "Share of daily uploads: >50%" vs "Share of streams: 1–3%" (draw 1–3% as a range band). Small inset: AI tracks per day — 10,000 (Jan 2025) → 75,000 (Apr 2026) → 90,000 (Jun 2026) as three labelled dots, not a continuous line.
**Caption:** "Fully AI-generated tracks passed half of Deezer's daily uploads in June 2026, yet accounted for 1–3% of listening; Deezer found up to 85% of their streams were fraudulent."
**Do not:** add intermediate points (Jun 2025, Jan 2026) — not PRIMARY.

## F3 — arXiv monthly submissions (Ch. 1.5 / Ch. 5.1)
**Data:** `F3_arxiv_submissions.csv` — arXiv blog, 1 Oct 2026 (rows F01–F03).
**Form:** three bars: Sep 2016 9,869 · Sep 2024 20,569 · Sep 2026 40,363. Callout on the 2026 bar: "≈9,000 support tickets". Side note: "cs.AI submissions: more than 6× in 2024–2026; other categories roughly doubled."
**Caption:** "Submissions doubled in two years. From 1 October 2026 each submitter may send two papers a month — rejected ones count."
**Counterweight in caption or footnote:** "arXiv attributes a disproportionate share of moderator time to a relatively small proportion of authors." (F05, Z11)

## F5 — How a text watermark fades (Ch. 3.3)
**Data:** `F5_openai_text_watermark.csv` — OpenAI, "Our approach to EU text provenance rules", 5 Oct 2026 (rows B13–B15). Verified by Claude (COI-2).
**Form:** two small panels.
 - Panel A "Length": bars 200 tokens 80% · 400 tokens 95%.
 - Panel B "Editing": step bars 0% → 92% · 10% → 66% · 25% → 17%.
**Caption:** "At a 1% false-positive target, replacing a quarter of the words with synonyms reduced detection from 92% to 17%. Detection was substantially lower for mathematics."
**Note:** state that these are the provider's own evaluations, on English ELI5 answers.

## F9 — Practice versus exam (Ch. 6.1)
**Data:** `F9_bastani.csv` — Bastani et al., PNAS 122(26), 2025 (rows D01–D02).
**Form:** grouped bars, two groups (Practice, Exam without AI), two arms (GPT Base, GPT Tutor); zero line = control group. Labels: +48%, −17%, +127%, ≈0.
**Caption:** "Unrestricted access improved practice scores by 48% and lowered exam scores by 17% once access was removed. A tutor designed not to hand out answers removed the loss."
**Companion line (no chart):** Fan et al. (BJET) — ChatGPT group improved essay scores most; knowledge gain and transfer did not differ (D08).

## F10 — UK undergraduates and AI, 2024–2026 (Ch. 6.2)
**Data:** `F10_hepi.csv` — HEPI/Kortext Student Generative AI Survey 2026 (rows E04–E05).
**Form:** three small multiples (2024/2025/2026): any AI use 66 → 92 → 95; GenAI for assessed work — (2024: "just over half", not plotted as number) → 89 → 94; AI text inserted directly 3 → 8 → 12.
**Caption:** "Use is near-universal; direct insertion of AI text into assessed work is a minority practice — 12% in 2026."
**Mandatory pairing:** the student quote "I'm not using my brain at all" appears only next to the split: 49% better / 16% worse / 35% no impact (E06).

## F11 — 88 to 1 (Ch. 7.1)
**Data:** `F11_moltbook.csv` — Wiz, "Hacking Moltbook", Feb 2026 (rows H03–H05).
**Form:** typographic figure, not a chart: "1,500,000 registered agents" over "17,000 human owners", with "88 : 1" large. Footnote: "Wiz: the platform had no mechanism to verify whether an 'agent' was AI or a human running a script."

---

## Deferred until GPT Task 01 returns
- F4 (Ch. 2 institution × decision matrix) — depends on I01 verdict.
- F6 (Ch. 3 lab symmetry B-SYM) — Anthropic column filled by GPT only.
- F7 (Ch. 4 regulation matrix) — depends on C-block promotions.
- F8 (Ch. 5 ad-fraud estimate range) — vendor rows, GPT Part 2.
