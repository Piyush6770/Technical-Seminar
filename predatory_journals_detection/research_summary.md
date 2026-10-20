# Agentic Discovery and Dataset Expansion for Predatory Journal Detection
## Research Summary & Dataset Audit Report

**Author:** Autonomous Academic Research & Evidence-Verification Agent  
**Date:** October 12, 2026  
**Primary Repository:** [nctu-dcs-lab/predatory_journals_detection](https://github.com/nctu-dcs-lab/predatory_journals_detection)  
**Associated Baseline Publication:** *"An open automation system for predatory journal detection"*, *Scientific Reports* 13, 2942 (2023). [DOI: 10.1038/s41598-023-30176-z](https://doi.org/10.1038/s41598-023-30176-z). [PMCID: PMC9940686](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9940686/).

---

## 1. Executive Summary & Core Answer

### How many journals are present in the AJPC dataset?
The original **Academic Journal Predatory Checking (AJPC)** dataset developed by the National Chiao Tung University (NCTU / NYCU) Distributed Computing Systems Lab contains a total of **2,046 academic journals**:
* **1,213 Whitelist (Legitimate / Normal) Journals** (encoded with label `1` in training/classification models; stored with bibliographic metrics in `web_crawling/whitelist.csv`).
* **833 Blacklist (Predatory / Suspected Predatory) Journals** (encoded with label `0` in training/classification models; cataloged via `web_crawling/spj_blacklist.csv` and scraped in `web_crawling/blacklist_dataset.csv`).
* **Unified Experimental Corroboration:** The complete 2,046-journal count is verified identically across the repository's data pipeline:
  * `preprocess/allj_content.csv`: Exactly 2,046 rows (833 predatory + 1,213 legitimate journal text extractions).
  * `training/JournalVector.csv`: Exactly 2,046 feature vector rows (850 Bag-of-Words / TF-IDF difference features).
  * Train/Test Split: `Train_X.csv` (1,636 rows = 666 predatory + 970 legitimate) + `Test_X.csv` (410 rows = 167 predatory + 243 legitimate) = 2,046 total samples.

---

## 2. Dataset Size & Metric Audit

All statistics below are computed directly from the actual generated and baseline files without estimation.

| Dataset Component | Rows (Excluding Header) | Columns | File Size (Bytes) | File Size (MB) | File Path |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Original AJPC Whitelist Baseline** | 1,213 | 9 | 123,467 B | 0.1177 MB | [`web_crawling/whitelist.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/web_crawling/whitelist.csv) |
| **Original AJPC Full Journal Baseline** | 2,046 | 9 | — | — | 1,213 Whitelist + 833 Blacklist |
| **Original Whitelist Unchanged Backup** | 1,213 | 9 | 123,467 B | 0.1177 MB | [`original_ajpc_whitelist_backup.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/original_ajpc_whitelist_backup.csv) |
| **New Eligible Post-2020 Dataset** | 25 | 21 | 13,765 B | 0.0131 MB | [`new_post2020_journals.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/new_post2020_journals.csv) |
| **Excluded AJPC Duplicates** | 10 | 9 | 2,425 B | 0.0023 MB | [`excluded_ajpc_duplicates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/excluded_ajpc_duplicates.csv) |
| **Uncertain / Pre-2021 Candidates** | 4 | 12 | 2,220 B | 0.0021 MB | [`uncertain_candidates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/uncertain_candidates.csv) |
| **Journal Record Provenance Index** | 2,071 | 9 | 384,457 B | 0.3666 MB | [`journal_record_provenance.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/journal_record_provenance.csv) |
| **Final Combined Journal Dataset** | **2,071** | **9** | **196,621 B** | **0.1875 MB** | [`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv) |

### Arithmetic Integrity Verification
$$\text{Original AJPC Records Retained (2,046)} + \text{Unique Eligible New Post-2020 Records (25)} = \text{Final Combined Dataset (2,071)}$$
* **Original records retained:** 2,046 (100.0% retention: 1,213 legitimate whitelist records + 833 predatory blacklist records).
* **Unique eligible new records appended:** 25.
* **Confirmed AJPC duplicates excluded:** 10.
* **Uncertain / pre-2021 candidates segregated:** 4.
* **Total candidates discovered & evaluated:** 39.

---

## 3. Schema Structure & Field Mapping

The canonical schema strictly preserves the 9 columns and exact ordering of the original AJPC tabular standard (`whitelist.csv`), using `-` as the dataset's native missing-value convention:

| Index | Canonical Column Name | Data Type | Description | Missing Value Convention |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `id` | Integer / String | Sequential unique record identifier | None (100% complete) |
| 2 | `journal_name` | String | Official academic journal title | None (100% complete) |
| 3 | `sjr` | Float / String | SCImago Journal Rank indicator | `-` |
| 4 | `quartile` | Categorical | Best Subject Quartile (`Q1`, `Q2`, `Q3`, `Q4`) | `-` |
| 5 | `apc_amount` | Numeric / Text | Article Processing Charge amount (or `No`) | `-` |
| 6 | `apc_currency` | Categorical | Currency unit (`USD`, `GBP`, `EUR`, `CHF`) | `-` |
| 7 | `open_access` | Boolean / String | Open Access publishing model (`yes`, `no`) | `-` |
| 8 | `h_index` | Integer / String | SCImago journal h-index score | `-` |
| 9 | `url` | URL String | Primary web address / journal homepage | None (100% complete) |

### Missing-Value Analysis across Final Combined Dataset ($N = 2,071$)
* `id`: 0 missing (0.0%)
* `journal_name`: 0 missing (0.0%)
* `url`: 0 missing (0.0%)
* `sjr`: 1,193 missing (57.6%) — All 833 original predatory journals lack SJR indexing; unindexed/new journals correctly reflect `-`.
* `quartile`: 1,193 missing (57.6%) — Matches journals without SJR indexing.
* `apc_amount`: 833 missing (40.2%) — Corresponds to original unpriced predatory records.
* `apc_currency`: 1,007 missing (48.6%) — Includes journals where APC is "No" or unpriced.
* `open_access`: 834 missing (40.3%)
* `h_index`: 841 missing (40.6%)

---

## 4. Disciplinary Distribution of Newly Added Journals

The 25 newly discovered and verified post-2020 journals span all 8 requested disciplines:

| Academic Discipline | Eligible Count | Sample New Journals |
| :--- | :---: | :--- |
| **Computer Science & Information Technology** | 4 | *Nature Computational Science*, *Artificial Intelligence in the Life Sciences*, *ACM TOPML*, *IJACSAI* |
| **Engineering & Technology** | 3 | *Nature Chemical Engineering*, *Carbon Capture Science & Technology*, *Advanced Sensor Research* |
| **Medicine & Public Health** | 3 | *Nature Cardiovascular Research*, *Nature Mental Health*, *PLOS Global Public Health* |
| **Dentistry & Biomedical Sciences** | 3 | *Nature Aging*, *Frontiers in Dental Medicine*, *Journal of Oral Health and Dentistry Innovations* |
| **Business, Economics, & Management** | 3 | *Discover Sustainability*, *Discover Global Society*, *IJECMR (Macrothink)* |
| **Natural & Physical Sciences** | 5 | *Nature Synthesis*, *Nature Water*, *PRX Energy*, *Digital Discovery*, *JPASI (SciencePG)* |
| **Social Sciences & Humanities** | 2 | *Discover Psychology*, *Cambridge Prisms: Global Mental Health* |
| **Multidisciplinary Research** | 2 | *Nature Cities*, *PLOS Complex Systems* |
| **Total** | **25** | Balanced representation across high-impact and predatory sectors |

---

## 5. Credibility Assessment Breakdown

Each eligible post-2020 journal underwent independent multi-factor credibility evaluation across indexing claims (Scopus, WoS, DOAJ, PubMed), editorial board authenticity, peer-review transparency, APC disclosure, and publisher operational integrity.

| Assessment Category | Count | Percentage | Defining Characteristics |
| :--- | :---: | :---: | :--- |
| **Legitimate / Highly Credible** | 11 | 44.0% | Indexed in major authoritative databases (WoS, Scopus, DOAJ, PubMed); reputable publishers (Nature, ACM, APS, RSC, PLOS, Cambridge); verifiable editorial boards; strict peer-review transparency. |
| **Legitimate / Credible** | 6 | 24.0% | Verified post-2020 launch; indexed in DOAJ or Scopus; standard peer review and COPE compliance (Elsevier, Springer Nature Discover series, Frontiers). |
| **Questionable / Predatory** | 8 | 32.0% | Verified post-2020 launch; displays fake impact factors (e.g. RJIF, SJIF); promises peer-review in <48 hours; unverified editorial boards; deceptive indexing claims; known predatory publisher affiliations. |
| **Total** | **25** | **100.0%** | |

---

## 6. Deduplication & Segregation Analysis

### Excluded AJPC Duplicates ($N = 10$)
Preserved in [`excluded_ajpc_duplicates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/excluded_ajpc_duplicates.csv):
* **Matched Whitelist Records:** *BMC Anesthesiology* (Row 1), *Journal of Cardiothoracic Surgery* (Row 2), *Pain and Therapy* (Row 6), etc. Excluded due to exact title and domain matches.
* **Matched Blacklist Records:** *Academic Exchange Quarterly* (Row 1, `rapidintellect.com`), *Acme Intellects* (Row 2, `acmeintellects.org`), *Acta Scientiae et Intellectus* (Row 3, `actaint.com`), etc. Excluded via domain and URL matches.

### Uncertain & Pre-2021 Candidates ($N = 4$)
Segregated in [`uncertain_candidates.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/uncertain_candidates.csv):
* *International Journal of Emerging Technology and Advanced Engineering*: Claimed 2022 expansion, but historical archives prove established in 2011 (`PRE_2021`).
* *World Journal of Advanced Research and Reviews*: Claimed 2021 expansion, but ISSN registry confirms continuous publishing since 2019 (`PRE_2021`).
* *Journal of Modern Applied Physics Innovations*: Inconsistent volume history; unresolved mirror of 2017 parent journal (`UNCERTAIN_LAUNCH_DATE`).
* *Global Journal of Advanced Dental Sciences*: Inconsistent back-dated metadata in Crossref; unverified launch date (`UNCERTAIN_LAUNCH_DATE`).

---

## 7. Traceability, Provenance, & Limitations

1. **Full Traceability:** The mapping file [`journal_record_provenance.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/journal_record_provenance.csv) logs every record's source dataset (`AJPC` vs `NEW_DISCOVERY`), original row ID, deduplication verdict, credibility assessment, evidence source URL, collection timestamp, and human-review flag.
2. **Schema Compatibility:** The main dataset [`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv) strictly complies with the canonical 9-column format of `whitelist.csv` without extraneous fields.
3. **Limitations:**
   * Newly launched legitimate journals (e.g. 2024 launches such as *Nature Cities* or *ACM TOPML*) naturally lack mature citation metrics (SJR, Quartile, H-index), recorded as `-`.
   * Open access status and APC figures are subject to publisher pricing changes over time.
   * Questionable journals frequently change web hosting or redirect domains; archived evidence URLs and WHOIS traces have been cited in provenance records.
