#!/usr/bin/env python3
"""Read plotted SVG marks back and compare their values and geometry to CSVs."""

from __future__ import annotations

import csv
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from pypdf import PdfReader
from render import TABLES, TOKENS, source_lines, use_category

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = ROOT / "shadow06-figdata"
FIGURES = {
    "F1": "F1_pew_domain_share.csv",
    "F2": "F2_deezer_uploads_vs_streams.csv",
    "F3": "F3_arxiv_submissions.csv",
    "F4": "F4_institutions_decisions.csv",
    "F6": "F6_providers.csv",
    "F7": "F7_obligations.csv",
    "F8": "F8_vendor_methods.csv",
    "F9": "F9_learning_study.csv",
    "F10": "F10_hepi.csv",
    "F11": "F11_moltbook.csv",
}
SPECIFIED_TEXT = {
    "F1": ["Pew's detector flags pages written or substantially edited with AI, and misclassifies individual pages in both directions. Points are six-month averages; Pew reports a higher false-positive rate on pre-AI pages.",
           "Nov 2022"],
    "F9": ["Unrestricted access raised practice scores by 48% and was followed by exam scores 17% below the control group once access was removed. For a tutor designed not to hand out answers, the authors report the loss was largely mitigated."],
    "F11": ["About 1.5 million registered 'agents' and about 17,000 human owners, according to the Wiz investigation. Registrations do not measure activity or autonomy; the platform had no mechanism to verify whether an 'agent' was AI.",
            "Database state before the first fix, 31 Jan 2026. Registrations and owner records — not activity."],
}
SPEC_TEXT_LABELS = {
    "F1": {"caption": "**Caption (replace):**", "source": "**Source line must state:**"},
    "F2": {"caption": "**Caption (replace):**"},
    "F3": {"caption": "**Caption (replace):**", "callout": "**Callout (replace):**", "source": "**Source line must state:**"},
    "F8": {"title": "**Title (replace):**"},
    "F9": {"companion": "**Companion line (replace):**", "axis_label": "**Axis/label note:**", "source": "**Source line must state:**"},
    "F10": {"source": "**Source line must state:**"},
    "F11": {"title": "**Title (replace):**", "source": "**Source line must state:**"},
}


def specified_text():
    """Read the quoted target strings from the supplied specification itself."""
    specification = (OUT / "TEXT.md").read_text(encoding="utf-8")
    expected = {}
    for figure_id, labels in SPEC_TEXT_LABELS.items():
        section = re.search(rf"^## {figure_id} —[^\n]*\n(.*?)(?=^## |\Z)", specification,
                            re.MULTILINE | re.DOTALL)
        assert section, f"Specification section missing for {figure_id}"
        expected[figure_id] = {}
        for role, label in labels.items():
            lines = [line for line in section.group(1).splitlines() if line.startswith(label)]
            assert len(lines) == 1, f"Specification field missing for {figure_id} {role}"
            quoted = re.findall(r'"([^"]+)"', lines[0])
            assert len(quoted) == 1, f"Specification target ambiguous for {figure_id} {role}"
            expected[figure_id][role] = quoted[0]
    return expected


def spec_output_text(figure_id, role, path):
    root = ET.parse(path).getroot()
    if role == "title":
        title = root.find("{http://www.w3.org/2000/svg}title")
        visible = [el.text for el in root if el.tag.rsplit("}", 1)[-1] == "text"
                   and el.attrib.get("x") == "52" and el.attrib.get("y") == "78"]
        assert title is not None and len(visible) == 1 and title.text == visible[0]
        return title.text or ""
    groups = [el for el in root.iter() if el.attrib.get("data-text-role") == role]
    assert len(groups) == 1, f"{path}: expected one {role} text group"
    rendered = " ".join(el.text or "" for el in groups[0]
                        if el.tag.rsplit("}", 1)[-1] == "text")
    if role == "source":
        assert rendered.startswith("SOURCE  ")
        return rendered[len("SOURCE  "):]
    return rendered


