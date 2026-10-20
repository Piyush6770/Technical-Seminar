"""
Generate IEEE Two-Column Publication-Grade Word (.docx) Document:
1. Section 1 (Single column, full width):
   - Document Title
   - Anonymous Author(s) & Double-Blind Review metadata
   - Abstract & Index Terms with horizontal rule delimiters
2. Section 2+ (Two-column layout):
   - IEEE two-column text flow (gutter = 0.25 in, column width = 3.375 in)
   - Times New Roman typography throughout
   - Fully justified text, clean line spacing
   - Figures 2-7 sized to column width (3.35 in)
   - Figure 1 and wide Tables (1-6) span full width via continuous section breaks
   - Authentic IEEE booktabs table styling: pure white background (uncolored), crisp black rules
   - Zero raw LaTeX dollar signs ($), zero missing glyph boxes
   - Stripped author biographies
"""

import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(PROJECT_ROOT, "research_paper", "research_paper.md")
DOCX_PATH = os.path.join(PROJECT_ROOT, "research_paper", "research_paper.docx")
FIG_DIR = os.path.join(PROJECT_ROOT, "research_paper", "figures")

def set_section_columns(section, num_cols, space_dxa=360):
    sectPr = section._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    cols.set(qn('w:num'), str(num_cols))
    if num_cols > 1:
        cols.set(qn('w:space'), str(space_dxa))

