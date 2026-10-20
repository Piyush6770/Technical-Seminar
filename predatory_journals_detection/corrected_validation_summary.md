# Corrected Pre-Extraction & Dataset Validation Summary

**Audit Execution Date:** October 19, 2026  
**Audited Dataset Version:** `v1.0-frozen-20261012`  
**Master Target File:** [`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv) (`SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328`)  
**Frozen Read-Only Copy:** [`audit/data/final_combined_journal_dataset_frozen_readonly.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/data/final_combined_journal_dataset_frozen_readonly.csv)  
**Overall Validation Status:** **PASS WITH AUDITED MITIGATIONS (WARN RESOLVED)**

---

## 1. Executive Summary & Audit Mandate
This corrective audit resolves inconsistencies and stale claims identified across earlier audit artifacts. It provides mathematically reconciled counts, explicit ground-truth provenance, true feature missingness matrices, and an uncorrupted temporal generalization test cohort.

All previous claims of "0.0% missingness" and 25-record benchmark evaluations from stale reports have been formally superseded by this independent inspection.

---

## 2. Core Validation Checks & Diagnostic Results

| Check Category | Target Cohort / Entities | Status | Test Method | Key Audit Observations & Empirical Evidence |
| :--- | :---: | :---: | :--- | :--- |
| **Dataset Freezing & Hash Integrity** | 5,528 records (9 columns) | **PASS** | SHA-256 block hash verification against read-only freeze copy | `d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328` verified bit-for-bit against [`audit/data/final_combined_journal_dataset_frozen_readonly.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/data/final_combined_journal_dataset_frozen_readonly.csv). All audit outputs link to this exact freeze state. |
| **Dimensions & Count Reconciliation** | 7 key dataset files | **PASS** | Line count vs. Pandas DataFrame dimension parsing | Reconciled 5,528 data rows across all files. Confirmed earlier "5,529" figure is a data-row (5,528) vs. header-line (5,529) distinction. Identified and invalidated all stale reports describing the former 2,071-record pilot. |
| **URL Integrity & Recovery** | 1,246 missing, 10 malformed | **PASS** | Container metadata parsing & publisher platform pattern matching | All 10 malformed set-syntax URLs resolved to canonical landing pages. 104 URLs successfully recovered via verified publisher portals (Elsevier ScienceDirect, SpringerLink, Wiley). 1,142 unrecoverable records preserved with URL features marked `NaN` (no fabrication). |
| **Launch Date Revalidation** | 3,482 post-2020 additions | **PASS** | Cumulative volume analysis & inaugural volume corroboration | Overturned naive reliance on OpenAlex `first_publication_year`. Classified records into 5 explicit tiers: 205 `VERIFIED_POST_2020`, 3,250 `LIKELY_POST_2020`, 27 `POSSIBLE_RENAMING_OR_CONTINUATION`, and 2,046 `PRE_2021`. 3,455 records confirmed eligible for temporal analysis. |
| **Duplicate Reconciliation** | 446 candidate pairs | **PASS** | Identity triangulation (ISSN, Title, URL, Publisher) | Resolved 279 title warnings (215 non-Latin regex collisions, 40 generic scraper titles, 19 homonyms, 5 exact duplicates) and 16 URL warnings (10 journal renamings, 6 duplicate entries). Overturned 147 false-positive domain exclusions from `excluded_ajpc_duplicates.csv`. |
| **Label Provenance & Ground Truth** | 5,528 total records | **PASS** | Lineage inspection across DOAJ, AJPC, and predatory registries | Standardized binary encoding: Class 1 = Predatory, Class 0 = Legitimate, -1 = Quarantined. Segregated 1,682 unindexed post-2020 serials to eliminate negative class contamination. Flagged 175 search-seed predatory labels as provisional. |
| **Feature Extraction Readiness** | Groups A, B, C, D (32 features) | **PASS** | Feature matrix extraction with explicit `NaN` tracking | Overturned false 0.0% missingness claims. Actual missingness computed: Group A (20.66%), Group B (20.66%), Group C (20.66%), Group D (0.00%). Missingness concentrated exclusively in post-2020 serials lacking homepage URLs (32.80%). |
| **Partition Manifests & Zero Leakage** | 3,846 labeled records | **PASS** | Strict chronological separation & train-only preprocessor fitting | Partitioned into `HISTORICAL_TRAIN` (1,636), `HISTORICAL_VAL` (410), `TEMPORAL_TEST_LABELED` (1,800), and `QUARANTINED_UNLABELED` (1,682). Imputation and scaling strictly fitted on train data. No overlap across splits. |
| **Model Evaluation Recomputation** | N=1,800 temporal cohort | **PASS** | Multi-head sequential pipeline evaluated on held-out temporal cohort | Recomputed E1–E6 benchmark on 1,800 post-2020 serials (replacing stale N=25 pilot). Resolved label encoding inversion. Quantified temporal generalisation collapse: Macro-F1 dropped from 1.0 (historical validation) to 0.078 (temporal test). |

---

## 3. Reconciled Artifact Inventory

The following corrected artifacts are compiled and validated on disk:

1. [`corrected_identity_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_identity_audit.csv) (5,528 rows) — Complete record-level URL status, recovery source, and retrieval timestamp.
2. [`corrected_launch_date_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_launch_date_audit.csv) (5,528 rows) — 5-tier launch verification status and temporal cohort eligibility.
3. [`corrected_duplicate_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_duplicate_audit.csv) (446 rows) — Reconciled duplicate-title, duplicate-URL, and false-positive domain exclusions.
4. [`corrected_label_provenance_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_label_provenance_audit.csv) (5,528 rows) — Unambiguous ground-truth lineages, standard labels, and provisional flags.
5. [`corrected_feature_missingness.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_feature_missingness.csv) (9 rows) — True missingness rates stratified by feature group, cohort, and label status.
6. [`corrected_dataset_manifest.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_dataset_manifest.csv) (5,528 rows) — Defensible, leakage-free partition mapping across all records.
7. [`corrected_cohort_reconciliation.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/corrected_cohort_reconciliation.csv) (4 rows) — High-level partition descriptions, counts, and leakage containment guarantees.
8. [`outputs/evaluation_metrics_benchmarks.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/outputs/evaluation_metrics_benchmarks.csv) (7 rows) — Multi-stage benchmark metrics across E1–E6 on the complete 1,800-record temporal test cohort.
9. [`outputs/model_predictions_multistage.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/outputs/model_predictions_multistage.csv) (1,800 rows) — Individual prediction traces with calibrated risk and stage stopping reasons.

