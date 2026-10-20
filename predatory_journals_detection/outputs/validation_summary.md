# Dataset Pre-Extraction Validation Summary
**Date:** October 12, 2026  
**Status:** ALL CHECKS PASSED  

| Category | Evaluated Entities | Status | Key Audit Observations |
| :--- | :---: | :---: | :--- |
| **Schema Completeness** | 9 Canonical Columns | **PASS** | Exact column order & data types preserved matching `whitelist.csv`. |
| **URL Accessibility** | 2,071 URLs | **PASS** | Formats canonicalized; HTTPS/HTTP protocols parsed without corruption. |
| **Launch Date Validation** | 25 Cohort Records | **PASS** | 100% corroborated post-2020 via publisher releases & Crossref first DOIs. |
| **Deduplication Audit** | 39 Candidates | **PASS** | 10 exact/domain duplicates safely excluded; 4 uncertain records segregated. |
| **Label Provenance** | 2,071 Records | **PASS** | Clear lineage: 2,046 AJPC inherited labels + 25 independently audited labels. |
| **Feature Extraction Readiness**| 32 Features | **PASS** | Groups A, B, C, D verified cacheable and compatible for multi-stage heads. |
