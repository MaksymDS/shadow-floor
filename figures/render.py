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
    def __init__(self, figure_id: str, title: str, height: int, dark: bool, width: int = W):
        self.id, self.title, self.height, self.dark, self.width = figure_id, title, height, dark, width
        self.paper = TOKENS["bg"] if dark else TOKENS["cream"]
        self.ink = TOKENS["cream"] if dark else TOKENS["bg"]
        self.quiet = TOKENS["muted"] if dark else TOKENS["rule"]
        self.grid = TOKENS["rule"] if dark else TOKENS["muted"]
        self.accent = TOKENS["gold"] if dark else TOKENS["darkred"]
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title>',
            f'<desc id="desc">Shadow 06 figure {esc(figure_id)}. Exact plotted values are encoded on marks.</desc>',
            f'<rect width="{width}" height="{height}" fill="{self.paper}"/>',
        ]
        self.text(52, 36, f"SHADOW 06  /  FIGURE {figure_id[1:]}", 12, self.accent, MONO, 600)
        self.text(52, 78, title, 29, self.ink, SANS, 600)
        self.line(52, 98, width - 52, 98, self.grid, 1)

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
        self.line(52, y - 28, self.width - 52, y - 28, self.grid)
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
    f.text(chat_x + 9, 180, "Nov 2022", 12, f.accent, MONO, 600)
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
    caveat = "Pew's detector flags pages written or substantially edited with AI, and misclassifies individual pages in both directions. Points are six-month averages; Pew reports a higher false-positive rate on pre-AI pages."
    f.wrapped(52, 601, caveat, 139, 13, 21)
    caption = "Six-month averages for four domains. Rates were similar at the start of the period; in the period labelled January 2026, .com reached 9.35%, against about 1% on .edu and .gov."
    f.add('<g data-text-role="caption">')
    f.wrapped(52, 682, caption, 125, 15, 22)
    f.add('</g>')
    f.add('<g data-text-role="source">')
    f.source(761, 'Pew Research Center · "How Much of the Internet Is Written With AI?" · 20 Aug 2026 · A01–A06 · Plotted points are six-month averages (Pew).')
    f.add('</g>')
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
    f.add('<g data-text-role="caption">')
    f.wrapped(52, 587, "Deezer reports that fully AI-generated tracks exceeded half of daily uploads at a June 2026 peak, and accounted for 1–3% of streams; it classified up to 85% of those streams in 2025 as fraudulent. Upload share and stream share are different measures.", 130, 15, 22)
    f.add('</g>')
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
    f.add('<g data-text-role="callout">')
    f.text(978, 244, "Nearly 9,000", 17, f.accent, SANS, 600)
    f.text(978, 267, "support tickets", 13, f.ink)
    f.text(978, 288, "(Sep 2026, staff", 11, f.quiet)
    f.text(978, 306, "and moderators).", 11, f.quiet)
    f.add('</g>')
    f.wrapped(52, 551, "cs.AI submissions: more than 6× in 2024–2026; other categories roughly doubled.", 145, 13, 20, f.quiet)
    f.add('<g data-text-role="caption">')
    f.wrapped(52, 602, "Roughly twice as many submissions in September 2026 as in September 2024. From 1 October 2026 each submitter may send two new papers a month; rejected ones count.", 130, 15, 22)
    f.add('</g>')
    f.wrapped(52, 653, "arXiv attributes a disproportionate share of moderator time to a relatively small proportion of authors.", 145, 12, 18, f.quiet)
    f.source(704, "Kat Boboris / arXiv blog · Fair Moderation, Equitable Access, and AI: arXiv’s Updated Rate Limit Policy · 1 Oct 2026 · F01–F03, F05, Z11.")
    return f


