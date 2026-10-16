# Noise Floor — Figure Specifications v0.3 (delta on v0.2)

**Why this revision:** the conflict-of-interest rule COI-4 is now read strictly. Facts about specific AI labs appear in one comparison table only (F6). Captions and annotations elsewhere do not name labs or their products. Two further corrections: statistical non-significance must not be drawn as equality, and the regulation matrix is rebuilt with separate fields.
**Everything not listed here is unchanged from v0.2.** Rules as before: plot only CSV values; source line under every figure; greyscale-safe; direct labels; Shadow 04 design system.

---

## F1 — annotation and caption changed (Ch. 1.1)
- **Annotation (replace "ChatGPT released"):** "Nov 2022".
- **Caption (replace):** "Before late 2022, every domain sat near 1%. By January 2026, almost one in ten .com pages showed signs of AI authorship — ten times the rate on .edu and .gov."
- The source line may name Pew's own window definition; the graphic itself names no product.

## F2 — caption wording (Ch. 1.2)
- **Caption (replace):** "Fully AI-generated tracks passed half of Deezer's daily uploads in June 2026, yet accounted for 1–3% of streams; Deezer reports that up to 85% of their streams were fraudulent."

## F4 — one row changed (Ch. 2)
- **Data:** `F4_institutions_decisions.csv`, replacing the v0.2 file. The Newby row now reads "court review of one evidentiary record and disciplinary process" and "determination annulled on case-specific evidentiary and procedural grounds; no general finding on detectors".
- Caption and note unchanged.

## F5 — WITHDRAWN
- Delete the F5 outputs. The data now sits in the F6 "Published text robustness evaluation" row.
- If F5 was already built, keep the script out of the release and note the withdrawal in CHECK.md.

## F6 — Providers, one table (Ch. 3.2) — REBUILT
- **Data:** `F6_providers.csv`, replacing `F6_lab_symmetry.csv`.
- **Title:** "Providers, one table".
- **Form:** comparison table: 6 rows × 3 provider columns, plus a narrow grey "rows" column.
  - Columns in alphabetical order: Anthropic, Google, OpenAI. Do not reorder.
  - Identical styling for every column. No highlighting, ticks, crosses, colour scales or bolding of any cell.
- **Cell text:** exactly as in the CSV. The Anthropic cells were worded by GPT under the conflict-of-interest protocol. Do not shorten, paraphrase or "harmonise" them.
- **Footnote 1:** "Anthropic column verified and worded by GPT (OpenAI model); OpenAI rows verified by Claude (Anthropic model), under the issue's conflict-of-interest protocol."
- **Footnote 2:** "Figures come from different implementations, corpora and operating points. No ranking is implied."
- **Source line:** "Provider documentation and publications as listed in the ledger rows shown; verified 14–16 Oct 2026."

## F7 — Who must mark what (Ch. 4) — REBUILT
- **Data:** `F7_obligations.csv`, replacing the v0.2 file.
- **Form:** grouped table.
  - Groups in the CSV's `group` order: 1 Statute/regulation · 2 Election rule · 3 Sectoral/media standard · 4 Guidance/policy. Within each group, rows in CSV order (alphabetical).
  - Columns: Jurisdiction · Instrument · Issuer · Covered actor · Medium · Duty · Status · Effective date. The `rows` column is small and grey.
- **Rows with `clearance` = "located, not cleared":** grey or hatched background with "—" cells and the note "Official text located; not cleared for detailed description (language or access)". Use one neutral treatment for every such row, whatever the country.
- **Caption:** "Instruments we located and verified, as of 16 October 2026 (evidence freeze 18 October 2026). A comparison of specified obligations, not a ranking of countries' overall AI regulation."
- **Do not:**
  - add any jurisdiction that is not in the CSV — in particular, Kuwait is excluded;
  - use colour to imply strict or lenient;
  - merge Brazil's two rows or Australia's two rows.

## F9 — Practice versus exam (Ch. 6) — CHANGED
- **Data:** `F9_learning_study.csv`, replacing `F9_bastani.csv`. Arm names are generic: "Unrestricted assistant" and "Tutor with safeguards".
- **Form:** as v0.1, with one change.
  - The Tutor-with-safeguards exam cell has no value. Draw no bar there.
  - Place the text label "largely mitigated (authors)" at the zero line instead.
  - Never draw a zero-height bar or "≈0" for it.
- **Caption (replace):** "Unrestricted access raised practice scores by 48% and was followed by exam scores 17% below the control group once access was removed. For a tutor designed not to hand out answers, the authors report the loss was largely mitigated."
- **Companion line (replace):** "A separate randomised study (BJET, 2025; 117 students) found the strongest essays in the AI-assisted group and did not detect a statistically significant difference in knowledge gain or transfer."
- **Source line:** "Bastani et al., PNAS 122(26), 2025; Fan et al., BJET 56(2), 2025."

## F11 — 88 to 1 (Ch. 2.7) — date note added
- **Data:** `F11_moltbook.csv`, replacing the v0.2 file; it now carries dates and definitions.
- **Add under the numbers:** "Database state before the first fix, 31 Jan 2026; Wiz, published 2 Feb 2026. Registrations and owner records — not activity."
- **Do not** add any other count to this figure.

## F3, F8, F10 — unchanged.
