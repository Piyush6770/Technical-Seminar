# Dataset Curation & Provenance Reconciliation

This directory contains the data engineering pipeline, provenance audits, and reconciliation scripts used to assemble, verify, and freeze the audited research corpus ($N=5,528$ academic serials).

---

## Directory Overview

The curation pipeline reconciles raw records from historical predatory lists (Beall's list, Cabells), contemporary open access directories (DOAJ), and registry metadata (Crossref, OpenAlex, official ISSN portals) into frozen research partitions.

### Core Datasets

| File | Description | Records |
| :--- | :--- | :--- |
| `audited_verified_dataset.csv` | Reconciled records with validated labels and verified launch dates. | 3,846 |
| `audited_uncertain_records.csv` | Serials with conflicting provenance or disputed status (quarantined). | 1,682 |
| `audited_excluded_records.csv` | Malformed, unreachable, or non-journal records excluded from evaluation. | 142 |
| `final_combined_journal_dataset.csv` | Consolidated dataset prior to partition freezing. | 5,528 |
| `new_post2020_journals.csv` | Contemporary serials (2021–2026) for out-of-distribution temporal evaluation. | 1,800 |
| `dataset_hashes.txt` | SHA-256 cryptographic signatures for all frozen tables. | — |

---

## Reconciliation Pipeline Steps

The pipeline is structured into 7 sequential audit and verification stages:

```
[Raw Sources: Beall's, DOAJ, Crossref, OpenAlex, ISSN]
                       │
                       ▼
         step1_verify_freeze.py       ──► Verifies input checksums and locks base tables
                       │
                       ▼
         step2_inspect_urls.py        ──► Resolves redirects, TLD anomalies, and domain canonicals
                       │
                       ▼
         step3_inspect_launch_dates.py──► Confirms launch years for temporal partitioning
                       │
                       ▼
         step4_inspect_continuations.py──► Resolves renamed, merged, and continuation serials
                       │
                       ▼
         step5_inspect_duplicates.py  ──► Deduplicates records by ISSN-L and canonical domain
                       │
                       ▼
         step6_reconcile_and_audit.py ──► Resolves conflicting labels & applies provenance rules
                       │
                       ▼
         step7_feature_and_eval.py    ──► Extracts 4-stage features & evaluates baseline models
```

### Script Reference

1. **`step1_verify_freeze.py`**
   - Validates that source files match expected cryptographic hashes before processing.
   - Prevents unintended data drift during pipeline execution.

2. **`step2_inspect_urls.py`**
   - Inspects URL structures, resolves DNS reachability, handles HTTPS redirects, and strips tracking parameters.

3. **`step3_inspect_launch_dates.py`**
   - Determines earliest documented publication year via ISSN Portal, Crossref earliest DOI, or Wayback Machine archives.
   - Assigns records to either historical ($<2021$) or contemporary ($2021\text{--}2026$) cohorts.

4. **`step4_inspect_continuations.py`**
   - Tracks journals that changed publishers, migrated domains, or updated ISSNs to prevent spurious duplicate entries.

5. **`step5_inspect_duplicates.py`**
   - Identifies cross-list duplicates using normalized title matching, ISSN-L mapping, and URL canonicalization.

6. **`step6_reconcile_and_audit.py`**
   - Applies tri-state adjudication: verified legitimate, high predatory risk, or quarantined for human librarian review.
   - Generates `corrected_cohort_reconciliation.csv` and `corrected_label_provenance_audit.csv`.

7. **`step7_feature_and_eval.py`**
   - Extracts the 42 progressive features across Groups A, B, C, and D.
   - Executes baseline evaluations (XGBoost, Random Forest) and saves intermediate metric summaries.

8. **`build_pipeline.py`**
   - Master automation script that coordinates end-to-end data preparation, feature extraction, and split generation.

---

## Audit Documentation

- **`corrected_dataset_audit.md`**: Complete reconciliation report documenting label corrections, duplicate resolutions, and exclusion rationales.
- **`audit_dataset_summary.md`**: Summary of the final 5,528-record corpus distribution across eras and classes.
- **`corrected_validation_summary.md`**: Integrity verification confirming that zero test serials leak into training partitions.
- **`literature_review_novelty.md`**: Analysis of differences between our dataset curation methodology and prior static benchmarks.

---

## Frozen Checksums

All finalized splits used in the research paper are mirrored under `audit/data/` and `audit/splits/` at the repository root. Master frozen file digest:
```
SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328
```