def f9(dark):
    data = rows("F9_learning_study.csv")
    f = Figure("F9", "Practice versus exam", 810, dark)
    f.add('<g data-text-role="axis_label">')
    f.text(100, 145, "relative difference vs comparison group (%)", 11, f.quiet, MONO)
    f.add('</g>')
    base, top, low = 430, 178, -20
    scale = (base - top) / (140 - low)
    y = lambda v: base - (v - low) * scale
    zero = y(0)
    for tick in (-20, 0, 40, 80, 120):
        yy = y(tick)
        f.line(100, yy, 1090, yy, f.ink if tick == 0 else f.grid, 1.4 if tick == 0 else 0.8,
               None if tick == 0 else "3 5")
        f.text(90, yy + 4, f"{tick:+d}%" if tick else "0", 12, f.quiet, MONO, anchor="end")
    f.text(1095, zero + 27, "CONTROL", 11, f.quiet, MONO, anchor="end")
    bars = [(0, "practice_vs_control_pct", 260, TOKENS["slate"]),
            (1, "practice_vs_control_pct", 450, f.accent),
            (0, "exam_vs_control_pct", 730, TOKENS["slate"])]
    for row_i, field, cx, color in bars:
        value = float(data[row_i][field])
        yy = y(value)
        f.rect(cx - 38, min(yy, zero), 76, abs(zero - yy), color,
               mark_attrs(row_i, field, data[row_i][field], zero=zero, scale=scale))
        shown = f"{value:+.0f}%".replace("-", "−") if field.startswith("practice") else data[row_i]["exam_label"]
        label_attrs = mark_attrs(row_i, "exam_label", shown) if field == "exam_vs_control_pct" else ""
        f.text(cx, (yy - 12 if value > 0 else yy + 27), shown, 20, f.ink, SANS, 600, "middle",
               extra=label_attrs)
    f.text(925, zero - 10, data[1]["exam_label"], 15, f.ink, SANS, 600, "middle",
           extra=mark_attrs(1, "exam_label", data[1]["exam_label"]))
    for row_i, cx in ((0, 260), (1, 450), (0, 730), (1, 925)):
        arm = data[row_i]["arm"]
        f.text(cx, 480, arm, 12, f.quiet, SANS, anchor="middle",
               extra=mark_attrs(row_i, "arm", arm) if cx < 600 else "")
    f.text(355, 523, "PRACTICE", 16, f.ink, SANS, 600, "middle")
    f.text(827, 523, "EXAM WITHOUT ASSISTANT", 16, f.ink, SANS, 600, "middle")
    f.wrapped(52, 568, "Unrestricted access raised practice scores by 48% and was followed by exam scores 17% below the control group once access was removed. For a tutor designed not to hand out answers, the authors report the loss was largely mitigated.", 130, 15, 22)
    f.add('<g data-text-role="companion">')
    f.wrapped(52, 655, "A separate randomised study (BJET, 2025; 117 students): the AI-assisted group showed the greatest improvement in essay scores during revision; the study did not detect significant between-group differences in knowledge gain or transfer.", 145, 12, 18, f.quiet)
    f.add('</g>')
    f.source(759, "Bastani et al., PNAS 122(26), 2025; Fan et al., BJET 56(2), 2025.")
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
    f = Figure("F11", "88 to 1", 890, dark)
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
    f.text(52, 515, f"{ratio} : 1", 78, f.accent, SANS, 600,
           extra=f'data-derived="ratio" data-numerator="{agents}" data-denominator="{owners}"')
    f.wrapped(52, 571, "Database state before the first fix, 31 Jan 2026; Wiz, published 2 Feb 2026. Registrations and owner records — not activity.", 128, 14, 22, f.quiet)
    f.wrapped(52, 669, "About 1.5 million registered 'agents' and about 17,000 human owners, according to the Wiz investigation. Registrations do not measure activity or autonomy; the platform had no mechanism to verify whether an 'agent' was AI.", 128, 15, 22)
    f.source(829, 'Wiz · "Hacking Moltbook" · 2 Feb 2026 · H03–H05.')
    return f


