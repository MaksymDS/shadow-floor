#!/usr/bin/env python3
"""Offline, deterministic Shadow 06 figure renderer.

Data always comes from the frozen CSVs. SVG carries each mark's source row,
field and value so check.py can validate the rendered geometry independently.
"""

from __future__ import annotations

import csv
import datetime as dt
import html
from pathlib import Path
import re
import sys
import textwrap
import xml.etree.ElementTree as ET

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = ROOT / "shadow06-figdata"
W = 1200

# Literal Shadow 04 tokens from shadow-crack-landing/index.html and README.md.
TOKENS = {
    "bg": "#161819", "header": "#121415", "card": "#101213",
    "deep": "#0E0F10", "cream": "#EDE0C8", "muted": "#9C907A",
    "gold": "#E8B547", "red": "#C73E3A", "ochre": "#CC7722",
    "slate": "#6E8499", "darkred": "#8B2D2D", "rule": "#2A2D2F",
}
SANS = "Inter,Arial,sans-serif"
MONO = "JetBrains Mono,monospace"


def number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


class Figure:
    def __init__(self, figure_id: str, title: str, height: int, dark: bool):
        self.id, self.title, self.height, self.dark = figure_id, title, height, dark
        self.paper = TOKENS["bg"] if dark else TOKENS["cream"]
        self.ink = TOKENS["cream"] if dark else TOKENS["bg"]
        self.quiet = TOKENS["muted"] if dark else TOKENS["rule"]
        self.grid = TOKENS["rule"] if dark else TOKENS["muted"]
        self.accent = TOKENS["gold"] if dark else TOKENS["darkred"]
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title>',
            f'<desc id="desc">Shadow 06 figure {esc(figure_id)}. Exact plotted values are encoded on marks.</desc>',
            f'<rect width="{W}" height="{height}" fill="{self.paper}"/>',
        ]
        self.text(52, 36, f"SHADOW 06  /  FIGURE {figure_id[1:]}", 12, self.accent, MONO, 600)
        self.text(52, 78, title, 29, self.ink, SANS, 600)
        self.line(52, 98, W - 52, 98, self.grid, 1)

    def add(self, element: str):
        self.parts.append(element)

    def text(self, x, y, content, size=15, color=None, family=SANS, weight=400,
             anchor="start", extra=""):
        color = color or self.ink
        self.add(f'<text x="{number(x)}" y="{number(y)}" fill="{color}" '
                 f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" {extra}>{esc(content)}</text>')

    def wrapped(self, x, y, content, width=112, size=14, leading=22,
                color=None, family=SANS, weight=400):
        for i, line in enumerate(textwrap.wrap(content, width=width, break_long_words=False,
                                               break_on_hyphens=False)):
            self.text(x, y + i * leading, line, size, color, family, weight)
        return y + (i + 1) * leading

    def line(self, x1, y1, x2, y2, color=None, width=1, dash=None, extra=""):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{number(x1)}" y1="{number(y1)}" '
                 f'x2="{number(x2)}" y2="{number(y2)}" '
                 f'stroke="{color or self.grid}" stroke-width="{width}"{dash_attr} {extra}/>')

    def rect(self, x, y, width, height, fill=None, extra=""):
        self.add(f'<rect x="{number(x)}" y="{number(y)}" '
                 f'width="{number(width)}" height="{number(height)}" '
                 f'fill="{fill or self.accent}" {extra}/>')

    def circle(self, x, y, radius=5, fill=None, extra=""):
        self.add(f'<circle cx="{number(x)}" cy="{number(y)}" r="{radius}" '
                 f'fill="{fill or self.accent}" {extra}/>')

    def source(self, y, content):
        self.line(52, y - 28, W - 52, y - 28, self.grid)
        self.wrapped(52, y, "SOURCE  " + content, 157, 11, 17, self.quiet, MONO)

    def save(self, path: Path):
        path.write_text("\n".join(self.parts + ["</svg>", ""]), encoding="utf-8")


def mark_attrs(row: int, field: str, value: str, **geometry) -> str:
    attrs = [f'data-row="{row}"', f'data-field="{field}"', f'data-value="{esc(value)}"']
    attrs += [f'data-{k.replace("_", "-")}="{number(v)}"' for k, v in geometry.items()]
    return " ".join(attrs)


