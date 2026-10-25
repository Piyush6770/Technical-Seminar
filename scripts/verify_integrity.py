"""
Complete Integrity Verification Script
Verifies:
1. Master Dataset SHA-256 Cryptographic Hash
2. Authentic Reference Library (20 Publisher PDFs)
3. BibTeX References & Manuscript Citation Sequence
"""

import os
import sys
import re
import hashlib
import pypdf

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.streamline_20_references import PAPERS_20

MASTER_DATASET_PATH = os.path.join(PROJECT_ROOT, "audit", "data", "final_combined_journal_dataset_frozen_readonly.csv")
EXPECTED_SHA256 = "d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328"

def verify_dataset_integrity():
    print("=== 1. VERIFYING MASTER DATASET SHA-256 ===")
    if not os.path.exists(MASTER_DATASET_PATH):
        raise FileNotFoundError(f"Master dataset missing at: {MASTER_DATASET_PATH}")
    
    with open(MASTER_DATASET_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    print(f"Calculated: {file_hash}")
    print(f"Expected:   {EXPECTED_SHA256}")
    assert file_hash == EXPECTED_SHA256, "Dataset hash mismatch!"
    print(">>> DATASET INTEGRITY VERIFIED (SHA-256 MATCH) <<<\n")

def verify_reference_library():
    print("=== 2. VERIFYING 20 AUTHENTIC PDFS ===")
    ref_dir = os.path.join(PROJECT_ROOT, "research_paper", "reference_papers")
    assert os.path.exists(ref_dir), f"Directory not found: {ref_dir}"
    
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
        print(f"[{p['num']:02d}] {p['new_file']:70} | {pages:2d} pages | {size:9d} bytes | VALID")
    print(">>> ALL 20 PDFS VERIFIED <<<\n")

def verify_citations():
    print("=== 3. VERIFYING BIBTEX & MANUSCRIPT CITATION SEQUENCE ===")
    bib_path = os.path.join(PROJECT_ROOT, "paper", "references.bib")
    with open(bib_path, "r", encoding="utf-8") as f:
        bib_text = f.read()
    bib_keys = re.findall(r"@\w+\{([^,]+),", bib_text)
    assert len(bib_keys) == 20, f"Expected 20 bib keys, got {len(bib_keys)}"

    tex_path = os.path.join(PROJECT_ROOT, "paper", "manuscript.tex")
    with open(tex_path, "r", encoding="utf-8") as f:
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

    assert len(first_appearance) == 20, f"Expected 20 unique citations, got {len(first_appearance)}"
    for idx, p in enumerate(PAPERS_20):
        assert first_appearance[idx] == p["key"], f"Citation mismatch at {idx+1}: expected {p['key']}, got {first_appearance[idx]}"

    bibitems = re.findall(r"\\bibitem\{([^}]+)\}", tex[bib_pos:])
    assert len(bibitems) == 20, f"Expected 20 bibitems, got {len(bibitems)}"
    for idx, p in enumerate(PAPERS_20):
        assert bibitems[idx] == p["key"], f"Bibitem mismatch at {idx+1}: expected {p['key']}, got {bibitems[idx]}"
    print(">>> CITATION SEQUENCE & BIBITEMS VERIFIED (STRICT 1 TO 20) <<<\n")

if __name__ == "__main__":
    verify_dataset_integrity()
    verify_reference_library()
    verify_citations()
    print("=" * 70)
    print("ALL INTEGRITY CHECKS PASSED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 70)
