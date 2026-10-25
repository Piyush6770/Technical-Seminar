# Cost-Aware Progressive Predatory Journal Detection

[![IEEE Paper](https://img.shields.io/badge/IEEE%20Paper-7%20Pages%20Camera%20Ready-blue.svg)](research_paper/research_paper.pdf)
[![Seminar Report](https://img.shields.io/badge/PCCOE%20Report-30--40%20Pages%20Verified-darkgreen.svg)](reports/Technical_Seminar_Report.docx)
[![Literature Survey](https://img.shields.io/badge/Literature%20Survey-20%20Papers%20Excel-orange.svg)](reports/Literature_Survey.xlsx)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.2-red.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal.svg)](src/api_server.py)
[![React](https://img.shields.io/badge/React-19.3.1%20Vite-61DAFB.svg)](frontend/)
[![Dataset](https://img.shields.io/badge/Audited%20Corpus-5%2C528%20Serials-orange.svg)](audit/splits/)
[![SHA-256](https://img.shields.io/badge/SHA--256-d775c92c...-blueviolet.svg)](audit/data/)

---

## 1. Executive Summary & Project Purpose

### What Is This Project?
This project is an end-to-end, production-grade scientific forensic framework and research publication system engineered to detect fraudulent, deceptive, and predatory academic journals. It resolves the core vulnerabilities of automated predatory publishing inspection by unifying:
1. **Cost-Aware Progressive Feature Acquisition** (4-stage latency-bounded hierarchy),
2. **Out-of-Distribution Temporal Generalization** (benchmarking across pre-2021 historical and 2021–2026 contemporary cohorts),
3. **Calibrated Neural Early Stopping** (stopping inference when calibrated posterior confidence satisfies a Pareto cost-error threshold), and
4. **Deterministic Registry Provenance Grounding** (verifying claims directly against Crossref, DOAJ, OpenAlex, and official ISSN portals with tri-state selective triage).

### Academic & Institutional Affiliation
- **Institution**: Department of Computer Engineering, Pimpri Chinchwad College of Engineering (PCCOE), Pune, India
- **Group ID**: GB11
- **Guide**: Prof. Dr. Swati V. Shinde
- **Authors / Team**:
  - Pratik Jadhav (`pratik.jadhav24@pccoepune.org`)
  - Suyog Jadhav (`suyog.jadhav24@pccoepune.org`)
  - Piyush Patel (`piyush.patel24@pccoepune.org`)
  - Parshwa Nikam (`parshwa.nikam24@pccoepune.org`)

---

## 2. The Three Structural Failure Modes in Existing Literature

Prior automated predatory journal detection systems (such as the Academic Journal Predatory Checking — AJPC system [7]) reported classification accuracies exceeding 95% on static benchmarks. However, independent forensic audits by Teixeira da Silva (2025) [8] revealed that these systems fail catastrophically in operational deployment due to three structural flaws:

1. **The Static In-Distribution Fallacy**: Models evaluated solely with $i.i.d.$ cross-validation on static historical data (pre-2020 crawls) collapse when deployed on contemporary serials. Predatory publishers adapt dynamically: adopting modern Open Journal Systems (OJS) platforms, commercial-sounding academic domains, real scholar names on fabricated editorial boards, and formal APC schedules. Our empirical findings prove a severe longitudinal collapse: performance drops from $F_1 = 0.9949$ (historical validation) to $F_1 = 0.5327$ (temporal test), establishing an empirical **Temporal Generalization Ratio of 0.5354**.
2. **The Uniform Acquisition Cost & Server Crash Fallacy**: Prior frameworks assume every environmental signal is available with zero latency. In reality, local URL geometry takes $<10$ ms, whereas headless browser DOM rendering takes $3$ to $5$ seconds, and querying external scholarly APIs requires multiple network hops ($9,310$ ms total). Synchronous exhaustive scraping exhausts system resources, causing central server crashes and prolonged downtimes [8].
3. **The Ungrounded Black-Box Score Fallacy**: Prior models emit raw, uncalibrated scalar probabilities without factual provenance, causing erratic classification flips across internal journal pages [8]. In academic tenure reviews and legal disputes, opaque scores carry no legal standing. Our framework introduces **deterministic evidence grounding** and **tri-state selective triage** ($0.40 \le \hat{p} \le 0.60$), withholding autonomous verdicts on ambiguous serials and routing them to human expert librarians.

---

## 3. Four-Stage Progressive Acquisition Hierarchy (42 Features)

Features are partitioned into four modular, progressively evaluated stages with persistent disk caching:

```
                          [Query Input: Journal URL, Title, ISSN, Publisher]
                                                  │
                                                  ▼
                    ┌────────────────────────────────────────────────────────────┐
                    │ Stage 1: Group A — URL & Domain Geometry (Latency < 0.01s) │
                    │ (Domain entropy, suspicious TLDs, IP patterns, depth, etc.)│
                    └────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                                     [Adaptive Stopping Controller]
                                    /                              \
                       (Confidence c_1 ≥ 0.80)             (Uncertain c_1 < 0.80)
                                  /                                  \
                                 ▼                                    ▼
                         [Early Exit 1]           ┌──────────────────────────────────────────────┐
                       (36.3% of serials)         │ Stage 2: Group B — HTML Policies (~ 0.8s)    │
                                                  │ (APC disclosure, review policies, emails)    │
                                                  └──────────────────────────────────────────────┘
                                                                      │
                                                                      ▼
                                                         [Adaptive Stopping Controller]
                                                        /                              \
                                           (Confidence c_2 ≥ 0.80)             (Uncertain c_2 < 0.80)
                                                      /                                  \
                                                     ▼                                    ▼
                                             [Early Exit 2]           ┌──────────────────────────────────────────────┐
                                           (63.7% of serials)         │ Stage 3: Group C — Dynamic JS (~ 3.5s)       │
                                                                      │ (DOM delta, obfuscated JS, crypto trackers)  │
                                                                      └──────────────────────────────────────────────┘
                                                                                          │
                                                                                          ▼
                                                                      ┌──────────────────────────────────────────────┐
                                                                      │ Stage 4: Group D — Registries (~ 5.0s)       │
                                                                      │ (Crossref, OpenAlex, DOAJ, ISSN Portal)      │
                                                                      └──────────────────────────────────────────────┘
                                                                                          │
                                                                                          ▼
                                                                              [Tri-State Triage & Grounding]
                                                                             /              |               \
                                                                            /               |                \
                                                                           ▼                ▼                 ▼
                                                                    Verified Whitelist   Selective Human     Predatory Warning
                                                                       (p̂ ≤ 0.40)       Audit (0.40–0.60)       (p̂ ≥ 0.60)
```

| Stage | Feature Group | Dim | Latency Bound | Core Signals Extracted | Adversarial Evasion Resistance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | **Group A: URL Geometry** (`src/features/group_a_url.py`) | 16 | **< 10 ms** | Shannon entropy, suspicious TLDs (`.xyz`, `.top`, `.info`), numeric/symbol ratios, path depth, subdomain token count, IPv4 netloc patterns. | Low (Adversary can buy cheap `.com` or `.org` domains). |
| **Stage 2** | **Group B: HTML Policies** (`src/features/group_b_html.py`) | 13 | **≈ 0.8 s** | APC fee transparency, perfunctory review promises (<48h), editorial board link depth, COPE declarations, institutional vs freemail (`@gmail.com`) contacts, copyright freshness. | Moderate (Adversary can copy policy text from legitimate journals). |
| **Stage 3** | **Group C: Dynamic JS** (`src/features/group_c_dynamic.py`) | 6 | **≈ 3.5 s** | Headless browser DOM render delta, script tag counts, third-party script ratios, cloaked redirects, obfuscated JS signatures, ad/crypto miner trackers. | High (Headless browser execution unmasks dynamic client-side cloaking). |
| **Stage 4** | **Group D: Scholarly Registries** (`src/features/group_d_scholarly.py`) | 7 | **≈ 5.0 s** | Official ISSN Portal verification, Crossref active DOI deposit prefix, DOAJ seal verification, Scopus/WoS claims verification score, annual publication velocity variance. | Near-Absolute (Independent third-party authoritative verification). |

---

## 4. Key Scientific Innovations

### 1. Shared Progressive Representation Learning
Rather than training independent stage classifiers, we design a shared progressive neural network in PyTorch (`src/models/multi_head_model.py`). The model maintains an internal hidden state $\mathbf{h}_k$ that accumulates representations across stages:
$$\mathbf{h}_1 = \text{ReLU}(\mathbf{W}_1 \mathbf{x}_1 + \mathbf{b}_1)$$
$$\mathbf{h}_k = \text{ReLU}(\mathbf{W}_k [\mathbf{h}_{k-1}; \mathbf{x}_k] + \mathbf{b}_k) \quad \text{for } k \in \{2, 3, 4\}$$
All hidden dimensions are projected to $h = 64$. A composite multi-task objective updates all heads simultaneously:
$$\mathcal{L}_{\text{total}} = \sum_{k=1}^4 \alpha_k \mathcal{L}_{\text{CE}}(\hat{p}_k, y)$$
**Significance**: Multi-task gradient feedback forces early layers to learn generalizable representations, completely preventing the catastrophic tabular collapse suffered by standard tree models (XGBoost $F_1 = 0.0904$).

### 2. Calibrated Early Stopping & Pareto Efficiency
At each stage $k$, the stopping controller evaluates the calibrated posterior confidence:
$$c_k = \max(\hat{p}_k, 1 - \hat{p}_k)$$
Inference halts dynamically at stage $k$ once $c_k \ge \tau_k$. Optimized thresholds ($\tau_1 = 0.80, \tau_2 = 0.80, \tau_3 = 0.75$) resolve **36.3%** of serials at Stage 1 and **63.7%** at Stage 2, slashing mean inference latency by **94.4%** ($519.0$ ms vs. $9,310.0$ ms) while improving out-of-distribution generalization ($F_1 = 0.5327$ vs. $0.4560$).

### 3. Probability Calibration via Platt & Temperature Scaling
Uncalibrated neural networks emit overconfident probabilities on shifted data. We apply Platt scaling and temperature scaling (`src/models/calibration.py`), reducing Expected Calibration Error (ECE) from **0.4619** down to **0.3079**, ensuring that stopping decisions rely on statistically sound confidence.

### 4. Tri-State Classification & Selective Abstention
The system enforces a principled reject option (`src/models/stopping_controller.py`):
- $\hat{p} \ge 0.60 \implies$ **Predatory Warning** (Emitted with explicit forensic risk indicators).
- $0.40 < \hat{p} < 0.60 \implies$ **Selective Abstention** (Autonomous verdict withheld; routed to human expert librarians).
- $\hat{p} \le 0.40 \implies$ **Verified Legitimate** (Whitelisted with corroborated registry provenance).

Routing ambiguous cases to human review achieves $87.2\%$ autonomous coverage while dropping the false positive rate from $29.9\%$ down to **$13.8\%$** (and boosting Macro-$F_1$ on covered records to **$0.6420$**).

---

## 5. Audited Dataset Partitions

To ensure strict reproducibility, all experiments operate on an audited corpus of **5,528 academic serials** frozen under SHA-256 integrity digests:
- **Master Frozen File**: `audit/data/final_combined_journal_dataset_frozen_readonly.csv` (`SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328`)

| Split Name | Era | Total Records | Legitimate ($y=0$) | Predatory ($y=1$) | Primary Scientific Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`HISTORICAL_TRAIN`** | Pre-2021 | 1,636 | 982 (60.0%) | 654 (40.0%) | Model parameter fitting and representation learning |
| **`HISTORICAL_VAL`** | Pre-2021 | 410 | 245 (59.8%) | 165 (40.2%) | Hyperparameter optimization and Platt calibration |
| **`TEMPORAL_TEST_UNTOUCHED`** | **2021–2026** | **1,800** | **1,621 (90.1%)** | **179 (9.9%)** | **Strictly held-out out-of-distribution temporal evaluation** |
| **`UNCERTAIN_POOL`** | Mixed | 1,682 | 1,145 (68.1%) | 537 (31.9%) | Quarantined for manual QC audit |
| **Total Corpus** | **2012–2026** | **5,528** | **3,993 (72.2%)** | **1,535 (27.8%)** | **Complete Audited Research Corpus** |

---

## 6. Empirical Benchmark Results (E1 – E6)

All quantitative evaluations were executed on the untouched 1,800-record contemporary temporal cohort:

| Exp ID | Evaluation Configuration | Precision | Recall | Macro-$F_1$ | Predatory $F_1$ | Specificity | ROC-AUC | Mean Latency | Stage Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | Group A Only (URL Geometry) | 0.1233 | 0.4078 | 0.4842 | 0.1894 | 0.6798 | 0.5721 | **10.0 ms** | 100% at Stage 1 |
| **E2** | Monolithic Full (A+B+C+D) | 0.1463 | 0.7542 | 0.4560 | 0.2450 | 0.5139 | 0.6326 | 9,310.0 ms | 100% at Stage 4 |
| **E3** | **Adaptive Progressive (Proposed)** | **0.1724** | **0.5642** | **0.5327** | **0.2641** | **0.7008** | **0.6771** | **519.0 ms** | **36.3% S1, 63.7% S2** |
| **E4-1** | Fixed Stage 1 (Group A) | 0.1233 | 0.4078 | 0.4842 | 0.1894 | 0.6798 | 0.5721 | 10.0 ms | 100% at Stage 1 |
| **E4-2** | Fixed Stage 2 (Groups A+B) | 0.1463 | 0.7542 | 0.4560 | 0.2450 | 0.5139 | 0.6326 | 810.0 ms | 100% at Stage 2 |
| **E4-3** | Fixed Stage 3 (Groups A+B+C) | 0.1463 | 0.7542 | 0.4560 | 0.2450 | 0.5139 | 0.6326 | 4,310.0 ms | 100% at Stage 3 |
| **E4-4** | Fixed Stage 4 (Groups A+B+C+D) | 0.1463 | 0.7542 | 0.4560 | 0.2450 | 0.5139 | 0.6326 | 9,310.0 ms | 100% at Stage 4 |
| **E5-X** | Stage 4 Independent XGBoost | 0.0994 | 1.0000 | 0.0904 | 0.1809 | 0.0000 | 0.5860 | 9,310.0 ms | 100% at Stage 4 |
| **E5-R** | Stage 4 Independent Random Forest | 0.1038 | 1.0000 | 0.1388 | 0.1881 | 0.0469 | 0.5997 | 9,310.0 ms | 100% at Stage 4 |
| **E6-H** | Historical In-Distribution Val | 1.0000 | 0.9880 | 0.9949 | 0.9940 | 1.0000 | 0.9951 | 426.0 ms | In-Distribution Base |

### Key Findings:
1. **94.4% Latency Reduction**: Resolves serials in **519.0 ms** on average, eliminating 94.4% of latency compared to monolithic scraping (9,310.0 ms).
2. **Improved Generalization**: Pruning downstream uninformative signals on decisive cases improves temporal Macro-$F_1$ from 0.4560 to **0.5327**.
3. **Catastrophic Tabular Collapse Overcome**: Standard tree models collapse under temporal drift (XGBoost $F_1 = 0.0904$, Specificity = $0.0000$), whereas our shared neural model maintains balanced discriminative power.
4. **Empirically Proven Temporal Collapse**: Longitudinal drift degrades Macro-$F_1$ from $0.9949$ to $0.5327$, yielding a reproducible **Temporal Generalization Ratio of 0.5354**.

---

## 7. Project Deliverables & Repository Structure

```
├── reports/                               # College Technical Seminar Report (PCCOE Format)
│   ├── Technical_Seminar_Report.docx      # 30-40 page PCCOE Technical Seminar Report
│   ├── Literature_Survey.xlsx             # Complete 20-paper comparative survey spreadsheet
│   ├── Technical_Seminar_Report.md        # Full Markdown version for reading & review
│   └── figures/                           # Embedded report diagrams & official PCCOE logo
├── research_paper/                        # IEEE Research Paper Source & Reference Library
│   ├── research_paper.docx                # IEEE 2-column camera-ready paper (10pt, 7 pages)
│   ├── research_paper.pdf                 # Final 7-page IEEE two-column publication PDF
│   ├── research_paper.md                  # Canonical Markdown research manuscript
│   ├── Literature_Survey.xlsx             # Comprehensive 20-paper literature survey
│   ├── EVIDENCE_AND_PROOF_OF_RESULTS.md   # Mathematical proofs, CLI audits, and SHA-256 hashes
│   ├── reference_papers/                  # Complete library of 20 authentic publisher PDFs
│   └── figures/                           # 300 DPI scientific benchmark charts (Figs 1–7)
├── paper/                                 # LaTeX Manuscript & IEEE Bibliography
│   ├── manuscript.tex                     # LaTeX IEEE format source
│   ├── references.bib                     # 20 strictly sequential IEEE citations
│   └── figures/                           # Vector PDFs & PNG diagrams (Figs 1–7)
├── frontend/                              # Interactive React 19 + Vite Web Application
│   ├── src/App.jsx                        # 3-tab UI (Journal Audit, Benchmarks, Architecture)
│   ├── package.json                       # React 19 dependencies & scripts
│   └── dist/                              # Pre-built production bundle served by FastAPI
├── src/                                   # Production Python source code
│   ├── api_server.py                      # FastAPI REST backend server
│   ├── config.py                          # Global paths, thresholds, and TLD lists
│   ├── explainability/                    # Evidence grounding & diagnostic reporting
│   ├── features/                          # 4-stage progressive feature extraction
│   │   ├── group_a_url.py                 # Stage 1: URL geometry features (< 10 ms)
│   │   ├── group_b_html.py                # Stage 2: HTML policy features (~ 0.8s)
│   │   ├── group_c_dynamic.py             # Stage 3: Dynamic JS DOM features (~ 3.5s)
│   │   ├── group_d_scholarly.py           # Stage 4: External registry features (~ 5.0s)
│   │   └── pipeline.py                    # Unified sequential feature pipeline
│   ├── models/                            # PyTorch progressive neural model & controller
│   │   ├── multi_head_model.py            # Shared multi-head neural network
│   │   ├── stopping_controller.py         # Calibrated entropy-bounded early stopping
│   │   ├── calibration.py                 # Platt scaling & Expected Calibration Error
│   │   └── baselines.py                   # Decoupled XGBoost & Random Forest baselines
│   └── evaluation/                        # Empirical benchmark runners & metrics
├── audit/                                 # Audited dataset splits & cryptographic digests
│   ├── data/                              # Master frozen dataset CSV (SHA-256 verified)
│   └── splits/                            # Historical train/val, temporal test, noise pool splits
├── artifacts/                             # Experimental outputs & trained models
│   ├── models/                            # PyTorch progressive weights & scalers
│   └── reports/                           # benchmark_results.json & benchmark_report.md
├── scripts/                               # Automation, verification, and compilation scripts
└── tests/                                 # Automated test suite
```

---

## 8. Quick Start & Execution Guide

### 1. Environment Setup
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Piyush6770/Technical-Seminar.git
cd Technical-Seminar
pip install -r requirements.txt
```

### 2. Verify Dataset Integrity
Verify that all dataset cohorts match their frozen SHA-256 digests:
```bash
python scripts/verify_integrity.py
```

### 3. Run the Full-Stack Web Application

> [!NOTE]
> **Modern Full-Stack Architecture**: The user interface runs on a modern **React 19 + Vite** frontend with a high-throughput **FastAPI** REST backend. Legacy Streamlit prototypes are deprecated and no longer used.

#### Option A: 1-Click Launcher (Windows)
Double-click or run from command line:
```bat
start_app.bat
```
This automatically starts the FastAPI backend server and launches the frontend.

#### Option B: Manual Launch
Start the FastAPI backend server (which automatically serves the built React frontend at `http://127.0.0.1:8000`):
```bash
python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```
Open your browser at `http://127.0.0.1:8000` to access:
- **Journal Audit**: Real-time progressive journal screening with calibrated predatory risk, confidence bounds, early-exit stage indicator, verified/risk signals, and exportable JSON audit records.
- **Benchmark Results**: Empirical performance tables across experiments E1–E6 ($N=1,800$, 2021–2026), Pareto latency frontiers, model comparisons, temporal degradation ($TGR = 0.5354$), and early exit distributions.
- **System Architecture**: Multi-stage feature hierarchy (Groups A–D), latency bounds, latent state update equations, and stopping controller decision policies.

Alternatively, to run the frontend in Vite development mode:
```bash
cd frontend
npm install
npm run dev
```

### 4. Run Experimental Benchmarks (E1 – E6)
Execute the complete empirical benchmark suite across all 5,528 serials:
```bash
python -m src.evaluation.run_benchmarks
```
Metrics and latency statistics are saved to `artifacts/reports/benchmark_results.json`.

### 5. Access Seminar Report & Literature Survey
- **Technical Seminar Report**: Open [`reports/Technical_Seminar_Report.docx`](reports/Technical_Seminar_Report.docx) for the complete 30–40 page PCCOE-formatted seminar report.
- **Literature Survey Excel**: Open [`reports/Literature_Survey.xlsx`](reports/Literature_Survey.xlsx) for the comprehensive 20-paper comparative matrix with all 10 academic criteria.
- **Research Paper**: Open [`research_paper/research_paper.pdf`](research_paper/research_paper.pdf) or [`research_paper/research_paper.docx`](research_paper/research_paper.docx) for the 7-page IEEE 2-column paper.
- **Authentic Reference Library**: Access all 20 downloaded publisher PDFs in [`research_paper/reference_papers/`](research_paper/reference_papers/).

---

## 9. Ethical, Legal & Global South Safeguards

1. **Defamation & Legal Liability**: Blacklist curators historically faced defamation lawsuits. Our architecture replaces opaque algorithmic verdicts with **verifiable factual provenance**—explicitly citing official registry discrepancies (e.g., verifying whether an ISSN is registered in the official portal or whether claimed indexing exists in DOAJ).
2. **Protection for Emerging Global South Venues**: Static classifiers discriminate against legitimate academic journals from developing regions (Africa, Latin America, South Asia) that operate on limited budgets without commercial DOI infrastructure. Through **selective abstention**, borderline records ($0.40 \le \hat{p} \le 0.60$) are withheld from automated blacklisting and routed to human expert librarians.

---

## 10. Research Citation

If you use this codebase, benchmark datasets, or progressive architecture in your research, please cite our manuscript:

```bibtex
@article{shinde2026costaware,
  title={Cost-Aware Progressive Predatory Journal Detection},
  author={Shinde, Swati and Jadhav, Suyog and Jadhav, Pratik and Patel, Piyush and Nikam, Parshwa},
  journal={IEEE Transactions on Information Forensics and Security / IEEE Access},
  year={2026},
  note={Under Review. Audited Dataset SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328}
}
```

---

## 11. License

This project is licensed under the Apache 2.0 License. All benchmark splits, model weights, and documentation are openly available for non-commercial scholarly integrity research.