def f1(dark):
    data = rows("F1_pew_domain_share.csv")
    f = Figure("F1", "Signs of AI authorship by web domain, 2021–2026", 815, dark)
    left, right, top, bottom = 110, 890, 165, 510
    start = dt.date.fromisoformat(data[0]["crawl_date"])
    end = dt.date.fromisoformat(data[-1]["crawl_date"])
    x = lambda date: left + (date - start).days / (end - start).days * (right - left)
    y = lambda v: bottom - float(v) / 10 * (bottom - top)
    f.text(left, 137, "% OF SAMPLED PAGES", 11, f.quiet, MONO)
    for tick in (0, 2, 4, 6, 8, 10):
        yy = y(tick)
        f.line(left, yy, right, yy, f.grid, 0.8, "3 5" if tick else None)
        f.text(left - 12, yy + 5, f"{tick}%", 12, f.quiet, MONO, anchor="end")
    for i, row in enumerate(data):
        date = dt.date.fromisoformat(row["crawl_date"])
        if i % 2 == 0 or i == len(data) - 1:
            f.text(x(date), bottom + 27, date.strftime("%Y"), 12, f.quiet, MONO, anchor="middle")
    chat_x = x(dt.date(2022, 11, 30))
    f.line(chat_x, top, chat_x, bottom, f.accent, 1.2, "5 5")
    f.text(chat_x + 9, 180, "ChatGPT released", 12, f.accent, MONO, 600)
    series = [
        ("com", ".com", TOKENS["red"] if dark else TOKENS["darkred"], None, "circle"),
        ("org", ".org", TOKENS["gold"] if dark else TOKENS["ochre"], "7 5", "square"),
        ("edu", ".edu", TOKENS["slate"] if dark else TOKENS["slate"], "2 4", "diamond"),
        ("gov", ".gov", f.ink, "10 4 2 4", "triangle"),
    ]
    end_label_y = {"com": y(9.35) + 4, "org": y(4.59) + 4,
                   "edu": 478, "gov": 510}
    for field, label, color, dash, symbol in series:
        pts = [(x(dt.date.fromisoformat(r["crawl_date"])), y(r[field])) for r in data]
        for a, b in zip(pts, pts[1:]):
            f.line(a[0], a[1], b[0], b[1], color, 2.5, dash)
        for i, (px, py) in enumerate(pts):
            attr = mark_attrs(i, field, data[i][field], x=px, y=py)
            if symbol == "circle":
                f.circle(px, py, 4.5, color, attr)
            elif symbol == "square":
                f.rect(px - 4.5, py - 4.5, 9, 9, color, attr)
            elif symbol == "diamond":
                f.add(f'<path d="M {number(px)} {number(py-5)} L {number(px+5)} {number(py)} '
                      f'L {number(px)} {number(py+5)} L {number(px-5)} {number(py)} Z" '
                      f'fill="{color}" {attr}/>')
            else:
                f.add(f'<path d="M {number(px)} {number(py-6)} L {number(px+6)} {number(py+5)} '
                      f'L {number(px-6)} {number(py+5)} Z" fill="{color}" {attr}/>')
        ly = end_label_y[field]
        f.line(right + 5, pts[-1][1], 922, ly - 4, color, 1)
        f.text(930, ly, f"{label} {data[-1][field]}%", 16, color, SANS, 600)
    f.text(52, 575, "CAVEAT", 11, f.accent, MONO, 600)
    caveat = "Pew's detector flags pages written or substantially edited with AI and misclassifies individual pages in both directions; Pew notes a higher false-positive rate on pre-AI pages."
    f.wrapped(52, 601, caveat, 139, 13, 21)
    caption = "Before ChatGPT, every domain sat near 1%. By January 2026, almost one in ten .com pages showed signs of AI authorship — ten times the rate on .edu and .gov."
    f.wrapped(52, 682, caption, 125, 15, 22)
    f.source(761, 'Pew Research Center · "How Much of the Internet Is Written With AI?" · 20 Aug 2026 · A01–A06 · points are six-month averages.')
    return f


