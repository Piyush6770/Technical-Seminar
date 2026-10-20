# Project Analysis and Technical Audit Report

**System Title**: *Progressive Cost-Aware Feature Acquisition & Temporal Shift Auditing for Predatory Journal Forensics*  
**Repository Working Directory**: `c:\Users\Pratik\Engineering\3rd Year\TS`  
**Auditor**: Senior Research Paper Author & Technical Research Investigator  
**Audit Timestamp**: October 2026  
**Primary Dataset Cryptographic Hash**: `SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328`

---

## 1. Executive Summary of Inspected Codebase

The inspected workspace contains an end-to-end, production-grade research system designed to detect deceptive, fraudulent, and predatory academic journals. Unlike conventional static classification systems reported in the scientific literature, this project specifically tackles:
1. **Longitudinal Temporal Distribution Shift**: Quantified performance degradation on post-2020 serials when trained on historical (pre-2021) publishing patterns.
2. **Cost-Aware Progressive Feature Acquisition**: Dynamically minimizing high-latency web rendering and external registry API overhead using sequential decision-theoretic stopping.
3. **Evidence-Grounded Explanations & Selective Abstention**: Corroborating public website claims against authoritative bibliometric registries with explicit human-in-the-loop abstention on ambiguous records.

The codebase is written in Python (3.10–3.14 compatible) and is organized cleanly across modular packages for feature extraction, representation learning, calibration, evaluation, explainability, and user interaction.

---

## 2. Directory Structure and Component Inventory

```
c:\Users\Pratik\Engineering\3rd Year\TS
├── artifacts/
│   ├── models/
│   │   ├── progressive_multi_head.pt          # PyTorch shared neural weights (weights_only=True safe)
│   │   ├── progressive_multi_head_scalers.joblib # Decoupled scikit-learn standard scalers
│   │   ├── stopping_controller_params.json   # Calibrated thresholds (tau1=0.80, tau2=0.80, tau3=0.75, lambda=16.0)
│   │   ├── rf_stage1..4.joblib               # Decoupled Random Forest baselines
│   │   └── xgb_stage1..4.joblib              # Decoupled XGBoost baselines
│   └── reports/
│       ├── benchmark_results.json            # Machine-readable quantitative outputs across E1–E6
│       └── benchmark_report.md               # Markdown summary of empirical benchmarks
├── audit/
│   ├── data/
│   │   └── final_combined_journal_dataset_frozen_readonly.csv # 5,528 records (SHA-256 verified)
│   └── splits/
│       ├── historical_train.csv              # 1,636 records (970 legit, 666 pred)
│       ├── historical_val.csv                # 410 records (243 legit, 167 pred)
│       ├── temporal_test_cohort_untouched.csv # 1,800 records (1,621 legit, 179 pred)
│       ├── audited_uncertain_records.csv     # 1,682 quarantined records (unlabeled)
│       └── evaluation_splits_manifest.csv    # Manifest detailing split statistics
├── data_cache/
│   └── feature_cache.sqlite                  # SQLite disk cache for accelerated feature re-use
├── paper/
│   ├── manuscript.tex                        # Full two-column IEEEtran LaTeX paper
│   ├── manuscript.md                         # Matching GitHub-flavored Markdown paper
│   ├── references.bib                        # 29 verified scholarly citations
│   └── figures/                              # Publication-grade vector PDF and high-res PNG plots
├── src/
│   ├── config.py                             # Paths, stage cost parameters, and hyperparameter constants
│   ├── features/
│   │   ├── cache.py                          # SQLite-backed feature caching layer
│   │   ├── group_a_url.py                    # Group A: 16 URL & domain geometry features (<0.01s)
│   │   ├── group_b_html.py                   # Group B: 13 static HTML & editorial policy features (~0.8s)
│   │   ├── group_c_dynamic.py                # Group C: 6 dynamic JS & client behavior features (~3.5s)
│   │   ├── group_d_scholarly.py              # Group D: 7 registry corroboration features (~5.0s)
│   │   └── pipeline.py                       # Unified progressive feature extraction orchestrator
│   ├── models/
│   │   ├── multi_head_model.py               # Progressive shared neural representation network
│   │   ├── stopping_controller.py            # Cost-aware stopping policy and Pareto optimization
│   │   ├── calibration.py                    # Platt scaling & 10-bin ECE reliability estimation
│   │   └── baselines.py                      # Tabular ensemble baselines (RF & XGBoost)
│   ├── evaluation/
│   │   └── run_benchmarks.py                 # Automated benchmark test suite (Experiments E1–E6)
│   ├── explainability/
│   │   ├── evidence_grounding.py             # Deterministic fact verification & contradiction engine
│   │   └── diagnostic_report.py              # Section 6 structured JSON diagnostic emitter
│   └── ui/
│       └── app.py                            # Streamlit diagnostic web dashboard
├── tests/
│   ├── test_features.py                      # Feature extraction unit tests
│   ├── test_models.py                        # Model inference and calibration tests
│   └── test_stopping.py                      # Stopping controller and threshold tests
├── prompt.md                                 # Master research prompt & scientific specification
└── requirements.txt                          # Python package dependencies
```

