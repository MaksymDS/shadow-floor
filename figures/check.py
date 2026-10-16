#!/usr/bin/env python3
"""Read plotted SVG marks back and compare their values and geometry to CSVs."""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = ROOT / "shadow06-figdata"
FIGURES = {
    "F1": "F1_pew_domain_share.csv",
    "F2": "F2_deezer_uploads_vs_streams.csv",
    "F3": "F3_arxiv_submissions.csv",
    "F5": "F5_openai_text_watermark.csv",
    "F9": "F9_bastani.csv",
    "F10": "F10_hepi.csv",
    "F11": "F11_moltbook.csv",
}


def csv_rows(filename):
    with (DATA / filename).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def expected_keys(figure_id, data):
    if figure_id == "F1":
        return {(i, field) for i in range(len(data)) for field in ("com", "org", "edu", "gov")}
    if figure_id == "F2":
        return ({(i, "ai_tracks_per_day") for i in range(3)} |
                {(2, field) for field in ("share_of_daily_uploads_pct",
                                          "share_of_streams_pct_low", "share_of_streams_pct_high")})
    if figure_id == "F3":
        return {(i, "submissions") for i in range(3)}
    if figure_id == "F5":
        return {(i, "detection_rate_pct") for i in range(5)}
    if figure_id == "F9":
        return {(i, field) for i in range(2) for field in
                ("practice_vs_control_pct", "exam_vs_control_pct")}
    if figure_id == "F10":
        return {(i, field) for i in range(3) for field in
                ("any_ai_use_pct", "genai_for_assessed_work_pct", "ai_text_inserted_directly_pct")
                if data[i][field]}
    return {(0, "value"), (1, "value")}


def close(a, b, tolerance=0.003):
    return abs(float(a) - float(b)) <= tolerance


def actual_point(el):
    a = el.attrib
    kind = el.tag.rsplit("}", 1)[-1]
    if kind == "circle":
        return float(a["cx"]), float(a["cy"])
    if kind == "rect":
        return float(a["x"]) + float(a["width"]) / 2, float(a["y"]) + float(a["height"]) / 2
    if kind == "path":
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", a["d"])]
        return nums[0], nums[1]
    raise AssertionError(kind)


def geometry_ok(figure_id, el, row, field, data):
    a = el.attrib
    val = float(row[field])
    kind = el.tag.rsplit("}", 1)[-1]
    i = int(a["data-row"])
    if figure_id == "F1":
        from datetime import date
        start, end = date.fromisoformat(data[0]["crawl_date"]), date.fromisoformat(data[-1]["crawl_date"])
        d = date.fromisoformat(row["crawl_date"])
        x = 110 + (d - start).days / (end - start).days * 780
        y = 510 - val / 10 * 345
        px, py = actual_point(el)
        if field == "edu":
            return close(px, x) and close(py, y - 5)  # first diamond vertex
        if field == "gov":
            return close(px, x) and close(py, y - 6)  # triangle apex
        return close(px, x) and close(py, y)
    if figure_id == "F2":
        if field == "ai_tracks_per_day":
            return kind == "circle" and close(a["cx"], (185, 595, 1005)[i]) and close(a["cy"], 495)
        if field == "share_of_daily_uploads_pct":
            return kind == "rect" and close(a["x"], 340) and close(a["width"], val * 14)
        if field == "share_of_streams_pct_low":
            high = float(row["share_of_streams_pct_high"])
            return kind == "rect" and close(a["x"], 340 + val * 14) and close(a["width"], (high - val) * 14)
        return kind == "line" and close(a["x1"], 340 + val * 14) and close(a["x2"], 340 + val * 14)
    if figure_id == "F3":
        expected_y = 480 - val / 45000 * 315
        return kind == "rect" and close(a["y"], expected_y) and close(a["height"], 480 - expected_y)
    if figure_id == "F5":
        expected_y = 445 - val / 100 * 255
        return kind == "rect" and close(a["y"], expected_y) and close(a["height"], 445 - expected_y)
    if figure_id == "F9":
        scale = 252 / 160
        zero = 430 - 20 * scale
        expected_y = zero - val * scale
        if val == 0:
            return kind == "line" and close(a["y1"], zero) and close(a["y2"], zero)
        return kind == "rect" and close(a["y"], min(zero, expected_y)) and close(a["height"], abs(zero - expected_y))
    if figure_id == "F10":
        panel = ("any_ai_use_pct", "genai_for_assessed_work_pct", "ai_text_inserted_directly_pct").index(field)
        return (kind == "rect" and close(a["x"], 52 + panel * 380 + 69) and
                close(a["width"], val * 2.15) and close(a["y"], 210 + i * 105 - 20))
    return kind == "text" and (el.text or "").replace(",", "") == row[field]