def f2(dark):
    data = rows("F2_deezer_uploads_vs_streams.csv")
    f = Figure("F2", "Music: half of what is uploaded, a sliver of what is heard", 765, dark)
    latest = data[-1]
    x0, scale = 340, 14.0
    f.text(52, 145, "JUNE 2026 · SHARE OF DAILY ACTIVITY", 12, f.quiet, MONO)
    for tick in (0, 10, 20, 30, 40, 50):
        xx = x0 + tick * scale
        f.line(xx, 176, xx, 370, f.grid, 0.7, "3 5")
        f.text(xx, 390, f"{tick}%", 12, f.quiet, MONO, anchor="middle")
    f.text(52, 225, "Share of daily uploads", 16, f.ink, SANS, 600)
    f.rect(x0, 198, float(latest["share_of_daily_uploads_pct"]) * scale, 34,
           f.accent, mark_attrs(2, "share_of_daily_uploads_pct", latest["share_of_daily_uploads_pct"], x=x0, scale=scale))
    f.text(1110, 224, "50%", 19, f.ink, SANS, 600, anchor="end")
    f.text(52, 321, "Share of streams", 16, f.ink, SANS, 600)
    low = float(latest["share_of_streams_pct_low"])
    high = float(latest["share_of_streams_pct_high"])
    f.rect(x0 + low * scale, 292, (high - low) * scale, 34, TOKENS["slate"],
           mark_attrs(2, "share_of_streams_pct_low", latest["share_of_streams_pct_low"],
                      x=x0 + low * scale, scale=scale, high=high))
    f.line(x0 + low * scale, 286, x0 + low * scale, 334, f.ink, 1.5)
    f.line(x0 + high * scale, 286, x0 + high * scale, 334, f.ink, 1.5,
           extra=mark_attrs(2, "share_of_streams_pct_high", latest["share_of_streams_pct_high"], x=x0 + high * scale, scale=scale))
    f.text(1110, 321, "1–3%", 19, f.ink, SANS, 600, anchor="end")
    f.text(52, 445, "FULLY AI-GENERATED TRACKS UPLOADED PER DAY", 12, f.quiet, MONO)
    dot_x = (185, 595, 1005)
    for i, row in enumerate(data):
        label = {"2025-01": "JAN 2025", "2026-04": "APR 2026", "2026-06": "JUN 2026"}[row["period"]]
        f.circle(dot_x[i], 495, 8, f.accent,
                 mark_attrs(i, "ai_tracks_per_day", row["ai_tracks_per_day"], x=dot_x[i], y=495))
        f.text(dot_x[i], 475, f'{int(row["ai_tracks_per_day"]):,}', 24, f.ink, SANS, 600, "middle")
        f.text(dot_x[i], 523, label, 12, f.quiet, MONO, anchor="middle")
    f.wrapped(52, 587, "Fully AI-generated tracks passed half of Deezer's daily uploads in June 2026, yet accounted for 1–3% of listening; Deezer found up to 85% of their streams were fraudulent.", 130, 15, 22)
    f.source(704, "Deezer newsroom · Deezer: AI-generated tracks now represent 44% of all new uploaded music (20 Apr 2026); Deezer: AI music has surpassed 50% of new music uploads for the first time (21 Jul 2026) · A26–A28 · vendor data.")
    return f


def f3(dark):
    data = rows("F3_arxiv_submissions.csv")
    f = Figure("F3", "arXiv monthly submissions", 750, dark)
    base, top = 480, 165
    centers = (235, 515, 795)
    f.text(52, 141, "SEPTEMBER SUBMISSIONS", 12, f.quiet, MONO)
    for tick in (0, 10000, 20000, 30000, 40000):
        yy = base - tick / 45000 * (base - top)
        f.line(100, yy, 950, yy, f.grid, 0.8, "3 5" if tick else None)
        f.text(89, yy + 4, f"{tick//1000}k", 12, f.quiet, MONO, anchor="end")
    for i, (row, cx) in enumerate(zip(data, centers)):
        value = int(row["submissions"])
        yy = base - value / 45000 * (base - top)
        f.rect(cx - 68, yy, 136, base - yy, f.accent if i == 2 else TOKENS["slate"],
               mark_attrs(i, "submissions", row["submissions"], base=base, top=top, max=45000))
        f.text(cx, yy - 13, f"{value:,}", 22, f.ink, SANS, 600, "middle")
        f.text(cx, base + 29, "SEP " + row["month"][:4], 13, f.quiet, MONO, anchor="middle")
    f.text(996, 248, "≈9,000", 19, f.accent, SANS, 600)
    f.text(996, 272, "support tickets", 13, f.ink)
    f.wrapped(52, 551, "cs.AI submissions: more than 6× in 2024–2026; other categories roughly doubled.", 145, 13, 20, f.quiet)
    f.wrapped(52, 602, "Submissions doubled in two years. From 1 October 2026 each submitter may send two papers a month — rejected ones count.", 130, 15, 22)
    f.wrapped(52, 653, "arXiv attributes a disproportionate share of moderator time to a relatively small proportion of authors.", 145, 12, 18, f.quiet)
    f.source(704, "Kat Boboris / arXiv blog · Fair Moderation, Equitable Access, and AI: arXiv’s Updated Rate Limit Policy · 1 Oct 2026 · F01–F03, F05, Z11.")
    return f


