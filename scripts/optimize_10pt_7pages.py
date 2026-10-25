"""
Optimizes research_paper.docx to achieve 10pt font and <= 7 pages max.
Preserves all user text, edits, headings, tables, and figures.
"""

import os
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DOCX = os.path.join(PROJECT_ROOT, "research_paper", "research_paper.docx")
TARGET_7P = os.path.join(PROJECT_ROOT, "research_paper", "research_paper_7pages.docx")
TARGET_2COL = os.path.join(PROJECT_ROOT, "research_paper", "research_paper_ieee_2column.docx")

def optimize_to_10pt(doc_path, fig_width_in=2.65, body_space_after=0.5):
    doc = docx.Document(doc_path)
    body = doc._body._element

    # 1. Margins: 0.55 in top/bottom, 0.58 in left/right (compact IEEE)
    for s in doc.sections:
        s.top_margin = Inches(0.55)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.58)
        s.right_margin = Inches(0.58)

    # 2. Remove purely blank paragraphs that don't have drawings
    to_remove = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        drawings = p._p.findall('.//' + qn('w:drawing'))
        if not txt and not drawings:
            # Check if this paragraph contains a section break
            pPr = p._p.find(qn('w:pPr'))
            if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
                continue
            to_remove.append(p._p)

    for el in to_remove:
        body.remove(el)
    print(f"Removed {len(to_remove)} redundant empty paragraphs.")

    # 3. Format paragraphs
    in_references = False
    in_header = True

    for p in doc.paragraphs:
        txt = p.text.strip()

        # References block
        if txt == "REFERENCES" or txt.startswith("## References"):
            in_references = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(1.5)
            continue

        if in_references:
            if not txt:
                continue
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0.8)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(7.5)
            continue

        # Header block
        if txt.startswith("I. INTRODUCTION") or txt.startswith("## I. Introduction"):
            in_header = False

        if in_header:
            if p == doc.paragraphs[0]: # Title
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2.5)
                for r in p.runs:
                    r.font.size = Pt(15.0)
            elif "Dr. Swati Shinde" in txt: # Authors
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3.0)
                for r in p.runs:
                    r.font.size = Pt(8.5)
            elif txt.startswith("Abstract") or txt.startswith("Key Words") or txt.startswith("Index Terms"):
                p.paragraph_format.space_before = Pt(0.5)
                p.paragraph_format.space_after = Pt(1.5)
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(8.5)
            continue

        # Headings
        is_h1 = any(txt.startswith(prefix) for prefix in ["I. ", "II. ", "III. ", "IV. ", "V. ", "VI. ", "VII. ", "ACKNOWLEDGMENT", "APPENDIX"])
        is_h2 = any(txt.startswith(f"{letter}. ") for letter in "ABCDEFGH") and len(txt) < 80

        if is_h1:
            p.paragraph_format.space_before = Pt(3.5)
            p.paragraph_format.space_after = Pt(1.0)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.0)
                r.bold = True
            continue

        if is_h2:
            p.paragraph_format.space_before = Pt(2.5)
            p.paragraph_format.space_after = Pt(0.5)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.0)
                r.bold = True
                r.italic = True
            continue

        # Drawings / Figures
        drawings = p._p.findall('.//' + qn('w:drawing'))
        if drawings:
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(0.5)
            extents = p._p.findall('.//' + qn('wp:extent'))
            for ext in extents:
                cur_cx = int(ext.get('cx'))
                cur_cy = int(ext.get('cy'))
                new_cx = int(fig_width_in * 914400)
                new_cy = int(cur_cy * (new_cx / cur_cx))
                ext.set('cx', str(new_cx))
                ext.set('cy', str(new_cy))
                for a_ext in p._p.findall('.//' + qn('a:ext')):
                    a_ext.set('cx', str(new_cx))
                    a_ext.set('cy', str(new_cy))
            continue

        # Captions
        if txt.startswith("Figure ") or txt.startswith("Fig. "):
            p.paragraph_format.space_before = Pt(0.5)
            p.paragraph_format.space_after = Pt(2.0)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(7.5)
                r.italic = True
            continue

        # Normal body paragraphs: 10.0 pt font, single line spacing
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(body_space_after)
        p.paragraph_format.line_spacing = 1.0
        for r in p.runs:
            r.font.name = 'Times New Roman'
            if r.font.size and r.font.size > Pt(10.5):
                continue
            r.font.size = Pt(10.0)

    # 4. Tables formatting: ultra compact padding
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_before = Pt(0.1)
                    p.paragraph_format.space_after = Pt(0.1)
                    p.paragraph_format.line_spacing = 1.0

    # Save to targets
    doc.save(TARGET_7P)
    doc.save(TARGET_2COL)
    try:
        doc.save(doc_path)
        print(f"Saved directly to {doc_path}!")
    except PermissionError:
        print(f"Note: {doc_path} is currently locked by Word. Saved to {TARGET_7P} and {TARGET_2COL}")

if __name__ == '__main__':
    optimize_to_10pt(SRC_DOCX)