def inspect_svg(path, figure_id, data, expected):
    tree = ET.parse(path)
    root = tree.getroot()
    seen = {}
    for el in root.iter():
        a = el.attrib
        if "data-row" not in a:
            continue
        key = (int(a["data-row"]), a["data-field"])
        if key in seen:
            raise AssertionError(f"{path}: duplicate plotted mark {key}")
        if key not in expected:
            raise AssertionError(f"{path}: extra plotted mark {key}")
        source = data[key[0]][key[1]]
        if not source or Decimal(a["data-value"]) != Decimal(source):
            raise AssertionError(f"{path}: value mismatch {key}: {a['data-value']} != {source}")
        if not geometry_ok(figure_id, el, data[key[0]], key[1], data):
            raise AssertionError(f"{path}: geometry mismatch {key}")
        seen[key] = a["data-value"]
    if set(seen) != expected:
        raise AssertionError(f"{path}: missing marks {sorted(expected - set(seen))}")
    if figure_id == "F11":
        ratio = [el for el in root.iter() if el.attrib.get("data-derived") == "ratio"]
        agents, owners = (int(r["value"]) for r in data)
        assert len(ratio) == 1 and (ratio[0].text or "").strip() == f"{round(agents / owners)} : 1"
    return seen


def pdf_ok(figure_id, data):
    pdf = PdfReader(OUT / f"{figure_id}.pdf")
    assert len(pdf.pages) == 1
    content = pdf.pages[0].extract_text()
    assert content and "SHADOW 06" in content and "SOURCE" in content
    fonts = pdf.pages[0]["/Resources"]["/Font"]
    embedded_names = " ".join(str(fonts[k].get_object().get("/BaseFont")) for k in fonts)
    assert "Inter" in embedded_names and "JetBrainsMono" in embedded_names
    if figure_id == "F11":
        assert f"{int(data[0]['value']):,}" in content and f"{int(data[1]['value']):,}" in content


def main():
    lines = [
        "# Shadow 06 figure check",
        "",
        "Generated by `python figures/check.py` after reading plotted marks back from both SVG themes. "
        "Each mark's displayed geometry and encoded value are checked against the frozen CSV; "
        "the PDF is checked for one vector page, extractable text, and embedded Shadow fonts.",
        "",
        "| Figure | CSV | Every plotted value read back from SVG | Matches CSV and geometry? |",
        "|:--|:--|:--|:--|",
    ]
    for figure_id, filename in FIGURES.items():
        data = csv_rows(filename)
        expected = expected_keys(figure_id, data)
        light = inspect_svg(OUT / f"{figure_id}.svg", figure_id, data, expected)
        dark = inspect_svg(OUT / f"{figure_id}.dark.svg", figure_id, data, expected)
        assert light == dark
        pdf_ok(figure_id, data)
        values = []
        for i, field in sorted(light):
            row_label = data[i].get("crawl_date") or data[i].get("period") or data[i].get("month") or data[i].get("year") or data[i].get("condition") or data[i].get("arm") or data[i].get("metric")
            values.append(f"{row_label} {field}={light[(i, field)]}")
        lines.append(f"| {figure_id} | `{filename}` | {'<br>'.join(values)} | Yes (both SVGs); PDF page/fonts checked |")
    lines += [
        "",
        "## Strict readings and source discrepancies",
        "",
        "- F2: the spec asks for `>50%` daily uploads in June 2026, but the frozen CSV records `50`. The bar and direct label use `50%`; the exact supplied caption retains its wording. The caption's `up to 85%` fraud claim is specified prose, not a plotted value in the CSV.",
        "- F5: the spec describes English ELI5 answers, while the CSV calls the length-panel content psychology. The figure explicitly identifies both descriptions; it does not reconcile them by inventing data.",
        "- F10: the 2024 assessed-work cell is blank. No bar is drawn and the specified qualitative note appears. The student quote and 49/16/35 split are omitted together because those percentages are absent from the frozen CSV.",
        "- F11: `88 : 1` is the spec's rounded ratio of the two CSV counts (1,500,000 / 17,000 ≈ 88.24); it is not an independent observation.",
        "- F1/F3/F9: the supplied spec omits exact source titles or dates in some cases. Those metadata were checked against the primary Pew, arXiv and PNAS/PubMed pages; no additional values were plotted.",
        "- F4, F6, F7 and F8 were deferred by the supplied task and are not produced.",
        "",
    ]
    (OUT / "CHECK.md").write_text("\n".join(lines), encoding="utf-8")
    print("Checked 7 figures: every SVG mark matches its CSV value and geometry; PDFs contain embedded Shadow fonts.")


if __name__ == "__main__":
    main()