def f5(dark):
    data = rows("F5_openai_text_watermark.csv")
    f = Figure("F5", "How a text watermark fades", 760, dark)
    f.text(52, 142, "A  /  LENGTH", 13, f.accent, MONO, 600)
    f.text(618, 142, "B  /  EDITING", 13, f.accent, MONO, 600)
    f.line(595, 130, 595, 465, f.grid)
    base, top = 445, 190
    for tick in (0, 25, 50, 75, 100):
        yy = base - tick / 100 * (base - top)
        for x0, x1 in ((92, 553), (658, 1110)):
            f.line(x0, yy, x1, yy, f.grid, 0.7, "3 5" if tick else None)
        f.text(85, yy + 4, f"{tick}%", 11, f.quiet, MONO, anchor="end")
        f.text(652, yy + 4, f"{tick}%", 11, f.quiet, MONO, anchor="end")
    for i, row in enumerate(data):
        value = float(row["detection_rate_pct"])
        yy = base - value / 100 * (base - top)
        if row["panel"] == "length":
            cx = (245, 430)[i]
            label = row["condition"]
            color = TOKENS["slate"] if i == 0 else f.accent
        else:
            cx = (725, 875, 1025)[i - 2]
            label = row["condition"].replace(" words replaced", "")
            color = f.accent if i == 2 else TOKENS["slate"]
        f.rect(cx - 38, yy, 76, base - yy, color,
               mark_attrs(i, "detection_rate_pct", row["detection_rate_pct"], base=base, top=top, max=100))
        f.text(cx, yy - 11, f'{number(value)}%', 19, f.ink, SANS, 600, "middle")
        f.text(cx, base + 25, label, 12, f.quiet, MONO, anchor="middle")
    f.wrapped(52, 520, "At a 1% false-positive target, replacing a quarter of the words with synonyms reduced detection from 92% to 17%. Detection was substantially lower for mathematics.", 132, 15, 22)
    f.wrapped(52, 595, "Provider's own evaluations. The supplied spec says English ELI5 answers; the CSV length rows say psychology content.", 138, 12, 19, f.quiet)
    f.source(711, 'OpenAI · "Our approach to EU text provenance rules" · 5 Oct 2026 · B13–B15 · vendor data.')
    return f


