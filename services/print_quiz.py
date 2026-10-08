"""Översättningsförhör och separat facit från exakt samma valda glosor."""
from io import BytesIO
from html import escape
from pathlib import Path
import random
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def quiz_versions(vocab, word_ids, shuffled=True, two_versions=False, seed=None):
    if not word_ids or len(word_ids) != len(set(word_ids)):
        raise ValueError("Välj minst en glosa, utan dubblerade ord.")
    by_id = {w["id"]: w for w in vocab["words"]}
    if not set(word_ids) <= by_id.keys():
        raise ValueError("En vald glosa finns inte längre i listan.")
    words = [by_id[i] for i in word_ids]
    rng = random.Random(seed)
    if shuffled:
        rng.shuffle(words)
    versions = {"A": words}
    if two_versions:
        if len(words) < 2:
            raise ValueError("A/B-versioner behöver minst två glosor.")
        other = list(words)
        rng.shuffle(other)
        if [w["id"] for w in other] == [w["id"] for w in words]:
            other = other[1:] + other[:1]
        versions["B"] = other
    return versions


def quiz_pdf(vocab, versions, direction="forward", answers=False):
    if direction not in ("forward", "reverse"):
        raise ValueError("Ogiltig språkriktning.")
    font_dir = Path(reportlab.__file__).parent / "fonts"
    for name, filename in (("GlosFlow", "Vera.ttf"), ("GlosFlow-Bold", "VeraBd.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily("GlosFlow", normal="GlosFlow", bold="GlosFlow-Bold")
    body = ParagraphStyle("body", fontName="GlosFlow", fontSize=10, leading=15, textColor=colors.HexColor("#173b4c"), alignment=TA_LEFT, splitLongWords=True)
    heading = ParagraphStyle("heading", parent=body, fontName="GlosFlow-Bold", fontSize=20, leading=26, spaceAfter=8)
    meta = ParagraphStyle("meta", parent=body, fontSize=9, leading=13, spaceAfter=5)
    def p(text, style=body):
        return Paragraph(escape(str(text)), style)
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                           topMargin=17*mm, bottomMargin=19*mm, title="GlosFlow - " + ("Facit" if answers else "Glosförhör"), author="GlosFlow")
    story = []
    source, destination = ("Svenska", vocab["language"]) if direction == "forward" else (vocab["language"], "Svenska")
    for index, (version, words) in enumerate(versions.items()):
        if index:
            story.append(PageBreak())
        story.extend([p(("Facit" if answers else "Glosförhör") + (" - Version " + version if len(versions) > 1 else ""), heading),
                      p(vocab["name"], meta), p("Kurs: " + vocab["category"], meta),
                      p(f"{source} till {destination}  |  {len(words)} glosor", meta)])
        if not answers:
            story.extend([Spacer(1, 5*mm), p("Namn: ____________________________________   Klass: ______________"),
                          Spacer(1, 3*mm), p("Datum: ____________________"), Spacer(1, 6*mm),
                          p("Översätt varje ord eller uttryck. Skriv ditt svar på raden."), Spacer(1, 5*mm)])
        else:
            story.extend([p("Godkända svarsalternativ från gloslistan visas nedan.", meta), Spacer(1, 4*mm)])
        rows = [[p("Nr"), p(source), p("Godkända svar" if answers else "Ditt svar på " + destination.lower())]]
        for number, word in enumerate(words, 1):
            prompt = word["svenska"] if direction == "forward" else word["accepted_answers"][0]
            solutions = word["accepted_answers"] if direction == "forward" else word["swedish_answers"]
            rows.append([p(number), p(prompt), p("; ".join(solutions) if answers else "________________________________")])
        table = Table(rows, colWidths=[11*mm, 68*mm, 95*mm], repeatRows=1, hAlign="LEFT", splitInRow=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 12 if answers else 18),
            ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#758a8d")),
            ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#c9d3d5")),
        ]))
        story.append(table)
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("GlosFlow", 8)
        canvas.setFillColor(colors.HexColor("#526773"))
        canvas.drawString(18*mm, 11*mm, "GlosFlow | " + ("Facit" if answers else "Glosförhör"))
        canvas.drawRightString(192*mm, 11*mm, f"Sida {document.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()