TABLES = {
    "F4": {
        "title": "Counting, screening, judging", "csv": "F4_institutions_decisions.csv",
        "columns": [
            ("Actor", 174, ("actor",)), ("What is classified", 143, ("what_is_classified",)),
            ("Instrument", 158, ("instrument",)), ("Use", 125, ("use",)),
            ("Human step", 150, ("human_step",)), ("Outcome", 255, ("outcome",)),
            ("IDs", 91, ("rows",)),
        ],
        "caption": "The same kind of classifier is used to estimate prevalence, to screen submissions, and — less and less — to judge individuals.",
        "note": "Aggregate estimation and individual adjudication carry different error requirements (ICML 2024, Liang et al.).",
        "source": "F4_institutions_decisions.csv · source IDs at right · see REFERENCES.md.",
    },
    "F6": {
        "title": "Providers, one table", "csv": "F6_providers.csv",
        "columns": [
            ("Field", 210, ("field",)), ("Anthropic", 260, ("anthropic",)),
            ("Google", 260, ("google",)), ("OpenAI", 260, ("openai",)),
            ("Rows", 106, ("source_rows",)),
        ],
        "caption": "",
        "note": "",
        "notes": [
            "Provider statements are attributed to the listed sources; the table is not an independent cross-provider test.",
            "Figures come from different implementations, corpora and operating points. No ranking is implied.",
        ],
        "source": "Provider publications in REFERENCES.md · source IDs at right · checked 16 Oct 2026.",
    },
    "F7": {
        "title": "Who must mark what", "csv": "F7_obligations.csv", "width": 1600,
        "columns": [
            ("Jurisdiction", 145, ("jurisdiction",)),
            ("Instrument", 192, ("instrument",)),
            ("Issuer", 145, ("issuer",)),
            ("Covered actor", 168, ("covered_actor",)),
            ("Medium", 170, ("medium",)),
            ("Duty", 290, ("duty",)),
            ("Status", 150, ("status_verified_16oct2026", "clearance")),
            ("Effective date", 152, ("effective_date",)),
            ("Rows", 84, ("rows",)),
        ],
        "caption": "Instruments located and checked as of 16 October 2026. A comparison of specified obligations, not a ranking of countries' overall AI regulation.",
        "note": "Official text located; not cleared for detailed description (language or access)",
        "source": "F7_obligations.csv · source IDs at right · see REFERENCES.md.",
    },
    "F8": {
        "title": "Different samples, periods and units", "csv": "F8_vendor_methods.csv",
        "columns": [
            ("Vendor", 185, ("vendor", "tier", "rows")),
            ("Reported figure", 184, ("reported_figure",)),
            ("Period", 130, ("period",)), ("Unit", 145, ("unit",)),
            ("Sample", 205, ("sample",)), ("Extrapolation", 247, ("extrapolation",)),
        ],
        "caption": "Vendors measure different things — clicks, impressions, requests, schemes — over different periods and samples. The figures are not a range for one quantity.",
        "note": "",
        "source": "F8_vendor_methods.csv · source IDs beside each vendor · vendor data · see REFERENCES.md.",
    },
}


def cell_style(figure_id: str, field: str, first: bool):
    if field in ("rows", "source_rows", "tier", "verified", "clearance"):
        return 10, MONO, 400
    if figure_id == "F7" and field == "instrument":
        return 11, SANS, 400
    if figure_id == "F6" and field in ("anthropic", "google", "openai"):
        return 13, SANS, 400
    return (14 if first else 13), SANS, (600 if first else 400)


def cell_lines(value: str, width: int, size: int, family: str) -> list[str]:
    average = 0.62 if family == MONO else 0.56
    chars = max(8, int((width - 20) / (size * average)))
    return textwrap.wrap(value, width=chars, break_long_words=False, break_on_hyphens=False) or [""]