def f9(dark):
    data = rows("F9_bastani.csv")
    f = Figure("F9", "Practice versus exam", 720, dark)
    base, top, low = 430, 178, -20
    scale = (base - top) / (140 - low)
    y = lambda v: base - (v - low) * scale
    zero = y(0)
    for tick in (-20, 0, 40, 80, 120):
        yy = y(tick)
        f.line(100, yy, 1090, yy, f.ink if tick == 0 else f.grid, 1.4 if tick == 0 else 0.8,
               None if tick == 0 else "3 5")
        f.text(90, yy + 4, f"{tick:+d}%" if tick else "0", 12, f.quiet, MONO, anchor="end")
    f.text(1074, zero - 9, "CONTROL", 11, f.quiet, MONO, anchor="end")
    bars = [(0, "practice_vs_control_pct", 285, TOKENS["slate"], "GPT BASE"),
            (1, "practice_vs_control_pct", 390, f.accent, "GPT TUTOR"),
            (0, "exam_vs_control_pct", 755, TOKENS["slate"], "GPT BASE"),
            (1, "exam_vs_control_pct", 860, f.accent, "GPT TUTOR")]
    for row_i, field, cx, color, label in bars:
        value = float(data[row_i][field])
        yy = y(value)
        if value:
            f.rect(cx - 38, min(yy, zero), 76, abs(zero - yy), color,
                   mark_attrs(row_i, field, data[row_i][field], zero=zero, scale=scale))
        else:
            f.line(cx - 38, zero, cx + 38, zero, color, 6,
                   extra=mark_attrs(row_i, field, data[row_i][field], zero=zero, scale=scale))
        shown = "≈0" if value == 0 else f"{value:+.0f}%".replace("-", "−")
        f.text(cx, (yy - 12 if value > 0 else yy + 27), shown, 20, f.ink, SANS, 600, "middle")
        f.text(cx, 478, label, 11, f.quiet, MONO, anchor="middle")
    f.text(340, 516, "PRACTICE", 16, f.ink, SANS, 600, "middle")
    f.text(807, 516, "EXAM WITHOUT AI", 16, f.ink, SANS, 600, "middle")
    f.wrapped(52, 557, "Unrestricted access improved practice scores by 48% and lowered exam scores by 17% once access was removed. A tutor designed not to hand out answers removed the loss.", 130, 15, 22)
    f.wrapped(52, 631, "Fan et al. (BJET) — ChatGPT group improved essay scores most; knowledge gain and transfer did not differ (D08).", 143, 12, 18, f.quiet)
    f.source(690, "Bastani et al. · Generative AI without guardrails can harm learning: Evidence from high school mathematics · PNAS 122(26), 2025 · D01–D02; companion D08.")
    return f


def f10(dark):
    data = rows("F10_hepi.csv")
    f = Figure("F10", "UK undergraduates and AI, 2024–2026", 735, dark)
    panels = [
        ("ANY AI USE", "any_ai_use_pct"),
        ("GENAI FOR ASSESSED WORK", "genai_for_assessed_work_pct"),
        ("AI TEXT INSERTED DIRECTLY", "ai_text_inserted_directly_pct"),
    ]
    for panel_i, (title, field) in enumerate(panels):
        x0 = 52 + panel_i * 380
        f.text(x0, 142, title, 12, f.accent, MONO, 600)
        if panel_i:
            f.line(x0 - 21, 134, x0 - 21, 500, f.grid)
        for row_i, row in enumerate(data):
            yy = 210 + row_i * 105
            f.text(x0, yy, row["year"], 15, f.ink, MONO, 600)
            value = row[field]
            if value:
                f.rect(x0 + 69, yy - 20, float(value) * 2.15, 24,
                       f.accent if row_i == 2 else TOKENS["slate"],
                       mark_attrs(row_i, field, value, x=x0 + 69, scale=2.15))
                f.text(x0 + 339, yy, f"{value}%", 18, f.ink, SANS, 600, "end")
            else:
                f.text(x0 + 69, yy - 4, "just over half", 12, f.quiet, SANS)
                f.text(x0 + 69, yy + 14, "(no exact figure)", 11, f.quiet, SANS)
    f.wrapped(52, 538, "Use is near-universal; direct insertion of AI text into assessed work is a minority practice — 12% in 2026.", 133, 15, 22)
    f.source(673, "HEPI/Kortext · Student Generative AI Survey 2026 · 2026 · E04–E05.")
    return f


def f11(dark):
    data = rows("F11_moltbook.csv")
    f = Figure("F11", "88 to 1", 690, dark)
    agents = int(data[0]["value"])
    owners = int(data[1]["value"])
    ratio = round(agents / owners)
    f.text(52, 190, f"{agents:,}", 52, f.ink, SANS, 600,
           extra=mark_attrs(0, "value", data[0]["value"]))
    f.text(52, 227, "registered agents", 19, f.quiet, SANS)
    f.line(52, 262, 1120, 262, f.grid)
    f.text(52, 335, f"{owners:,}", 52, f.ink, SANS, 600,
           extra=mark_attrs(1, "value", data[1]["value"]))
    f.text(52, 372, "human owners", 19, f.quiet, SANS)
    f.text(52, 512, f"{ratio} : 1", 78, f.accent, SANS, 600,
           extra=f'data-derived="ratio" data-numerator="{agents}" data-denominator="{owners}"')
    f.wrapped(52, 568, "Wiz: the platform had no mechanism to verify whether an 'agent' was AI or a human running a script.", 125, 14, 22)
    f.source(647, 'Wiz · "Hacking Moltbook" · Feb 2026 · H03–H05.')
    return f


