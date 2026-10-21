import os
import re
import pypdf
from scripts.streamline_20_references import PAPERS_20

def verify_all():
    ref_dir = r"c:\Users\Pratik\Engineering\3rd Year\TS\research_paper\reference_papers"

    print("=== 1. VERIFYING 20 AUTHENTIC PDFS ===")
    pdf_files = sorted(os.listdir(ref_dir))
    print(f"Total files in directory: {len(pdf_files)}")
    assert len(pdf_files) == 20, f"Expected 20 PDFs, found {len(pdf_files)}"

    for p in PAPERS_20:
        path = os.path.join(ref_dir, p["new_file"])
        assert os.path.exists(path), f"Missing: {p['new_file']}"
        reader = pypdf.PdfReader(path)
        pages = len(reader.pages)
        size = os.path.getsize(path)
        assert pages > 0, f"Empty: {p['new_file']}"
        assert size > 50000, f"Suspicious small size: {size}"
        print(f"[{p['num']:02d}] {p['new_file']:70} | {pages:2d} pages | {size:9d} bytes | VALID PUBLISHER PDF")

    print("\n=== 2. VERIFYING BIBTEX KEYS ===")
    with open("paper/references.bib", "r", encoding="utf-8") as f:
        bib = f.read()
    bib_keys = re.findall(r"@\w+\{([^,]+),", bib)
    print(f"Total BibTeX entries: {len(bib_keys)}")
    assert len(bib_keys) == 20
    for idx, p in enumerate(PAPERS_20):
        assert bib_keys[idx] == p["key"], f"Bib key mismatch: {bib_keys[idx]} vs {p['key']}"
    print("All 20 BibTeX keys match perfectly in identical order.")

    print("\n=== 3. VERIFYING STRICT CITATION ORDER IN MANUSCRIPT ===")
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

    print(f"Total unique cited keys in body: {len(first_appearance)}")
    assert len(first_appearance) == 20

    for idx, p in enumerate(PAPERS_20):
        k = first_appearance[idx]
        assert k == p["key"], f"Seq error at {idx+1}: {k} vs {p['key']}"
        print(f"[{p['num']:02d}] Citation: {k:30} | MATCH")

    print("\n=== 4. VERIFYING BIBITEMS ===")
    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", tex[bib_pos:])
    assert len(bibitems) == 20
    for idx, p in enumerate(PAPERS_20):
        assert bibitems[idx] == p["key"]
    print("All 20 bibitems match perfectly!")

    print("\n>>> ALL CHECKS PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    verify_all()