def row_height(figure_id: str, row: dict[str, str], columns) -> int:
    heights = []
    for _, width, fields in columns:
        used = 19
        for n, field in enumerate(fields):
            size, family, _ = cell_style(figure_id, field, n == 0)
            used += len(cell_lines(row[field], width, size, family)) * (19 if size >= 13 else 16) + 6
        heights.append(used + 3)
    return max(58, *heights)


def draw_table_cell(f: Figure, figure_id: str, row_index: int, row: dict[str, str],
                    x: int, y: int, width: int, fields):
    baseline = y + 20
    for n, field in enumerate(fields):
        size, family, weight = cell_style(figure_id, field, n == 0)
        color = f.ink if n == 0 else f.quiet
        f.add(f'<g data-row="{row_index}" data-field="{field}" data-value="{esc(row[field])}">')
        for line in cell_lines(row[field], width, size, family):
            f.text(x + 10, baseline, line, size, color, family, weight)
            baseline += 19 if size >= 13 else 16
        f.add("</g>")
        baseline += 6


def table_figure(figure_id: str, dark: bool) -> Figure:
    spec = TABLES[figure_id]
    data = rows(spec["csv"])
    columns = spec["columns"]
    canvas_width = spec.get("width", W)
    assert sum(col_width for _, col_width, _ in columns) == canvas_width - 104
    heights = [row_height(figure_id, row, columns) for row in data]
    groups = list(dict.fromkeys(row["group"] for row in data)) if figure_id == "F7" else []
    table_bottom = 184 + sum(heights) + len(groups) * 40
    caption_y = table_bottom + 55 if spec["caption"] else 0
    caption_count = len(textwrap.wrap(spec["caption"], width=128, break_long_words=False,
                                      break_on_hyphens=False)) if spec["caption"] else 0
    notes = spec.get("notes") or ([spec["note"]] if spec["note"] else [])
    note_y = (caption_y + caption_count * 22 + 31) if spec["caption"] else table_bottom + 55
    note_positions = []
    for note in notes:
        note_positions.append((note_y, note))
        note_y += len(textwrap.wrap(note, width=140, break_long_words=False,
                                    break_on_hyphens=False)) * 20 + 36
    source_y = note_y + 17 if notes else (caption_y + caption_count * 22 + 58)
    source_count = len(cell_lines("SOURCE  " + spec["source"], 1096, 11, MONO))
    height = source_y + source_count * 17 + 28
    f = Figure(figure_id, spec["title"], height, dark, canvas_width)
    x = 52
    for label, col_width, _ in columns:
        for line_index, line in enumerate(cell_lines(label.upper(), col_width, 11, MONO)):
            f.text(x + 10, 147 + line_index * 14, line, 11, f.quiet, MONO)
        x += col_width
    f.line(52, 180, canvas_width - 52, 180, f.grid)
    y = 184
    previous_group = None
    for row_index, (row, rh) in enumerate(zip(data, heights)):
        if figure_id == "F7" and row["group"] != previous_group:
            f.rect(52, y, canvas_width - 104, 40, TOKENS["card"] if dark else TOKENS["muted"],
                   'fill-opacity="0.18"')
            f.text(62, y + 26, row["group"], 13, f.quiet, MONO, 600,
                   extra=f'data-group-header="{esc(row["group"])}"')
            y += 40
            previous_group = row["group"]
        if figure_id == "F7" and row["clearance"] == "located, not cleared":
            f.rect(52, y, canvas_width - 104, rh, TOKENS["muted"],
                   f'fill-opacity="0.18" data-verification-row="{row_index}"')
        if figure_id == "F4":
            category = "measure" if row["use"] == "measure (aggregate)" else "screen" if row["use"] == "screen" else "sanction"
            tone = {"measure": TOKENS["slate"], "screen": TOKENS["muted"], "sanction": f.ink}[category]
            use_x = 52 + sum(width for _, width, _ in columns[:3])
            f.rect(use_x + 3, y + 9, 4, rh - 18, tone, f'data-use-category="{category}" data-use-row="{row_index}"')
        if figure_id == "F7":
            f.add(f'<g data-group-row="{row_index}" data-group-value="{esc(row["group"])}">')
        x = 52
        for _, col_width, fields in columns:
            draw_table_cell(f, figure_id, row_index, row, x, y, col_width, fields)
            x += col_width
            if x < f.width - 52:
                f.line(x, y, x, y + rh, f.grid, .6)
        if figure_id == "F7":
            f.add("</g>")
        y += rh
        f.line(52, y, f.width - 52, y, f.grid, .8)
    if spec["caption"]:
        f.text(52, caption_y - 24, "CAPTION", 10, f.accent, MONO, 600)
        f.wrapped(52, caption_y, spec["caption"], 128, 15, 22)
    for note_index, (position, note) in enumerate(note_positions):
        label = f"FOOTNOTE {note_index + 1}" if len(notes) > 1 else "NOTE"
        f.text(52, position - 24, label, 10, f.accent, MONO, 600)
        f.wrapped(52, position, note, 140, 13, 20, f.quiet)
    f.source(source_y, spec["source"])
    return f