BUILDERS = {"F1": f1, "F2": f2, "F3": f3, "F5": f5,
            "F9": f9, "F10": f10, "F11": f11}


def pdf_from_svg(svg: Path, pdf: Path):
    """Draw the same SVG primitives into a vector PDF with bundled fonts."""
    font_dir = OUT / "fonts"
    for family, filename in (
        ("Inter", "Inter-Regular.ttf"),
        ("Inter-SemiBold", "Inter-SemiBold.ttf"),
        ("JetBrainsMono", "JetBrainsMono-Regular.ttf"),
        ("JetBrainsMono-SemiBold", "JetBrainsMono-SemiBold.ttf"),
    ):
        if family not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(family, str(font_dir / filename)))
    root = ET.parse(svg).getroot()
    height = float(root.attrib["height"])
    page = canvas.Canvas(str(pdf), pagesize=(W, height), invariant=1, pageCompression=1)
    page.setTitle(root.find("{http://www.w3.org/2000/svg}title").text or "")
    for el in root:
        kind = el.tag.rsplit("}", 1)[-1]
        a = el.attrib
        if kind == "rect":
            page.setFillColor(HexColor(a["fill"]))
            page.rect(float(a.get("x", 0)), height - float(a.get("y", 0)) - float(a["height"]),
                      float(a["width"]), float(a["height"]), fill=1, stroke=0)
        elif kind == "line":
            page.setStrokeColor(HexColor(a["stroke"]))
            page.setLineWidth(float(a.get("stroke-width", 1)))
            page.setDash([float(v) for v in a["stroke-dasharray"].split()] if "stroke-dasharray" in a else [])
            page.line(float(a["x1"]), height - float(a["y1"]),
                      float(a["x2"]), height - float(a["y2"]))
            page.setDash([])
        elif kind == "circle":
            page.setFillColor(HexColor(a["fill"]))
            page.circle(float(a["cx"]), height - float(a["cy"]), float(a["r"]), fill=1, stroke=0)
        elif kind == "path":
            page.setFillColor(HexColor(a["fill"]))
            path = page.beginPath()
            tokens = re.findall(r"[MLZ]|-?\d+(?:\.\d+)?", a["d"])
            i = 0
            while i < len(tokens):
                cmd = tokens[i]
                if cmd == "Z":
                    path.close()
                    i += 1
                else:
                    px, py = float(tokens[i + 1]), float(tokens[i + 2])
                    (path.moveTo if cmd == "M" else path.lineTo)(px, height - py)
                    i += 3
            page.drawPath(path, fill=1, stroke=0)
        elif kind == "text":
            family = "JetBrainsMono" if "JetBrains" in a["font-family"] else "Inter"
            if int(a.get("font-weight", 400)) >= 600:
                family += "-SemiBold"
            page.setFont(family, float(a["font-size"]))
            page.setFillColor(HexColor(a["fill"]))
            px, py = float(a["x"]), height - float(a["y"])
            content = el.text or ""
            align = a.get("text-anchor", "start")
            if align == "middle":
                page.drawCentredString(px, py, content)
            elif align == "end":
                page.drawRightString(px, py, content)
            else:
                page.drawString(px, py, content)
    page.showPage()
    page.save()


def build(figure_id: str):
    if figure_id not in BUILDERS:
        raise ValueError(f"Unknown figure: {figure_id}")
    OUT.mkdir(exist_ok=True)
    light = OUT / f"{figure_id}.svg"
    dark = OUT / f"{figure_id}.dark.svg"
    BUILDERS[figure_id](False).save(light)
    BUILDERS[figure_id](True).save(dark)
    pdf_from_svg(light, OUT / f"{figure_id}.pdf")


if __name__ == "__main__":
    ids = sys.argv[1:] or list(BUILDERS)
    for figure_id in ids:
        build(figure_id)