def set_cell_border(cell, **kwargs):
    """
    Set cell borders: top, bottom, left, right
    kwargs dict: dict(sz=8, val='single', color='000000')
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key, val in edge_data.items():
                element.set(qn(f'w:{key}'), str(val))

def clean_inline_markdown(text):
    text = re.sub(r'\$(\d+(?:\.\d+)?)\\\%\$', r'\1%', text)
    text = re.sub(r'\$(\d+(?:\.\d+)?)\%\$', r'\1%', text)
    text = re.sub(r'\$(\d+)', r'\1 USD', text)
    text = re.sub(r'\$(\d[\d,]*)\$', r'\1', text)
    text = re.sub(r'\$([\d\.]+)\$', r'\1', text)
    text = re.sub(r'\$<\s*0\.01\s*s\$', '< 0.01s', text)
    text = re.sub(r'<\s*0\.01\s*s', '< 0.01s', text)
    text = re.sub(r'\$\\approx\s*([\d\.]+)\s*s\$', r'≈ \1s', text)
    text = re.sub(r'\\approx\s*([\d\.]+)\s*s', r'≈ \1s', text)
    text = re.sub(r'\$([\d,]+)\s*ms\$', r'\1 ms', text)
    text = re.sub(r'\$(\d+)\s*ms\$', r'\1 ms', text)
    text = re.sub(r'Macro-\$F_1\$', 'Macro-F1', text)
    text = re.sub(r'Macro-F_1', 'Macro-F1', text)
    text = re.sub(r'Predatory F1', 'Predatory F1', text)
    text = re.sub(r'\$F_1\$', 'F1', text)
    text = re.sub(r'\$F_1\^\{\\text\{temporal\}\}\s*/\s*F_1\^\{\\text\{historical\}\}\s*=\s*0\.5354\$',
                  'F1(temporal) / F1(historical) = 0.5354', text)
    text = re.sub(r'F1_temporal\s*/\s*F1_historical\s*=\s*0\.5327\s*/\s*0\.9949\s*=\s*0\.5354',
                  'F1(temporal) / F1(historical) = 0.5327 / 0.9949 = 0.5354', text)
    text = re.sub(r'F1_temporal\s*/\s*F1_historical', 'F1(temporal) / F1(historical)', text)
    text = re.sub(r'\$\\tau_k\s*=\s*0\.80\$', 'τ_k = 0.80', text)
    text = re.sub(r'\$\\tau_k\$', 'τ_k', text)
    text = re.sub(r'\$\\phi_k\$', 'φ_k', text)
    text = re.sub(r'\$h_k\$', 'h_k', text)
    text = re.sub(r'\$c_k\$', 'c_k', text)
    text = re.sub(r'\$x_k\$', 'x_k', text)
    text = re.sub(r'\$p_hat\$', 'p̂', text)
    text = re.sub(r'\$\\hat\{p\}\$', 'p̂', text)
    text = re.sub(r'\\ge\s*', '≥ ', text)
    text = re.sub(r'\\le\s*', '≤ ', text)
    text = text.replace('$', '')
    return text.strip()

def add_formatted_text(p, text, base_font_size=9.5, base_color=(30, 41, 59)):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(part[2:-2])
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(base_font_size)
            run.font.color.rgb = RGBColor(15, 23, 42)
        elif part.startswith('*') and part.endswith('*'):
            run = p.add_run(part[1:-1])
            run.italic = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(base_font_size)
            run.font.color.rgb = RGBColor(*base_color)
        elif part.startswith('`') and part.endswith('`'):
            run = p.add_run(part[1:-1])
            run.font.name = 'Courier New'
            run.font.size = Pt(base_font_size - 0.5)
            run.font.color.rgb = RGBColor(15, 23, 42)
        else:
            run = p.add_run(part)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(base_font_size)
            run.font.color.rgb = RGBColor(*base_color)

def build_docx():
    doc = Document()

    # Base margins: 0.75 in (IEEE Standard)
    sec_top = doc.sections[0]
    sec_top.top_margin = Inches(0.75)
    sec_top.bottom_margin = Inches(0.75)
    sec_top.left_margin = Inches(0.75)
    sec_top.right_margin = Inches(0.75)
    set_section_columns(sec_top, 1)

    # Base style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(9.5)
    font.color.rgb = RGBColor(30, 41, 59)

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # -------------------------------------------------------------------------
    # 1. SECTION 1: HEADER (TITLE, AUTHORS, ABSTRACT, INDEX TERMS)
    # -------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("Cost-Aware Progressive Predatory Journal Detection")
    title_run.bold = True
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(17.0)
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(6)

    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    a_run1 = author_p.add_run("Dr. Swati Shinde,  Suyog Jadhav,  Pratik Jadhav,  Piyush Patel,  Parshwa Nikam\n")
    a_run1.bold = True
    a_run1.font.name = 'Times New Roman'
    a_run1.font.size = Pt(11.0)
    a_run1.font.color.rgb = RGBColor(15, 23, 42)
    a_run2 = author_p.add_run("Department of Computer Engineering, Pimpri Chinchwad College of Engineering (PCCOE), Pune, India\n")
    a_run2.font.name = 'Times New Roman'
    a_run2.font.size = Pt(9.5)
    a_run2.font.color.rgb = RGBColor(51, 65, 85)
    a_run3 = author_p.add_run("Emails: {swati.shinde, suyog.jadhav24, pratik.jadhav24, piyush.patel24, parshwa.nikam24}@pccoepune.org\nTarget Publication Standard: IEEE Transactions on Information Forensics and Security")
    a_run3.italic = True
    a_run3.font.name = 'Times New Roman'
    a_run3.font.size = Pt(8.5)
    a_run3.font.color.rgb = RGBColor(71, 85, 105)
    author_p.paragraph_format.space_after = Pt(10)

    # Extract Abstract
    abs_match = re.search(r'## Abstract\n([\s\S]*?)(?:---|\Z)', md_text)
    if abs_match:
        abs_text = abs_match.group(1).strip()
        abs_p = doc.add_paragraph()
        abs_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_lead = abs_p.add_run("Abstract—")
        r_lead.bold = True
        r_lead.italic = True
        r_lead.font.name = 'Times New Roman'
        r_lead.font.size = Pt(9.0)
        
        lines_abs = [l.strip() for l in abs_text.split('\n') if l.strip()]
        for l in lines_abs:
            l_clean = clean_inline_markdown(l)
            if 'Index Terms' in l_clean or 'Keywords' in l_clean:
                kw_p = doc.add_paragraph()
                kw_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                kw_lead = kw_p.add_run("Index Terms—")
                kw_lead.bold = True
                kw_lead.italic = True
                kw_lead.font.name = 'Times New Roman'
                kw_lead.font.size = Pt(9.0)
                kw_rest = re.sub(r'^(Index Terms|Keywords)—?', '', l_clean).strip()
                add_formatted_text(kw_p, kw_rest, base_font_size=9.0)
                kw_p.paragraph_format.space_after = Pt(10)
            else:
                add_formatted_text(abs_p, l_clean, base_font_size=9.0)
        abs_p.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # 2. SECTION 2: TWO-COLUMN BODY
    # -------------------------------------------------------------------------
    sec_body = doc.add_section(WD_SECTION_START.CONTINUOUS)
    sec_body.top_margin = Inches(0.75)
    sec_body.bottom_margin = Inches(0.75)
    sec_body.left_margin = Inches(0.75)
    sec_body.right_margin = Inches(0.75)
    set_section_columns(sec_body, 2, space_dxa=360)
    current_columns = 2

    # Split body
    sec1_idx = md_text.find('## I. Introduction')
    body_text = md_text[sec1_idx:]

    lines = body_text.split('\n')
    in_table = False
    table_lines = []
    in_refs = False

    def switch_to_columns(num):
        nonlocal current_columns
        if current_columns != num:
            s = doc.add_section(WD_SECTION_START.CONTINUOUS)
            s.top_margin = Inches(0.75)
            s.bottom_margin = Inches(0.75)
            s.left_margin = Inches(0.75)
            s.right_margin = Inches(0.75)
            set_section_columns(s, num, space_dxa=360)
            current_columns = num

    for line in lines:
        line_s = line.strip()

        if line_s.startswith('## Author Biographies'):
            break

        if line_s.startswith('## References'):
            in_refs = True
            # References remain in 2 columns
            switch_to_columns(2)
            ref_h = doc.add_paragraph()
            ref_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ref_h.paragraph_format.space_before = Pt(12)
            ref_h.paragraph_format.space_after = Pt(4)
            r_run = ref_h.add_run("REFERENCES")
            r_run.bold = True
            r_run.font.name = 'Times New Roman'
            r_run.font.size = Pt(10.0)
            r_run.font.color.rgb = RGBColor(15, 23, 42)
            continue

        if in_refs:
            if not line_s:
                continue
            p_ref = doc.add_paragraph()
            p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_ref.paragraph_format.space_after = Pt(2.5)
            p_ref.paragraph_format.left_indent = Inches(0.20)
            p_ref.paragraph_format.first_line_indent = Inches(-0.20)
            r_text = clean_inline_markdown(line_s)
            add_formatted_text(p_ref, r_text, base_font_size=8.0)
            continue

        # ---------------------------------------------------------------------
        # Table Processing (Uncolored IEEE Booktabs Style)
        # ---------------------------------------------------------------------
        if line_s.startswith('|') and line_s.endswith('|'):
            in_table = True
            table_lines.append(line_s)
            continue
        elif in_table:
            in_table = False
            if len(table_lines) >= 2:
                rows_data = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.strip('|').split('|')]
                    if all(re.match(r'^:?-+:?$', c) for c in cells if c):
                        continue
                    if all(c == '' for c in cells):
                        continue
                    rows_data.append(cells)
                
                if rows_data:
                    num_rows = len(rows_data)
                    num_cols = len(rows_data[0])
                    
                    # Wide tables (>= 5 cols or hardware spec table) span 1 full-width column
                    if num_cols >= 5 or num_cols == 3:
                        switch_to_columns(1)
                        total_tbl_w = 7.0
                    else:
                        total_tbl_w = 3.35

                    t = doc.add_table(rows=num_rows, cols=num_cols)
                    t.alignment = WD_TABLE_ALIGNMENT.CENTER

                    # Compute clean column widths
                    if num_cols == 6:
                        widths = [Inches(1.4), Inches(1.0), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.3)]
                    elif num_cols == 7:
                        widths = [Inches(1.2), Inches(0.9), Inches(0.9), Inches(0.9), Inches(1.0), Inches(1.0), Inches(1.1)]
                    elif num_cols == 10:
                        widths = [Inches(0.5), Inches(1.4), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.7), Inches(0.8)]
                    elif num_cols == 8:
                        widths = [Inches(1.2), Inches(1.3), Inches(0.75), Inches(0.75), Inches(0.75), Inches(0.75), Inches(0.75), Inches(0.80)]
                    elif num_cols == 3:
                        widths = [Inches(2.2), Inches(1.8), Inches(3.0)]
                    else:
                        w_per = total_tbl_w / num_cols
                        widths = [Inches(w_per)] * num_cols

                    for r_idx, row_vals in enumerate(rows_data):
                        row = t.rows[r_idx]
                        for c_idx, val in enumerate(row_vals):
                            if c_idx < len(row.cells):
                                cell = row.cells[c_idx]
                                if c_idx < len(widths):
                                    cell.width = widths[c_idx]
                                cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
                                cp = cell.paragraphs[0]
                                cp.paragraph_format.space_after = Pt(1)
                                cp.paragraph_format.space_before = Pt(1)
                                c_clean = clean_inline_markdown(val)
                                
                                # Pure uncolored cell
                                if r_idx == 0:
                                    run = cp.add_run(c_clean)
                                    run.bold = True
                                    run.font.name = 'Times New Roman'
                                    f_sz = 7.0 if num_cols >= 8 else 8.0
                                    run.font.size = Pt(f_sz)
                                    run.font.color.rgb = RGBColor(15, 23, 42)
                                    # Top rule (1.0 pt) and header bottom rule (0.75 pt)
                                    set_cell_border(cell,
                                                    top=dict(val='single', sz=8, color='0F172A'),
                                                    bottom=dict(val='single', sz=6, color='0F172A'),
                                                    left=dict(val='none', sz=0, color='auto'),
                                                    right=dict(val='none', sz=0, color='auto'))
                                else:
                                    f_sz = 6.8 if num_cols >= 8 else 7.8
                                    add_formatted_text(cp, c_clean, base_font_size=f_sz)
                                    # Clean data row borders
                                    if r_idx == num_rows - 1:
                                        set_cell_border(cell,
                                                        top=dict(val='single', sz=2, color='E2E8F0'),
                                                        bottom=dict(val='single', sz=8, color='0F172A'),
                                                        left=dict(val='none', sz=0, color='auto'),
                                                        right=dict(val='none', sz=0, color='auto'))
                                    else:
                                        set_cell_border(cell,
                                                        top=dict(val='none', sz=0, color='auto'),
                                                        bottom=dict(val='single', sz=2, color='E2E8F0'),
                                                        left=dict(val='none', sz=0, color='auto'),
                                                        right=dict(val='none', sz=0, color='auto'))

                    sp = doc.add_paragraph()
                    sp.paragraph_format.space_after = Pt(4)

                    # Resume 2 columns
                    switch_to_columns(2)
            table_lines = []

        if not line_s or line_s.startswith('# ') or line_s.startswith('---'):
            continue

        # ---------------------------------------------------------------------
        # Headings (IEEE Format)
        # ---------------------------------------------------------------------
        if line_s.startswith('## '):
            h_text = clean_inline_markdown(line_s.replace('## ', '').strip())
            h = doc.add_paragraph()
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            h.paragraph_format.space_before = Pt(9)
            h.paragraph_format.space_after = Pt(3)
            h_run = h.add_run(h_text.upper())
            h_run.bold = True
            h_run.font.name = 'Times New Roman'
            h_run.font.size = Pt(10.0)
            h_run.font.color.rgb = RGBColor(15, 23, 42)
            continue
        elif line_s.startswith('### '):
            h_text = clean_inline_markdown(line_s.replace('### ', '').strip())
            h = doc.add_paragraph()
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            h.paragraph_format.space_before = Pt(6)
            h.paragraph_format.space_after = Pt(2)
            h_run = h.add_run(h_text)
            h_run.bold = True
            h_run.italic = True
            h_run.font.name = 'Times New Roman'
            h_run.font.size = Pt(9.5)
            h_run.font.color.rgb = RGBColor(30, 41, 59)
            continue

        # ---------------------------------------------------------------------
        # Images (Figure 1 = full width; Figures 2-7 = column width 3.35 in)
        # ---------------------------------------------------------------------
        if line_s.startswith('!['):
            m = re.search(r'\((.*?)\)', line_s)
            cap_m = re.search(r'!\[(.*?)\]', line_s)
            caption = cap_m.group(1) if cap_m else ''
            if m:
                img_name = os.path.basename(m.group(1))
                img_path = os.path.join(FIG_DIR, img_name)
                if not os.path.exists(img_path):
                    img_path = os.path.join(PROJECT_ROOT, 'paper', 'figures', img_name)
                if os.path.exists(img_path):
                    is_fig1 = "fig1" in img_name.lower()
                    if is_fig1:
                        switch_to_columns(1)
                        img_width = Inches(6.8)
                    else:
                        img_width = Inches(3.35)

                    fig_p = doc.add_paragraph()
                    fig_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    fig_p.paragraph_format.space_before = Pt(4)
                    fig_p.paragraph_format.space_after = Pt(2)
                    run_img = fig_p.add_run()
                    run_img.add_picture(img_path, width=img_width)
                    
                    if caption:
                        cap_p = doc.add_paragraph()
                        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cap_p.paragraph_format.space_before = Pt(2)
                        cap_p.paragraph_format.space_after = Pt(6)
                        cap_run = cap_p.add_run(caption)
                        cap_run.italic = True
                        cap_run.font.name = 'Times New Roman'
                        cap_run.font.size = Pt(8.5)
                        cap_run.font.color.rgb = RGBColor(71, 85, 105)

                    if is_fig1:
                        switch_to_columns(2)
            continue

        # ---------------------------------------------------------------------
        # Body Paragraphs (Clean, no leading dashes)
        # ---------------------------------------------------------------------
        line_clean = re.sub(r'^[-\*]\s+', '', line_s)
        line_clean = clean_inline_markdown(line_clean)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.line_spacing = 1.12
        add_formatted_text(p, line_clean, base_font_size=9.5)

    doc.save(DOCX_PATH)
    print(f"Successfully generated IEEE Two-Column DOCX at: {DOCX_PATH}")

if __name__ == '__main__':
    build_docx()