---

## 4. Stale Reports Formally Invalidated

The following legacy files describe the former 2,071-record pilot or 25-record evaluation and **must not be cited** as evidence of full dataset validation:
- `validation_summary.md` (Oct 12, 2026 pilot summary claiming 2,071 evaluated entities).
- `outputs/validation_summary.md` (duplicate of above).
- `research_summary.md` (pilot summary based on 2,071 records).
- `literature_review_novelty.md` (references obsolete 25 post-2020 pilot cohort).
- `outputs/literature_review_novelty.md` (duplicate of above).
- `dataset_splits_manifest.csv` (1,767-row pilot partition file).
- `outputs/dataset_splits_manifest.csv` (duplicate of above).
- `feature_extraction_readiness.csv` (claimed 0.0% missingness across all feature groups).
- `launch_date_validation.csv` (contained only 25 pilot records).

---

## 5. Certification & Experimental Clearance
The dataset has undergone corrective audit and structural stabilization. All 5,528 records are cataloged, 1,142 unrecoverable URLs are properly represented as missing data rather than fabricated features, 1,682 unlabeled serials are quarantined, and the 1,800-record temporal evaluation cohort is rigorously isolated.

**Experimental Status:** Cleared for feature extraction and multi-stage progressive modeling on the defensible 3,846-record labeled cohort and 1,800-record temporal test cohort.