def check_spec_text(figure_id, fields):
    for role, expected in fields.items():
        for suffix in (".svg", ".dark.svg"):
            path = OUT / f"{figure_id}{suffix}"
            actual = spec_output_text(figure_id, role, path)
            assert actual == expected, f"{path}: {role}: {actual!r} != {expected!r}"
        pdf_text = normal(PdfReader(OUT / f"{figure_id}.pdf").pages[0].extract_text())
        assert expected in pdf_text, f"{figure_id}.pdf: missing specified {role} text"
        if figure_id == "F8" and role == "title":
            table = unescape((OUT / "F8.table.html").read_text(encoding="utf-8"))
            assert f"<h1>{expected}</h1>" in table and f"<caption>{expected}</caption>" in table


def csv_rows(filename):
    with (DATA / filename).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def expected_keys(figure_id, data):
    if figure_id in TABLES:
        return {(i, field) for i in range(len(data))
                for _, _, fields in TABLES[figure_id]["columns"] for field in fields}
    if figure_id == "F1":
        return {(i, field) for i in range(len(data)) for field in ("com", "org", "edu", "gov")}
    if figure_id == "F2":
        return ({(i, "ai_tracks_per_day") for i in range(3)} |
                {(i, "share_of_daily_uploads_label") for i in (1, 2)} |
                {(2, "share_of_streams_label")})
    if figure_id == "F3":
        return {(i, "submissions") for i in range(3)}
    if figure_id == "F9":
        return ({(i, "practice_vs_control_pct") for i in range(2)} |
                {(0, "exam_vs_control_pct")} |
                {(i, field) for i in range(2) for field in ("arm", "exam_label")})
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
    kind = el.tag.rsplit("}", 1)[-1]
    i = int(a["data-row"])
    if figure_id == "F9" and field in ("arm", "exam_label"):
        return kind == "text" and (el.text or "") == row[field]
    if figure_id == "F2":
        if field == "ai_tracks_per_day":
            return kind == "circle" and close(a["cx"], (185, 595, 1005)[i]) and close(a["cy"], 495)
        if field == "share_of_daily_uploads_label":
            if i == 1:
                return kind == "text" and (el.text or "") == row[field]
            return kind == "rect" and close(a["x"], 340) and close(a["width"], 50 * 14)
        return kind == "rect" and close(a["x"], 340 + 14) and close(a["width"], 28)
    val = float(row[field])
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
    if figure_id == "F3":
        expected_y = 480 - val / 45000 * 315
        return kind == "rect" and close(a["y"], expected_y) and close(a["height"], 480 - expected_y)
    if figure_id == "F9":
        scale = 252 / 160
        zero = 430 - 20 * scale
        expected_y = zero - val * scale
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
        field = key[1]
        source = data[key[0]][key[1]]
        if not source or a["data-value"] != source:
            raise AssertionError(f"{path}: value mismatch {key}: {a['data-value']} != {source}")
        if not geometry_ok(figure_id, el, data[key[0]], key[1], data):
            raise AssertionError(f"{path}: geometry mismatch {key}")
        seen[key] = a["data-value"]
    if set(seen) != expected:
        raise AssertionError(f"{path}: missing marks {sorted(expected - set(seen))}")
    if figure_id == "F11":
        assert not any(el.attrib.get("data-derived") == "ratio" for el in root.iter())
        assert root.find("{http://www.w3.org/2000/svg}title").text == "1.5 million registrations, 17,000 owners"
        assert "6,159" not in " ".join(el.text or "" for el in root.iter())
        assert data[0]["date_or_window"] == "database state before first fix, 31 Jan 2026"
        assert data[0]["definition"] == "registrations" and data[1]["definition"] == "owner records"
    if figure_id == "F9":
        assert data[1]["exam_vs_control_pct"] == ""
        assert not any(el.attrib.get("data-row") == "1" and el.attrib.get("data-field") == "exam_vs_control_pct"
                       for el in root.iter())
    if figure_id in SPECIFIED_TEXT:
        whole = normal(" ".join(el.text or "" for el in root.iter()
                                if el.tag.rsplit("}", 1)[-1] == "text"))
        for phrase in SPECIFIED_TEXT[figure_id]:
            assert normal(phrase) in whole, f"{path}: missing specified wording {phrase!r}"
    return seen


