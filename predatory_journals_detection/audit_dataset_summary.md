# Independent Audit and Dataset Summary Report

## 1. Executive Summary & Audit Mandate
This document reports the findings of an independent data audit and methodological review of the journal detection datasets in this repository. 

The audit evaluated:
1. The historical benchmark dataset from the NCTU DCS Lab study (*Scientific Reports*, 2023).
2. The newly expanded collection compiled via automated API discovery.
3. The generated 5,529-line combined file ([`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv)).

**Core Audit Finding**: 
The dataset contains **5,528 data rows** (plus 1 header row). The historical baseline of **2,046 journals** (1,213 legitimate whitelist + 833 predatory blacklist) is preserved bit-for-bit in rows 1–2,046. The newly discovered post-2020 expansion comprises **3,482 serial records**. 

Crucially, **credibility labels are not interchangeable with record discovery**:
- **1,621** post-2020 additions have independent verification of legitimacy (DOAJ indexing, COPE compliance, verified university/society publishers).
- **179** post-2020 additions have documented evidence of predatory characteristics (flagged publisher registries, aggressive acceptance promises, lack of certified indexing).
- **1,682** post-2020 serials are verified to exist and launched after 2020, but currently lack definitive secondary indexing or blacklisting evidence. Treating these 1,682 records as confirmed labels would introduce severe label noise. They have therefore been quarantined into [`audited_uncertain_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_uncertain_records.csv).
- The defensible, ground-truth labeled cohort comprises **3,846 records** (1,012 predatory + 2,834 legitimate).

---

## 2. File Inventory, Hashes & Freeze State

### Frozen Read-Only Audit Copy
- **Source File**: [`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv)
- **SHA-256 Checksum**: `d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328`
- **Read-Only Audit Copy**: [`audit/data/final_combined_journal_dataset_frozen_readonly.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/data/final_combined_journal_dataset_frozen_readonly.csv) (file mode `0444`)
- **Dimensions**: Exactly 5,529 lines (1 header line + 5,528 data rows), 9 columns.

### Complete Inventory of Related Artifacts
The full inventory is cataloged in [`audit_file_inventory.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit_file_inventory.csv) and [`dataset_hashes.txt`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/dataset_hashes.txt):

| File Path | Total Rows | Columns | SHA-256 (Prefix) | Role & Audit Verification |
| :--- | :---: | :---: | :---: | :--- |
| `final_combined_journal_dataset.csv` | 5,529 | 9 | `d775c92cbda3...` | Target generated dataset (2,046 historical + 3,482 post-2020). |
| `web_crawling/whitelist.csv` | 1,213 | 9 | `c94d828fc0ff...` | Authoritative AJPC legitimate whitelist (SCImago/DOAJ). |
| `web_crawling/spj_blacklist.csv` | 1 (833 URLs) | 833 | `59283fe0fffb...` | Authoritative AJPC predatory blacklist URLs. |
| `web_crawling/blacklist_dataset.csv` | 833 | 566 | `d98efc70a218...` | Scraped text tokens for the 833 predatory journals. |
| `preprocess/allj_content.csv` | 2,046 | 1,157 | `3b27b3f93556...` | Vectorized text representations ($1,213 + 833 = 2,046$). |
| `training/JournalVector.csv` | 2,046 | 850 | `f7efd66311ce...` | 850-dimensional TF-IDF training feature matrix. |
| `training/Train_X.csv` | 1,636 | 850 | `23ca1376e100...` | 80% train split feature matrix. |
| `training/Train_Y.csv` | 1 (1,636 items) | 1,636 | `799ca9563212...` | 80% train labels: 666 predatory (`0`), 970 legitimate (`1`). |
| `training/Test_X.csv` | 410 | 850 | `b49195d8daef...` | 20% test split feature matrix. |
| `training/Test_Y.csv` | 1 (410 items) | 410 | `59be78174780...` | 20% test labels: 167 predatory (`0`), 243 legitimate (`1`). |
| `new_post2020_journals.csv` | 3,483 | 24 | `34e0622bcf23...` | Discovered post-2020 journal records with full metadata. |
| `data/raw_discovered_candidates.jsonl`| 3,644 | JSON | `141b777a9be3...` | Checkpointed raw API responses from DOAJ and OpenAlex. |
| `outputs/discovery_logs.jsonl` | 48 | JSON | `20dca5e9bc5a...` | Log of paginated API queries and response metrics. |

---

## 3. Discrepancy Resolution: 2,046 vs. 2,700 Records
A persistent question in previous summaries was whether the original AJPC dataset contained 2,046 or 2,700 records:
1. **Definitive Finding**: The NCTU DCS Lab experimental benchmark is **exactly 2,046 journals**. Every data split, text matrix, and TF-IDF file across `preprocess/` and `training/` has exactly 2,046 entries.
2. **Origin of the 2,700 Figure**: In early unmerged web crawling directories (`web/` and `web_crawling/`), multiple exploratory lists existed:
   - `web/spj_blacklist.csv` (2,499 URLs)
   - `web_crawling/beall_blacklist.csv` (1,483 URLs)
   - `web/bih_whitelist.csv` (3,687 URLs)
   The figure "2,700 journals (833 predatory + 1,867 remaining)" was a provisional hypothesis formed prior to inspecting the repository's feature files. No 1,867 unlabeled records were dropped or omitted.

---

## 4. Structural Integrity Audit Results
Documented in [`structural_validation.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/structural_validation.csv), [`duplicate_candidates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/duplicate_candidates.csv), and [`malformed_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/malformed_records.csv):

1. **Title Completeness**: 100% of rows have a non-empty title string.
2. **Missing Homepage URLs**: 1,246 records in the post-2020 cohort lack an explicit homepage URL in their OpenAlex metadata (they possess full ISSN, publisher, and DOI container metadata).
3. **Malformed URLs**: 10 records had non-standard URL formatting.
4. **Scraped HTML Title Artifacts**: In the historical AJPC blacklist (rows 1214–2046), 48 records have titles derived from web-scraping artifacts (e.g., `"Home"`, `"Author: W3layouts"`, `"BiblioMed.org - Deposit for Medical Articles"`). These are documented in [`malformed_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/malformed_records.csv) and flagged for review.
5. **Deduplication Audit**:
   - 151 post-2020 candidate duplicates matching historical AJPC records were detected and segregated into [`excluded_ajpc_duplicates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/excluded_ajpc_duplicates.csv).
   - Within the post-2020 cohort, there are zero duplicate ISSN-L mappings.

---

## 5. Temporal & Credibility Triage

### Launch Date Verification (Phase 4)
Documented in [`launch_date_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/launch_date_audit.csv):
- Historical AJPC records (2,046): Pre-2021 cohort.
- Discovered post-2020 records (3,482): Confirmed launch years between 2021 and 2026 based on DOAJ `bibjson.oa_start` and OpenAlex `first_publication_year`.
- Non-journal serials (11): Excluded conference proceedings volumes (e.g., *IET conference proceedings*) triaged into [`uncertain_candidates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/uncertain_candidates.csv).

### Credibility Label Provenance (Phase 5)
Documented in [`label_provenance_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/label_provenance_audit.csv) and [`credibility_evidence_audit.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/credibility_evidence_audit.csv):
- **Inherited AJPC Labels**: 2,046 records (1,213 legitimate, 833 predatory).
- **Independently Supported New Labels**:
  - **1,621 Legitimate**: Indexed in DOAJ or published by established scholarly presses (Springer Nature, PLOS, IEEE, Cambridge University Press, etc.).
  - **179 Predatory**: Documented on predatory publisher registries or exhibiting deceptive publication practices.
- **Unlabeled / Pending Evidence**:
  - **1,682 Serials**: Discovered post-2020 serials with verifiable ISSNs but lacking certified directory indexing or blacklisting evidence. These are segregated into [`audited_uncertain_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_uncertain_records.csv) to prevent label corruption.

---

## 6. Stratified Manual Quality Control (Phase 7)
A stratified sample of 75 records across all 5 strata was audited in [`audit/reports/manual_qc_audit_sample.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/reports/manual_qc_audit_sample.csv) using random seed 42:
- **Original Whitelist (15)**: 100% identity and label agreement.
- **Original Blacklist (15)**: 100% URL agreement; 3 records noted with scraped navigation header artifacts.
- **Post-2020 Legitimate (15)**: 100% agreement with DOAJ catalogue records.
- **Post-2020 Predatory (15)**: 100% agreement with registry flags; recommended for ongoing expert verification.
- **Post-2020 Unlabeled (15)**: 100% identity confirmation as genuine post-2020 serials, confirming the necessity of keeping them unlabeled.

---

## 7. Defensible Final Datasets (Phase 8)

| Dataset Output File | Row Count | Status & Purpose |
| :--- | :---: | :--- |
| [`audited_verified_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_verified_dataset.csv) | **3,846** | **Primary Defensible Evaluation Dataset**: 2,046 historical AJPC + 1,800 post-2020 verified serials (2,834 legitimate, 1,012 predatory). |
| [`audited_uncertain_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_uncertain_records.csv) | **1,682** | **Unlabeled Pool**: Genuine post-2020 journals pending secondary credibility audit. |
| [`audited_excluded_records.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_excluded_records.csv) | **162** | **Excluded Candidates**: 151 confirmed AJPC duplicates + 11 pre-2021/conference volumes. |
| [`audited_dataset_manifest.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audited_dataset_manifest.csv) | **3** | Manifest linking files, counts, and descriptions. |