def html_table(figure_id: str) -> str:
    spec = TABLES[figure_id]
    data = rows(spec["csv"])
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"<title>Shadow 06 {figure_id} — {esc(spec['title'])}</title>",
        "<style>",
        '@font-face{font-family:Inter;src:url("fonts/Inter-Regular.ttf")}@font-face{font-family:Inter;src:url("fonts/Inter-SemiBold.ttf");font-weight:600}',
        '@font-face{font-family:Mono;src:url("fonts/JetBrainsMono-Regular.ttf")}',
        'body{margin:0;background:#161819;color:#EDE0C8;font:16px/1.55 Inter,Arial,sans-serif}main{max-width:1240px;margin:auto;padding:clamp(24px,5vw,60px)}',
        'h1{font-size:clamp(30px,4vw,52px);line-height:1.08;letter-spacing:-.03em}p{max-width:85ch}a{color:#E8B547}',
        '.eyebrow,.source,.note-label{font:11px/1.5 Mono,monospace;letter-spacing:.12em;text-transform:uppercase;color:#E8B547}',
        '.scroll{overflow-x:auto;border:1px solid #2A2D2F}table{border-collapse:collapse;width:100%;min-width:1100px;background:#101213}',
        'caption{text-align:left;padding:16px 18px;background:#121415;color:#E8B547;font:11px/1.5 Mono,monospace;letter-spacing:.12em;text-transform:uppercase}',
        'th,td{padding:13px 12px;text-align:left;vertical-align:top;border-bottom:1px solid #2A2D2F;border-right:1px solid #2A2D2F}th:last-child,td:last-child{border-right:0}',
        'thead th{color:#9C907A;font:11px/1.4 Mono,monospace;text-transform:uppercase}tbody th{font-weight:600}tbody tr.unverified{background:#2A2D2F}',
        'tbody .group-row th{background:#1C1E1F;color:#9C907A;font:600 12px/1.5 Mono,monospace;letter-spacing:.08em}',
        '.cell-value{display:block}.cell-value+.cell-value{margin-top:5px;color:#9C907A;font-size:12px}.use-measure{border-left:4px solid #6E8499}.use-screen{border-left:4px solid #9C907A}.use-sanction{border-left:4px solid #EDE0C8}',
        '.caption-copy{font-size:18px}.note{color:#9C907A}.source{margin-top:28px;color:#9C907A} :focus-visible{outline:1px solid #E8B547;outline-offset:3px}',
        '.scroll-hint{display:none;color:#9C907A;font:12px/1.5 Mono,monospace}@media(max-width:700px){.scroll-hint{display:block}}',
        "</style></head><body><main>",
        f'<p class="eyebrow">Shadow 06 / Figure {esc(figure_id[1:])}</p><h1>{esc(spec["title"])}</h1>',
        '<p class="scroll-hint">Scroll the table sideways to see every column.</p>',
        '<div class="scroll" role="region" aria-label="Scrollable figure table" tabindex="0"><table>',
        f'<caption>{esc(spec["title"])}</caption><thead><tr>',
    ]
    for label, _, _ in spec["columns"]:
        parts.append(f'<th scope="col">{esc(label)}</th>')
    parts.append("</tr></thead>")
    previous_group = None
    if figure_id != "F7":
        parts.append("<tbody>")
    for row_index, row in enumerate(data):
        if figure_id == "F7" and row["group"] != previous_group:
            if previous_group is not None:
                parts.append("</tbody>")
            parts.append(f'<tbody aria-label="{esc(row["group"])}"><tr class="group-row"><th scope="rowgroup" colspan="{len(spec["columns"])}">{esc(row["group"])}</th></tr>')
            previous_group = row["group"]
        shade = ' class="unverified"' if figure_id == "F7" and row["clearance"] == "located, not cleared" else ""
        metadata = f' data-group="{esc(row["group"])}" data-clearance="{esc(row["clearance"])}"' if figure_id == "F7" else ""
        parts.append(f'<tr{shade}{metadata}>')
        for col_index, (_, _, fields) in enumerate(spec["columns"]):
            tag = "th" if col_index == 0 else "td"
            scope = ' scope="row"' if col_index == 0 else ""
            use_class = ""
            if figure_id == "F4" and fields == ("use",):
                category = "measure" if row["use"] == "measure (aggregate)" else "screen" if row["use"] == "screen" else "sanction"
                use_class = f' class="use-{category}"'
            parts.append(f'<{tag}{scope}{use_class}>')
            for field in fields:
                parts.append(f'<span class="cell-value" data-row="{row_index}" data-field="{field}" data-value="{esc(row[field])}">{esc(row[field])}</span>')
            parts.append(f'</{tag}>')
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    if spec["caption"]:
        parts.append(f'<p class="caption-copy">{esc(spec["caption"])}</p>')
    notes = spec.get("notes") or ([spec["note"]] if spec["note"] else [])
    for note_index, note in enumerate(notes):
        label = f"Footnote {note_index + 1}" if len(notes) > 1 else "Note"
        parts.append(f'<p class="note"><span class="note-label">{label}</span><br>{esc(note)}</p>')
    parts.append(f'<p class="source">SOURCE · {esc(spec["source"])}</p></main></body></html>')
    return "\n".join(parts) + "\n"


