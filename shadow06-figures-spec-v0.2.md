# Noise Floor — Figure Specifications v0.2 (supersedes v0.1)

**Changes vs v0.1:** F1 caveat corrected; F5 caption neutral (provider's own evaluation); F11 moved to Ch. 2 with corrected caption; F4, F6, F7 added; F8 changed from range chart to methodology table. F2, F3, F9, F10 unchanged.
**Data:** `shadow06-figdata/` · **Style:** Shadow 04 design system exactly · **Rules:** as v0.1 (only CSV values; source line under every figure; vendor data labelled; greyscale-safe; direct labels).
**Vendor wording rule (tier P-A):** captions for vendor or company data use "X reports…".

---

## F1 — Signs of AI authorship by web domain, 2021–2026 (Ch. 1.1) — CAVEAT CORRECTED
Data/form/annotation/caption: as v0.1.
**Caveat line (replace v0.1 text):** "Pew's detector flags pages written *or substantially edited* with AI, and misclassifies individual pages in both directions. Points are six-month averages; Pew reports a higher false-positive rate on pre-AI pages." 

## F2 — unchanged (Ch. 1.2)
## F3 — unchanged (Ch. 1.5)

## F4 — Counting, screening, judging (Ch. 2) — NEW
**Data:** `F4_institutions_decisions.csv`
**Form:** table-figure, 7 rows. Columns: Actor · What is classified · Instrument · Use · Human step · Outcome. Colour-code the **Use** column in three neutral tones: *measure (aggregate)*, *screen*, *sanction / discontinued*. Row IDs in a small grey column at right.
**Caption:** "The same kind of classifier is used to estimate prevalence, to screen submissions, and — less and less — to judge individuals."
**Note under figure:** "Aggregate estimation and individual adjudication carry different error requirements (ICML 2024, Liang et al.)."

## F5 — How a text watermark fades (Ch. 3.3) — CAPTION NEUTRALISED
Data/form: as v0.1.
**Caption (replace):** "In OpenAI's own evaluation on English ELI5 answers at a 1% false-positive target, replacing a quarter of the words with synonyms reduced detection from 92% to 17%; detection was substantially lower for mathematics."
**Source line:** "OpenAI, 'Our approach to EU text provenance rules', 5 Oct 2026 — provider's own evaluation."

## F6 — Three labs, one table (Ch. 3.2) — NEW
**Data:** `F6_lab_symmetry.csv`
**Form:** comparison table, 6 rows × 3 lab columns, identical styling for every lab; no lab highlighted, no ticks/crosses implying ranking. Footnote: "Anthropic column verified by GPT (OpenAI model) under the issue's conflict-of-interest protocol; figures come from different implementations, corpora and operating points — no ranking is implied."
**Column order:** alphabetical (Anthropic, Google, OpenAI) — do not reorder.

## F7 — Who must mark what, at 16 October 2026 (Ch. 4) — NEW
**Data:** `F7_obligations.csv`
**Form:** matrix. Rows = jurisdictions in CSV order; columns = image/video/audio · text · deepfake label · platform duty · status. Cell text as in CSV (short). Rows with `verified = no` drawn with a hatched/grey background and the note "not verified to PRIMARY in English by cutoff".
**Caption:** "A comparison of specified obligations, not a ranking of countries' overall AI regulation."
**Do not:** add Kuwait or any jurisdiction not in the CSV; do not use colour to imply strict/lenient.

## F8 — Why ad-fraud figures do not add up (Ch. 5.4) — CHANGED to table
**Data:** `F8_vendor_methods.csv`
**Form:** methodology table (no bar or range chart). Columns: Vendor · Reported figure · Period · Unit · Sample · Extrapolation.
**Caption:** "Vendors measure different things — clicks, impressions, requests, schemes — over different periods and samples. The figures are not a range for one quantity."

## F9, F10 — unchanged (Ch. 6)

## F11 — 88 to 1 (now Ch. 2.7) — CAPTION CORRECTED
Data/form: as v0.1.
**Caption (replace):** "About 1.5 million registered 'agents' and about 17,000 human owners, according to the Wiz investigation. Registrations do not measure activity or autonomy; the platform had no mechanism to verify whether an 'agent' was AI."
**Do not:** add the 6,159 figure from the Holtz study to this graphic — different date and population.