---

## 3. Dataset Architecture & Verification

The project enforces a strict, defensible dataset partitioning protocol based on an audited inventory of **5,528 serial records** (`final_combined_journal_dataset.csv`), frozen with cryptographic integrity:
- **Baseline Historical Benchmark ($N=2,046$)**: Originating from the NCTU DCS Lab / Beall historical indexing (pre-2021). Exactly split into:
  - `HISTORICAL_TRAIN`: $1,636$ records ($970$ legitimate, $666$ predatory).
  - `HISTORICAL_VAL`: $410$ records ($243$ legitimate, $167$ predatory).
- **Post-2020 Inaugural Cohorts ($N=3,482$)**: Serials confirmed to have commenced publication between 2021 and 2026.
  - `TEMPORAL_TEST_UNTOUCHED`: $1,800$ records ($1,621$ legitimate, $179$ predatory). Strictly held out—never accessed during scaling, training, or threshold tuning.
  - `QUARANTINED_UNLABELED`: $1,682$ serials lacking definitive ground truth; quarantined to prevent label noise.

---

## 4. Technical Architecture & Methodology

### 4.1 Four-Stage Progressive Feature Hierarchy
The system extracts 42 total features categorized into four sequential groups:
1. **Group A (URL & Domain Geometry; $d=16$; Latency $<0.01$s)**:
   - Evaluates URL length, domain length, path depth, dot/hyphen counts, digit ratios, symbol ratios, Shannon entropy, HTTPS flag, academic/suspicious TLD classification, and IP address presence.
2. **Group B (Static HTML & Editorial Policies; $d=13$; Latency $\approx 0.8$s)**:
   - Evaluates HTTP response latency, DOM depth, presence and link depth of editorial board pages (`/editorial-board`, `/editors`), peer-review accessibility, APC transparency, APC numerical amounts, COPE declaration, contact email domain matching (institutional vs generic freemail like Gmail/Yahoo), copyright freshness, and text-to-HTML ratio.
3. **Group C (Dynamic JavaScript & Client Behavior; $d=6$; Latency $\approx 3.5$s)**:
   - Evaluates script tag density, third-party vs. first-party script domain ratio, intrusive ad/cryptominer presence, word count disparity between raw HTML and rendered DOM, automated redirects, and client-side obfuscation.
4. **Group D (Scholarly Registries & Provenance; $d=7$; Latency $\approx 5.0$s)**:
   - Evaluates ISSN Portal validity, Crossref DOI prefix deposit existence, publication volume variance, citation metrics, DOAJ indexing confirmation, Scopus/Web of Science claims verification, and editorial board institutional identity match score.

