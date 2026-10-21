import os
import re
import pypdf
from scripts.generate_complete_pdf_library import PAPERS

def run_checks():
    print("=== 1. VERIFYING PDF FILES ===")
    ref_dir = r"c:\Users\Pratik\Engineering\3rd Year\TS\research_paper\reference_papers"
    pdf_errors = 0
    for p in PAPERS:
        pdf_path = os.path.join(ref_dir, p["filename"])
        if not os.path.exists(pdf_path):
            print(f"MISSING PDF: {p['filename']}")
            pdf_errors += 1
            continue
        try:
            reader = pypdf.PdfReader(pdf_path)
            pages = len(reader.pages)
            if pages == 0:
                print(f"EMPTY PDF: {p['filename']}")
                pdf_errors += 1
        except Exception as e:
            print(f"INVALID PDF: {p['filename']} - {e}")
            pdf_errors += 1
    print(f"PDF check completed with {pdf_errors} errors across {len(PAPERS)} files.")

    print("\n=== 2. VERIFYING BIBTEX KEYS ===")
    with open("paper/references.bib", "r", encoding="utf-8") as f:
        bib_text = f.read()
    bib_keys = re.findall(r"@\w+\{([^,]+),", bib_text)
    bib_missing = [p["key"] for p in PAPERS if p["key"] not in bib_keys]
    print(f"BibTeX total entries: {len(bib_keys)}, missing from PAPERS: {bib_missing}")

    print("\n=== 3. VERIFYING MANUSCRIPT CITATION SEQUENCE ===")
    with open("paper/manuscript.tex", "r", encoding="utf-8") as f:
        tex = f.read()

    bib_pos = tex.find(r"\begin{thebibliography}")
    text_body = tex[:bib_pos]
    cites = re.findall(r"\\cite\{([^}]+)\}", text_body)
    first_appearance = []
    for c in cites:
        for k in c.split(","):
            k = k.strip()
            if k and k not in first_appearance:
                first_appearance.append(k)

    seq_errors = 0
    for idx, p in enumerate(PAPERS):
        cited_key = first_appearance[idx] if idx < len(first_appearance) else None
        if cited_key != p["key"]:
            print(f"Sequence error at index {idx+1}: Expected {p['key']}, Got {cited_key}")
            seq_errors += 1
    if seq_errors == 0:
        print(f"All {len(first_appearance)} unique citations appear in STRICT SEQUENTIAL ORDER (1 to {len(PAPERS)})!")
    else:
        print(f"Sequence errors found: {seq_errors}")

    print("\n=== 4. VERIFYING BIBITEMS ===")
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", tex[bib_pos:])
    bibitem_errors = 0
    for idx, p in enumerate(PAPERS):
        bkey = bibitems[idx] if idx < len(bibitems) else None
        if bkey != p["key"]:
            print(f"Bibitem error at index {idx+1}: Expected {p['key']}, Got {bkey}")
            bibitem_errors += 1
    if bibitem_errors == 0:
        print(f"All {len(bibitems)} bibitems match PAPERS in identical order!")
    else:
        print(f"Bibitem errors: {bibitem_errors}")

if __name__ == "__main__":
    run_checks()
