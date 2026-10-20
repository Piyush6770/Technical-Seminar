# Audit of the Original AJPC Dataset
**Investigator:** Autonomous Research & Integrity Engineering Agent  
**Date:** October 12, 2026  
**Repository:** [nctu-dcs-lab/predatory_journals_detection](https://github.com/nctu-dcs-lab/predatory_journals_detection)  
**Associated Scientific Publication:** *"An open automation system for predatory journal detection"*, *Scientific Reports* 13, 2942 (2023). [PMCID: PMC9940686](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9940686/).

---

## 1. Executive Summary & Reconciliation of Working Figures

### Investigation of the Provisional "2,700 Total Records / 1,867 Remaining" Figure
The project specification supplied a provisional working hypothesis:
* *Provisional figure:* Total records = 2,700, Predatory records = 833, Remaining records = 1,867.

**Empirical Audit Finding:**
Upon exhaustive programmatic inspection of all files in the repository:
1. **The actual physical AJPC experimental dataset contains exactly 2,046 journal records**, not 2,700.
2. **Breakdown of the 2,046 records:**
   * **833 Blacklist (Predatory) Records:** Exactly 833 URLs cataloged in `web_crawling/spj_blacklist.csv` and scraped in `web_crawling/blacklist_dataset.csv`.
   * **1,213 Whitelist (Legitimate) Records:** Exactly 1,213 structured rows in `web_crawling/whitelist.csv` and scraped in `web_crawling/whitelist_dataset.csv`.
   * Total sum: $833 + 1,213 = 2,046$.
3. **Corroborating Downstream Artifacts in the Repository:**
   * `preprocess/allj_content.csv`: Exactly 2,046 rows (first 833 predatory, next 1,213 legitimate).
   * `training/JournalVector.csv`: Exactly 2,046 rows (850 Bag-of-Words / TF-IDF difference features).
   * `training/Train_X.csv` + `training/Test_X.csv`: $1,636 + 410 = 2,046$ feature vectors (80/20 train/test split).
   * `training/Train_Y.csv` + `training/Test_Y.csv`: $1,636 + 410 = 2,046$ binary target labels.
     * Predatory (class `0`): 666 (train) + 167 (test) = 833.
     * Legitimate (class `1`): 970 (train) + 243 (test) = 1,213.
4. **Origin of the 2,700 / 1,867 Discrepancy:**
   * The number 2,700 appears to have been an external estimate derived from combining 833 predatory journals with an unverified estimate of ~1,867 whitelisted records before file inspection.
   * In reality, the authors of the NCTU DCS Lab paper selected **1,213 whitelisted journals** from SCImago/DOAJ, resulting in a 2,046-journal corpus.
   * There are no missing or "unlabeled 1,867" journals in the repository; all 1,213 whitelist journals are explicitly labeled `1` (Normal Journal), and all 833 blacklist journals are explicitly labeled `0` (Suspected Predatory Journal).

---

## 2. Cryptographic Hashes & File Manifest

All baseline files have been verified and sealed with cryptographic SHA-256 hashes:

| File Path | Role in AJPC | Exact Size (Bytes) | SHA-256 Cryptographic Hash |
| :--- | :--- | :---: | :--- |
| `web_crawling/whitelist.csv` | Whitelist metadata table (1,213 rows) | 123,467 B | `c94d828fc0ff6d8f81c68ec6282902344ba9c6b5d3fc050d64bc698b5ea9c15b` |
| `web_crawling/spj_blacklist.csv` | Predatory journal URLs (833 URLs) | 23,167 B | `59283fe0fffb4dcb87c6cc9cc6fb2febc16ee358c34b578d0af25bdfce56dc7c` |
| `web_crawling/blacklist_dataset.csv` | Scraped predatory homepage text (833 rows) | 5,363,744 B | `d98efc70a2186d47cf188ae43535764680cc07827e524e55704a3b5b5e947e94` |
| `preprocess/allj_content.csv` | Tokenized content for all 2,046 journals | 15,919,247 B | `3b27b3f93556380e2dcd076eac2aa2f36682f326fcfb1ce173f6822027c63ff8` |
| `training/JournalVector.csv` | 850-d feature vectors for 2,046 journals | 6,958,446 B | `f7efd66311ce99bbe06cf7067a3c21a85f1322222d2f9f23d1c2204cc43063bb` |
| `training/Train_Y.csv` | Ground-truth labels for training split (1,636 labels) | 3,273 B | `398cd6e9c0252aa58edf70894a84ea6a468cda5e12dcd9d460b18a06099c04b0` |
| `training/Test_Y.csv` | Ground-truth labels for testing split (410 labels) | 821 B | `44a35ece8f2551dc009da33ab4ce69aaf8af5cf968a9fdcd5d3f21df745be412` |

---

## 3. Detailed Schema, Field Types, & Missing-Value Statistics

The canonical structured metadata in `web_crawling/whitelist.csv` contains 9 columns without a header row:

1. `id` (Integer string): 1 to 1213. 0 missing (0.0%).
2. `journal_name` (String): Journal title. 0 missing (0.0%).
3. `sjr` (Float string): SCImago Journal Rank indicator. 360 missing (`-`, 29.7%).
4. `quartile` (String): Best Quartile (`Q1`, `Q2`, `Q3`, `Q4`). 360 missing (`-`, 29.7%).
5. `apc_amount` (Numeric string / `No`): APC charge. 0 missing in whitelist (100% complete).
6. `apc_currency` (String): `GBP`, `USD`, `EUR`, `CHF`, or `-`. 174 missing (`-`, 14.3%).
7. `open_access` (String): `yes` or `no`. 0 missing (100% complete).
8. `h_index` (Integer string): SCImago h-index. 8 missing (`-`, 0.7%).
9. `url` (String): Journal homepage URL. 0 missing (100% complete).

---

## 4. Class Balance & Partition Summary

```
Total Ground-Truth Samples: 2,046
├── Predatory Class (0): 833 (40.71%)
│   ├── Train split: 666
│   └── Test split:  167
└── Legitimate Class (1): 1,213 (59.29%)
    ├── Train split: 970
    └── Test split:  243
```
Ratio: ~1 : 1.45 (Predatory to Legitimate).
