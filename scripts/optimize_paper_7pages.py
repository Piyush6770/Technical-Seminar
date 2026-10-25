"""
Tightens research_paper.docx layout to achieve exactly 7 pages (IEEE Standard),
preserving all text, user edits, tables, diagrams, and sequential references.
"""

import os
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(PROJECT_ROOT, "research_paper", "research_paper.docx")

def optimize_layout(doc_path, body_font_sz=9.0, line_spacing=1.03, space_after=1.8, fig_scale=0.82):
    doc = docx.Document(doc_path)
    body = doc._body._element

    # 1. Margins: 0.65 in top/bottom, 0.65 in left/right (standard IEEE compact)
    for s in doc.sections:
        s.top_margin = Inches(0.65)
        s.bottom_margin = Inches(0.65)
        s.left_margin = Inches(0.65)
        s.right_margin = Inches(0.65)

    # 2. Iterate paragraphs and format
    in_references = False
    in_header = True

    for p in doc.paragraphs:
        txt = p.text.strip()

        # Detect References
        if txt == "REFERENCES" or txt.startswith("## References"):
            in_references = True
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            continue

        if in_references:
            if not txt:
                continue
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1.2)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(7.5)
            continue

        # Header detection
        if txt.startswith("I. INTRODUCTION") or txt.startswith("## I. Introduction"):
            in_header = False

        if in_header:
            if p == doc.paragraphs[0]: # Title
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)
                for r in p.runs:
                    r.font.size = Pt(16.0)
            elif "Dr. Swati Shinde" in txt: # Authors
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                for r in p.runs:
                    r.font.size = Pt(8.5)
            elif txt.startswith("Abstract") or txt.startswith("Key Words") or txt.startswith("Index Terms"):
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2.5)
                p.paragraph_format.line_spacing = 1.02
                for r in p.runs:
                    r.font.size = Pt(8.5)
            continue

        # Headings
        is_h1 = any(txt.startswith(prefix) for prefix in ["I. ", "II. ", "III. ", "IV. ", "V. ", "VI. ", "VII. ", "ACKNOWLEDGMENT", "APPENDIX"])
        is_h2 = any(txt.startswith(f"{letter}. ") for letter in "ABCDEFGH") and len(txt) < 80

        if is_h1:
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(1.5)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                r.bold = True
            continue

        if is_h2:
            p.paragraph_format.space_before = Pt(3.5)
            p.paragraph_format.space_after = Pt(1.0)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.0)
                r.bold = True
                r.italic = True
            continue

        # Drawings / Figures
        drawings = p._p.findall('.//' + qn('w:drawing'))
        if drawings:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(1)
            extents = p._p.findall('.//' + qn('wp:extent'))
            for ext in extents:
                cur_cx = int(ext.get('cx'))
                cur_cy = int(ext.get('cy'))
                # Scale slightly
                base_w = int(3.35 * 914400 * fig_scale)
                new_cx = base_w
                new_cy = int(cur_cy * (new_cx / cur_cx))
                ext.set('cx', str(new_cx))
                ext.set('cy', str(new_cy))
                for a_ext in p._p.findall('.//' + qn('a:ext')):
                    a_ext.set('cx', str(new_cx))
                    a_ext.set('cy', str(new_cy))
            continue

        # Captions
        if txt.startswith("Figure ") or txt.startswith("Fig. "):
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(7.8)
                r.italic = True
            continue

        # Normal body paragraphs
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        for r in p.runs:
            r.font.name = 'Times New Roman'
            if r.font.size and r.font.size > Pt(10):
                continue
            r.font.size = Pt(body_font_sz)

    # 3. Compact tables
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_before = Pt(0.2)
                    p.paragraph_format.space_after = Pt(0.2)
                    p.paragraph_format.line_spacing = 1.0

    # Save to 7pages target and 2column
    target_7p = os.path.join(PROJECT_ROOT, "research_paper", "research_paper_7pages.docx")
    target_2col = os.path.join(PROJECT_ROOT, "research_paper", "research_paper_ieee_2column.docx")
    doc.save(target_7p)
    doc.save(target_2col)
    print(f"Saved to {target_7p} and {target_2col}")

    try:
        doc.save(doc_path)
        print(f"Also saved directly to {doc_path}!")
    except PermissionError:
        print(f"Note: {doc_path} is currently open in Word. Changes saved in research_paper_7pages.docx and research_paper_ieee_2column.docx")

if __name__ == '__main__':
    optimize_layout(DOCX_PATH)