def normal(s):
    return " ".join(s.split())


def inspect_table_svg(path, figure_id, data, expected):
    root = ET.parse(path).getroot()
    seen = {}
    for group in root.iter():
        a = group.attrib
        if group.tag.rsplit("}", 1)[-1] != "g" or "data-field" not in a:
            continue
        key = (int(a["data-row"]), a["data-field"])
        assert key in expected and key not in seen, f"{path}: unexpected or repeated cell {key}"
        source = data[key[0]][key[1]]
        rendered = normal(" ".join(child.text or "" for child in group))
        assert a["data-value"] == source, f"{path}: encoded mismatch {key}"
        assert rendered == normal(source), f"{path}: visible mismatch {key}: {rendered!r} != {source!r}"
        seen[key] = rendered
    assert set(seen) == expected, f"{path}: missing cells {sorted(expected - set(seen))}"
    spec = TABLES[figure_id]
    whole = normal(" ".join(el.text or "" for el in root.iter()
                            if el.tag.rsplit("}", 1)[-1] == "text"))
    for phrase in (spec["title"], spec["caption"], spec["note"],
                   *(spec.get("notes") or []), *source_lines(figure_id)):
        if phrase:
            assert normal(phrase) in whole, f"{path}: missing specified text {phrase!r}"
    if figure_id == "F4":
        bars = {int(el.attrib["data-use-row"]): el.attrib for el in root.iter()
                if "data-use-row" in el.attrib}
        assert len(bars) == len(data)
        for i, row in enumerate(data):
            category = use_category(row["use"])
            assert bars[i]["data-use-category"] == category
            assert bars[i]["fill"] == {"measure": TOKENS["slate"], "screen": TOKENS["muted"],
                                       "guidance": "#7B8588", "discontinued": TOKENS["rule"],
                                       "reviewed": TOKENS["cream"] if path.name.endswith(".dark.svg") else TOKENS["bg"]}[category]
    if figure_id == "F6":
        provider_styles = {}
        for group in root.iter():
            if group.attrib.get("data-field") not in ("anthropic", "google", "openai"):
                continue
            provider_styles.setdefault(int(group.attrib["data-row"]), []).append(
                tuple(group[0].attrib[key] for key in ("fill", "font-size", "font-weight")))
        assert len(provider_styles) == len(data)
        assert all(len(styles) == 3 and len(set(styles)) == 1 for styles in provider_styles.values())
    if figure_id == "F7":
        order = [int(el.attrib["data-row"]) for el in root.iter()
                 if el.attrib.get("data-field") == "jurisdiction"]
        assert order == list(range(len(data)))
        group_headers = [el.attrib["data-group-header"] for el in root.iter()
                         if "data-group-header" in el.attrib]
        assert group_headers == list(dict.fromkeys(row["group"] for row in data))
        group_rows = {int(el.attrib["data-group-row"]): el.attrib["data-group-value"]
                      for el in root.iter() if "data-group-row" in el.attrib}
        assert group_rows == {i: row["group"] for i, row in enumerate(data)}
        shaded = {int(el.attrib["data-verification-row"]): el.attrib for el in root.iter()
                  if "data-verification-row" in el.attrib}
        expected_shaded = {i for i, row in enumerate(data) if row["clearance"] == "located, not cleared"}
        assert set(shaded) == expected_shaded
        assert all(a["fill"] == TOKENS["muted"] and a["fill-opacity"] == "0.18"
                   for a in shaded.values())
    return seen


class TableHTMLReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = {}
        self.current = None
        self.bits = []
        self.tables = 0
        self.col_headers = 0
        self.row_headers = 0
        self.groups = []
        self.row_metadata = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.tables += 1
        if tag == "th" and a.get("scope") == "col":
            self.col_headers += 1
        if tag == "th" and a.get("scope") == "row":
            self.row_headers += 1
        if tag == "tbody" and a.get("aria-label"):
            self.groups.append(a["aria-label"])
        if tag == "tr" and "data-group" in a:
            self.row_metadata.append(a)
        if tag == "span" and "data-field" in a:
            assert self.current is None
            self.current = (int(a["data-row"]), a["data-field"], a["data-value"])
            self.bits = []

    def handle_data(self, data):
        if self.current is not None:
            self.bits.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.current is not None:
            row, field, encoded = self.current
            key = (row, field)
            assert key not in self.cells
            self.cells[key] = (encoded, normal("".join(self.bits)))
            self.current = None


