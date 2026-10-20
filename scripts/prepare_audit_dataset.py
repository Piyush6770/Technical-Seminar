"""
Dataset Preparation and Audit Partitioning Module
Aligns strictly with Section 2 of prompt.md specification.
"""

import os
import shutil
import hashlib
import stat
import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_SHA256 = "d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328"

def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_csv = os.path.join(root_dir, "final_combined_journal_dataset.csv")
    
    assert os.path.exists(source_csv), f"Source dataset {source_csv} does not exist!"
    
    # 1. Verify SHA-256
    actual_sha = compute_sha256(source_csv)
    print(f"Source Dataset SHA-256: {actual_sha}")
    assert actual_sha == TARGET_SHA256, f"Checksum mismatch! Expected {TARGET_SHA256}, got {actual_sha}"
    
    # 2. Setup audit directories
    audit_data_dir = os.path.join(root_dir, "audit", "data")
    audit_splits_dir = os.path.join(root_dir, "audit", "splits")
    os.makedirs(audit_data_dir, exist_ok=True)
    os.makedirs(audit_splits_dir, exist_ok=True)
    
    # 3. Create frozen read-only copy
    frozen_csv = os.path.join(audit_data_dir, "final_combined_journal_dataset_frozen_readonly.csv")
    if os.path.exists(frozen_csv):
        # make writable temporarily to update if needed
        os.chmod(frozen_csv, stat.S_IWRITE)
    shutil.copy2(source_csv, frozen_csv)
    os.chmod(frozen_csv, stat.S_IREAD)
    print(f"Frozen read-only copy created: {frozen_csv}")
    
    # 4. Load full dataset
    df = pd.read_csv(source_csv)
    print(f"Loaded {len(df)} rows from {source_csv}")
    
    # 5. Extract Historical Baseline (first 2,046 records)
    historical_df = df.iloc[:2046].copy()
    # open_access == '-' is predatory (1), else legitimate (0)
    historical_df["label"] = (historical_df["open_access"] == "-").astype(int)
    historical_df["cohort"] = "HISTORICAL"
    
    legit_hist = (historical_df["label"] == 0).sum()
    pred_hist = (historical_df["label"] == 1).sum()
    print(f"Historical cohort: Total={len(historical_df)}, Legit={legit_hist}, Predatory={pred_hist}")
    assert legit_hist == 1213 and pred_hist == 833, f"Historical cohort count mismatch!"
    
    # Stratified 80/20 split (1636 train, 410 val, seed=42)
    train_idx, val_idx = train_test_split(
        historical_df.index,
        test_size=410,
        random_state=42,
        stratify=historical_df["label"]
    )
    
    train_df = historical_df.loc[train_idx].copy().sort_values("id")
    val_df = historical_df.loc[val_idx].copy().sort_values("id")
    
    train_legit = (train_df["label"] == 0).sum()
    train_pred = (train_df["label"] == 1).sum()
    val_legit = (val_df["label"] == 0).sum()
    val_pred = (val_df["label"] == 1).sum()
    
    print(f"Historical Train: Total={len(train_df)}, Legit={train_legit}, Predatory={train_pred}")
    print(f"Historical Val:   Total={len(val_df)}, Legit={val_legit}, Predatory={val_pred}")
    assert len(train_df) == 1636 and train_legit == 970 and train_pred == 666
    assert len(val_df) == 410 and val_legit == 243 and val_pred == 167
    
    train_path = os.path.join(audit_splits_dir, "historical_train.csv")
    val_path = os.path.join(audit_splits_dir, "historical_val.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    
    # 6. Quarantined Unlabeled Pool (rows 2046 to 3727: exactly 1,682 serials)
    quarantine_df = df.iloc[2046:3728].copy()
    quarantine_df["cohort"] = "QUARANTINED_UNLABELED"
    quarantine_df["label"] = -1  # Unlabeled
    print(f"Quarantined pool: Total={len(quarantine_df)}")
    assert len(quarantine_df) == 1682, f"Quarantine count mismatch: {len(quarantine_df)}"
    
    quarantine_path = os.path.join(audit_splits_dir, "audited_uncertain_records.csv")
    quarantine_df.to_csv(quarantine_path, index=False)
    
    # 7. Untouched Temporal Test Cohort (rows 3728 to 5527: 1,800 records)
    # 1,621 legitimate (rows 3728 to 5348) + 179 predatory (rows 5349 to 5527)
    temporal_legit_df = df.iloc[3728:5349].copy()
    temporal_legit_df["label"] = 0
    temporal_legit_df["cohort"] = "TEMPORAL_TEST_UNTOUCHED"
    
    temporal_pred_df = df.iloc[5349:5528].copy()
    temporal_pred_df["label"] = 1
    temporal_pred_df["cohort"] = "TEMPORAL_TEST_UNTOUCHED"
    
    temporal_test_df = pd.concat([temporal_legit_df, temporal_pred_df], axis=0).sort_values("id")
    temp_legit = (temporal_test_df["label"] == 0).sum()
    temp_pred = (temporal_test_df["label"] == 1).sum()
    
    print(f"Temporal Test: Total={len(temporal_test_df)}, Legit={temp_legit}, Predatory={temp_pred}")
    assert len(temporal_test_df) == 1800 and temp_legit == 1621 and temp_pred == 179
    
    temporal_test_path = os.path.join(audit_splits_dir, "temporal_test_cohort_untouched.csv")
    temporal_test_df.to_csv(temporal_test_path, index=False)
    
    # 8. Evaluation Splits Manifest
    manifest_rows = [
        {
            "split_name": "HISTORICAL_TRAIN",
            "filename": "historical_train.csv",
            "total_records": len(train_df),
            "legitimate_records": train_legit,
            "predatory_records": train_pred,
            "era": "Pre-2021",
            "purpose": "Model optimization & representation learning",
            "sha256": compute_sha256(train_path)
        },
        {
            "split_name": "HISTORICAL_VAL",
            "filename": "historical_val.csv",
            "total_records": len(val_df),
            "legitimate_records": val_legit,
            "predatory_records": val_pred,
            "era": "Pre-2021",
            "purpose": "Hyperparameter tuning, calibration & stopping policy threshold optimization",
            "sha256": compute_sha256(val_path)
        },
        {
            "split_name": "TEMPORAL_TEST_UNTOUCHED",
            "filename": "temporal_test_cohort_untouched.csv",
            "total_records": len(temporal_test_df),
            "legitimate_records": temp_legit,
            "predatory_records": temp_pred,
            "era": "Post-2020 (2021-2026)",
            "purpose": "Strictly held-out out-of-distribution temporal generalization evaluation",
            "sha256": compute_sha256(temporal_test_path)
        },
        {
            "split_name": "QUARANTINED_UNLABELED",
            "filename": "audited_uncertain_records.csv",
            "total_records": len(quarantine_df),
            "legitimate_records": 0,
            "predatory_records": 0,
            "era": "Post-2020 (2021-2026)",
            "purpose": "Quarantined pool to prevent label noise; semi-supervised exploration",
            "sha256": compute_sha256(quarantine_path)
        }
    ]
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = os.path.join(audit_splits_dir, "evaluation_splits_manifest.csv")
    manifest_df.to_csv(manifest_path, index=False)
    print(f"Manifest written: {manifest_path}")
    print("\nManifest summary:")
    print(manifest_df[["split_name", "total_records", "legitimate_records", "predatory_records", "era"]])

if __name__ == "__main__":
    main()