### 4.2 Progressive Shared Multi-Head Neural Architecture
Instead of four disconnected classifiers, the system implements a shared neural representation network:
$$\phi_1(x_A) = \sigma(\text{LN}(W_1 x_A + b_1))$$
$$\phi_k(\phi_{k-1}, x_k) = \sigma(\text{LN}(W_k [\phi_{k-1}; x_k] + b_k)), \quad k \in \{2, 3, 4\}$$
Each stage representation feeds into a specialized classification head $\hat{y}_k = f_{\text{head}_k}(\phi_k)$. Representation sharing regularizes early heads and prevents catastrophic collapse under temporal shift.

### 4.3 Adaptive Stopping Controller & Cost-Aware Decision Policy
Inference is governed by an adaptive stopping controller evaluated after stages 1, 2, and 3:
$$\text{Stop if } c_k \ge \tau_k \quad \text{AND} \quad \Delta_{\text{cost}}(k \to k+1) > \lambda \cdot (1 - c_k)$$
where $c_k = \max(\hat{p}_k, 1 - \hat{p}_k)$ is the Platt-calibrated posterior confidence, $\Delta_{\text{cost}}$ represents latency penalty, and $\tau = (0.80, 0.80, 0.75), \lambda = 16.0$ are optimized on validation data.

### 4.4 Deterministic Provenance Grounding & Selective Abstention
Statistical risk predictions are cross-checked against authoritative registries. If:
- Calibrated risk $\hat{p} \in [0.40, 0.60]$, or
- Registry facts contradict public website claims (e.g., claiming COPE or DOAJ without registration),
the system abstains with `abstention_status: "REQUIRES_HUMAN_EXPERT_REVIEW"`.

---

## 5. Summary of Verified Experimental Findings

| Experiment | Measured Finding |
| :--- | :--- |
| **E1 (Group A Only)** | Macro-$F_1 = 0.4842$, ROC-AUC = $0.5721$, Latency = $10.0$ ms. High false-positive rate ($56.7\%$). |
| **E2 (Full Acquisition)** | Macro-$F_1 = 0.4560$, ROC-AUC = $0.6326$, Latency = $9,310.0$ ms. Lower $F_1$ due to noisy downstream signals on evasive serials. |
| **E3 (Adaptive Progressive)** | **Macro-$F_1 = 0.5327$, ROC-AUC = $0.6771$, Latency = $519.0$ ms.** Resolves $36.3\%$ at Stage 1 and $63.7\%$ at Stage 2. Achieves **94.4% latency reduction** while improving accuracy over E2. |
| **E4 (Fixed Stage Ablation)** | Fixed Stage 1 ($0.4842$) $\to$ Stage 2 ($0.4907$) $\to$ Stage 3 ($0.4804$) $\to$ Stage 4 ($0.4560$). Dynamic stopping ($0.5327$) outperforms all fixed exit points. |
| **E5 (Model Comparisons)** | Random Forest ($F_1 = 0.1388$) and XGBoost ($F_1 = 0.0904$) collapse under temporal shift, while the shared neural representation preserves balanced discriminative power. |
| **E6 (Temporal Shift)** | Macro-$F_1$ drops from $0.9949$ on historical validation to $0.5327$ on temporal test (Generalization Ratio = $0.5354$), while Brier error inflates $58\times$. Proves the static cross-validation fallacy. |

---

## 6. Distinguishing Verified Functionality from Future Extensions

### Implemented & Verified
- Modular, cached progressive feature extraction pipeline (Groups A, B, C, D) with offline fallback.
- Shared progressive multi-head neural network with decoupled PyTorch 2.6+ state dict and joblib scalers.
- Calibrated adaptive stopping controller with cost-error trade-off.
- Six formal benchmarks (E1–E6) executed with full quantitative metrics logged to JSON.
- Deterministic evidence grounding and selective abstention schema.
- Interactive Streamlit application with minimal, institutional UI.
- Comprehensive unit test suite (13 passing tests).

### Limitations & Scope Boundaries
- **Registry Ingestion Lag**: Authoritative registries require 6–12 months to index new legitimate serials.
- **Dynamic JS Sandbox Overhead**: Stage 3 headless browser requires dedicated compute sandboxes.
- **Language Bias**: Heuristics are optimized primarily for English-language journal interfaces.