def inspect_table_html(path, figure_id, data, expected):
    reader = TableHTMLReader()
    reader.feed(path.read_text(encoding="utf-8"))
    assert reader.tables == 1
    assert reader.col_headers == len(TABLES[figure_id]["columns"])
    assert reader.row_headers == len(data)
    assert set(reader.cells) == expected
    for key in expected:
        source = data[key[0]][key[1]]
        assert reader.cells[key] == (source, normal(source)), f"{path}: HTML cell mismatch {key}"
    if figure_id == "F6":
        for note in TABLES["F6"]["notes"]:
            assert note in unescape(path.read_text(encoding="utf-8"))
        for source in source_lines("F6"):
            assert source in unescape(path.read_text(encoding="utf-8"))
    spec = TABLES[figure_id]
    rendered_html = unescape(path.read_text(encoding="utf-8"))
    for phrase in (spec["caption"], spec["note"], *(spec.get("notes") or []), *source_lines(figure_id)):
        if phrase:
            assert phrase in rendered_html, f"{path}: missing exact caption, note or source: {phrase!r}"
    if figure_id == "F7":
        assert reader.groups == list(dict.fromkeys(row["group"] for row in data))
        assert len(reader.row_metadata) == len(data)
        for metadata, row in zip(reader.row_metadata, data):
            assert metadata["data-group"] == row["group"]
            assert metadata["data-clearance"] == row["clearance"]
            assert ("unverified" in metadata.get("class", "")) == (row["clearance"] == "located, not cleared")
    return {key: value[1] for key, value in reader.cells.items()}


def pdf_ok(figure_id, data):
    pdf = PdfReader(OUT / f"{figure_id}.pdf")
    assert len(pdf.pages) == 1
    svg_root = ET.parse(OUT / f"{figure_id}.svg").getroot()
    assert float(pdf.pages[0].mediabox.width) == float(svg_root.attrib["width"])
    assert float(pdf.pages[0].mediabox.height) == float(svg_root.attrib["height"])
    content = pdf.pages[0].extract_text()
    assert content and "SHADOW 06" in content and "SOURCE" in content
    fonts = pdf.pages[0]["/Resources"]["/Font"]
    embedded_names = " ".join(str(fonts[k].get_object().get("/BaseFont")) for k in fonts)
    assert "Inter" in embedded_names and "JetBrainsMono" in embedded_names
    if figure_id in TABLES:
        assert TABLES[figure_id]["title"] in content
        for phrase in (TABLES[figure_id]["caption"], TABLES[figure_id]["note"],
                       *(TABLES[figure_id].get("notes") or []), *source_lines(figure_id)):
            if phrase:
                assert normal(phrase) in normal(content), f"{figure_id}.pdf: missing caption, note or source"
    if figure_id == "F11":
        assert f"{int(data[0]['value']):,}" in content and f"{int(data[1]['value']):,}" in content


