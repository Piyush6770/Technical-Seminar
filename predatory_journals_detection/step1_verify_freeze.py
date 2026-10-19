import os
import sys
import hashlib
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"

def get_file_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("--- PHASE 1: FREEZE & CHECKSUM VERIFICATION ---")
files_to_hash = [
    "final_combined_journal_dataset.csv",
    "audit/data/final_combined_journal_dataset_frozen_readonly.csv",
    "new_post2020_journals.csv",
    "journal_record_provenance.csv",
    "journal_credibility_audit.csv",
    "audited_verified_dataset.csv",
    "audited_uncertain_records.csv",
    "audited_excluded_records.csv",
    "duplicate_audit.csv",
    "excluded_ajpc_duplicates.csv",
    "structural_validation.csv",
    "duplicate_candidates.csv",
    "dataset_splits_manifest.csv",
    "balanced_training_manifest.csv",
    "evaluation_metrics_benchmarks.csv",
    "feature_extraction_readiness.csv",
    "model_predictions_multistage.csv",
    "identity_verification.csv",
    "label_provenance_audit.csv",
    "launch_date_audit.csv",
    "malformed_records.csv",
    "validation_summary.md",
    "audit_dataset_summary.md"
]

inventory = []
for fname in files_to_hash:
    fpath = os.path.join(BASE_DIR, fname)
    sha = get_file_sha256(fpath)
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        with open(fpath, 'rb') as fp:
            line_count = sum(1 for _ in fp)
        try:
            df = pd.read_csv(fpath, low_memory=False)
            data_rows, cols = df.shape
        except Exception:
            data_rows, cols = None, None
        inventory.append({
            "file": fname,
            "exists": True,
            "bytes": size,
            "line_count": line_count,
            "data_rows": data_rows,
            "columns": cols,
            "sha256": sha
        })
    else:
        inventory.append({
            "file": fname,
            "exists": False,
            "bytes": None,
            "line_count": None,
            "data_rows": None,
            "columns": None,
            "sha256": None
        })

df_inv = pd.DataFrame(inventory)
print(df_inv.to_string())

print("\n--- PHASE 2: VERIFICATION OF ACTUAL DIMENSIONS & DATA-ROW VS HEADER DISTINCTION ---")
key_files = [
    "final_combined_journal_dataset.csv",
    "new_post2020_journals.csv",
    "journal_record_provenance.csv",
    "journal_credibility_audit.csv",
    "audited_verified_dataset.csv",
    "audited_uncertain_records.csv",
    "audited_excluded_records.csv"
]
for kf in key_files:
    item = next(x for x in inventory if x["file"] == kf)
    print(f"File: {kf}")
    print(f"  Physical line count: {item['line_count']} (1 header + {item['line_count'] - 1} data lines)")
    print(f"  Pandas DataFrame shape: {item['data_rows']} rows x {item['columns']} columns")
    print(f"  SHA-256: {item['sha256']}")