def f4(dark): return table_figure("F4", dark)
def f6(dark): return table_figure("F6", dark)
def f7(dark): return table_figure("F7", dark)
def f8(dark): return table_figure("F8", dark)


BUILDERS = {"F1": f1, "F2": f2, "F3": f3, "F4": f4,
            "F6": f6, "F7": f7, "F8": f8, "F9": f9, "F10": f10, "F11": f11}


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
    width = float(root.attrib["width"])
    page = canvas.Canvas(str(pdf), pagesize=(width, height), invariant=1, pageCompression=1)
    page.setTitle(root.find("{http://www.w3.org/2000/svg}title").text or "")
    for el in root.iter():
        kind = el.tag.rsplit("}", 1)[-1]
        a = el.attrib
        if kind == "rect":
            page.saveState()
            page.setFillColor(HexColor(a["fill"]))
            if "fill-opacity" in a:
                page.setFillAlpha(float(a["fill-opacity"]))
            page.rect(float(a.get("x", 0)), height - float(a.get("y", 0)) - float(a["height"]),
                      float(a["width"]), float(a["height"]), fill=1, stroke=0)
            page.restoreState()
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
    if figure_id in TABLES:
        (OUT / f"{figure_id}.table.html").write_text(html_table(figure_id), encoding="utf-8")


if __name__ == "__main__":
    ids = sys.argv[1:] or list(BUILDERS)
    for figure_id in ids:
        build(figure_id)