def main():
    assert not any((OUT / f"F5{suffix}").exists() for suffix in
                   (".svg", ".dark.svg", ".pdf", ".py", ".table.html"))
    spec_text = specified_text()
    spec_text["F2"]["source"] = "; ".join(row["source"] for row in csv_rows(FIGURES["F2"]))
    lines = [
        "# Shadow 06 figure check",
        "",
        "Generated by `python figures/check.py` after reading plotted marks and table cells back "
        "from both SVG themes. Charts are checked against CSV values and geometry; table cell "
        "text is checked against the CSV in SVG and accessible HTML. Captions, notes and source "
        "lines are checked in both SVGs, HTML tables and PDFs. PDFs are checked for one "
        "vector page, extractable text, and embedded Shadow fonts.",
        "",
        "| Figure | CSV | Every plotted or tabulated value read back | Result |",
        "|:--|:--|:--|:--|",
    ]
    for figure_id, filename in FIGURES.items():
        data = csv_rows(filename)
        expected = expected_keys(figure_id, data)
        inspect = inspect_table_svg if figure_id in TABLES else inspect_svg
        light = inspect(OUT / f"{figure_id}.svg", figure_id, data, expected)
        dark = inspect(OUT / f"{figure_id}.dark.svg", figure_id, data, expected)
        assert light == dark
        if figure_id in TABLES:
            table = inspect_table_html(OUT / f"{figure_id}.table.html", figure_id, data, expected)
            assert table == light
        pdf_ok(figure_id, data)
        if figure_id in spec_text:
            check_spec_text(figure_id, spec_text[figure_id])
        values = []
        for i, field in sorted(light):
            row_label = (data[i].get("actor") or data[i].get("field") or data[i].get("jurisdiction") or
                         data[i].get("vendor") or data[i].get("crawl_date") or data[i].get("period") or
                         data[i].get("month") or data[i].get("year") or data[i].get("condition") or
                         data[i].get("arm") or data[i].get("metric"))
            values.append(f"{row_label} {field}={light[(i, field)]}")
        result = "Yes (both SVGs and HTML); PDF page/fonts checked" if figure_id in TABLES else "Yes (both SVGs); PDF page/fonts checked"
        lines.append(f"| {figure_id} | `{filename}` | {'<br>'.join(values)} | {result} |")
    lines += [
        "",
        "## Figure text audit",
        "",
        "Each specified field below was read back from the light and dark SVG and compared character for "
        "character with `figures/TEXT.md` or, for the F2 source, the CSV, after joining wrapped lines "
        "with spaces. Extractable PDF text was also checked after line reflow; F8's standalone "
        "HTML heading and table caption were checked too.",
        "",
        "| Figure | Field | Exact specification text | Output check |",
        "|:--|:--|:--|:--|",
    ]
    for figure_id, fields in spec_text.items():
        for role, expected in fields.items():
            result = "Exact in both SVGs and PDF"
            if figure_id == "F8":
                result += "; HTML heading and caption"
            lines.append(f"| {figure_id} | {role.replace('_', ' ')} | {expected} | {result} |")
    lines += [
        "",
        "## Strict readings and source discrepancies",
        "",
        "- F2: the June bar ends at the 50% tick, carries a ≥ marker and is labelled `over 50%`; January 2025 has no upload-share claim. The `up to 85%` fraud statement is specified prose, not a plotted CSV value.",
        "- F1: the source names Pew and states that plotted points are six-month averages. The detector caveat remains visible.",
        "- F5: withdrawn. Its material appears in F6; no F5 data or export is included.",
        "- F4: all eight institutional rows and five use tones follow the CSV. Its caption does not claim a measured trend.",
        "- F6: provider columns follow alphabetical order. Every cell retains the CSV wording; the source block is checked against all three rows of `F6_sources.csv`. The footnotes caution against ranking providers.",
        "- F7: all 26 CSV rows remain grouped in supplied order. Rows marked `located, not cleared` retain neutral shading. The United Kingdom briefing appears as a note, outside the table; Nigeria remains excluded. The caption omits the future 18 October evidence freeze pending completion.",
        "- F9: the Tutor with safeguards exam cell is blank in the new CSV. No mark or bar is drawn; its exact `exam_label` appears at the zero line. The companion text avoids treating a non-significant difference as equality.",
        "- F8: reported figures are presented as vendor reports from different periods, samples and units; no combined range is inferred.",
        "- F10: the 2024 assessed-work cell is blank. No bar is drawn and the specified qualitative note appears. The student quote and 49/16/35 split are omitted together because those percentages are absent from the frozen CSV.",
        "- F11: the unsupported agent-per-owner ratio has been removed. The two counts, source date and registration caveat remain visible.",
        "",
    ]
    (OUT / "CHECK.md").write_text("\n".join(lines), encoding="utf-8")
    print("Checked 10 active figures; F5 withdrawn. Every SVG mark/table cell matches its CSV; HTML tables and PDFs checked.")


if __name__ == "__main__":
    main()
