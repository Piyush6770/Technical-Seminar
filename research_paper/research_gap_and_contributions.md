# Research Gap and Scientific Contribution Analysis

**Document Purpose**: Methodological and theoretical foundation establishing the legitimate research gap, scientific contributions, research questions, and literature comparison for the IEEE research paper.

---

## 1. Problem Formulation & Operational Context

In modern academic research, author-facing Article Processing Charges (APCs) have catalyzed the rise of deceptive, predatory academic publishing. While machine-learning models in the literature frequently claim detection accuracies exceeding $90\%$, operational adoption by university libraries, promotion committees, and grant evaluators remains virtually non-existent.

Our codebase audit reveals that this failure is attributable to three fundamental literature gaps:
1. **The Static Cross-Validation Fallacy**: Existing models are trained and tested on identically distributed ($i.i.d.$) random splits of historical web archives (primarily pre-2021 snapshots). Deceptive publishers operate adversarially, rapidly adopting modern Content Management Systems (e.g., Open Journal Systems), acquiring academic-sounding domains, and publishing professional editorial pages. Classifiers evaluated on static benchmarks fail catastrophically under longitudinal temporal shift.
2. **The Uniform Acquisition Cost Fallacy**: Prior work operates under an exhaustive feature paradigm where all signals—from cheap URL strings to headless browser JavaScript rendering and third-party registry API queries—are assumed to be available simultaneously at zero cost. In production, feature extraction latency ranges from $<0.01$s for URL geometry to over $5.0$s for external scholarly APIs subject to rate limits and downtime.
3. **The Ungrounded Scalar Risk Fallacy**: Existing systems output raw, uncalibrated scalar probabilities without verifiable provenance or evidence grounding. In academic personnel disputes or forensic audits, automated decisions must be accompanied by corroborated facts, and systems must possess a principled mechanism for selective abstention on ambiguous records.

---

## 2. Research Questions (RQs)

To rigorously investigate these challenges, the research establishes four core research questions:

- **RQ1 (Temporal Robustness)**: To what quantitative extent do machine-learning classifiers trained on historical (pre-2021) publishing patterns degrade when evaluated on an out-of-distribution temporal cohort of serials established between 2021 and 2026?
- **RQ2 (Cost-Accuracy Trade-off)**: Can an adaptive, confidence-bounded stopping controller dynamically halt feature acquisition at low-cost stages (URL geometry or static HTML) without compromising diagnostic precision, compared to exhaustive feature acquisition?
- **RQ3 (Representation Sharing vs. Decoupled Ensembles)**: Does joint representation learning across progressive stages provide regularized inductive bias that prevents catastrophic collapse under temporal distribution shift compared to decoupled tabular baselines (Random Forest, XGBoost)?
- **RQ4 (Selective Classification & Provenance Grounding)**: How effectively does combining Platt probability calibration, entropy-based confidence thresholds, and deterministic registry corroboration isolate ambiguous borderline serials for human expert review while maintaining high coverage on decisive cases?

---

## 3. Critical Literature Comparison

The table below contrasts existing representative approaches in predatory publishing forensics with our framework:

| Approach / Reference | Feature Domain | Temporal Split? | Acquisition Cost Awareness? | Shared Multi-Stage Architecture? | Calibrated Confidence? | Provenance Grounding & Selective Abstention? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Dadkhah & Bianciardi (2016)** [5] | Domain & WHOIS | No (Static) | No (Uniform) | No (Decision Trees) | No | No |
| **Shamseer et al. (2017)** [3] | Biomedical HTML Inspection | No (Cross-sectional) | No (Manual Audit) | No (Statistical Rules) | No | No |
| **NCTU DCS Lab (2023)** [7] | Lexical URL Features | No ($k$-fold $i.i.d.$) | No (Uniform) | No (Single SVM / RF) | No | No |
| **Bano et al. (2023)** [9] | Static DOM Trees | No ($k$-fold $i.i.d.$) | No (Uniform) | No (XGBoost / LightGBM) | No | No |
| **Krawczyk & Kulczycki (2023)** [8] | Editorial Board NLP | No (Single Snapshot) | No (Uniform) | No (Transformer Embeddings)| No | No |
| **This Work (Proposed Framework)** | **Hierarchical (URL + HTML + JS + Registries)** | **Yes (Pre-2021 Train/Val vs. 2021–2026 Test)** | **Yes (Adaptive Cost-Aware Controller)** | **Yes (Progressive Shared Multi-Head NN)** | **Yes (Platt Scaling + 10-bin ECE)** | **Yes (Deterministic Registry Corroboration & Triage)** |

---

## 4. Legitimate Scientific Contributions

We explicitly categorize the contributions of this research into verified novelties, engineering contributions, and experimentally validated findings:

### 4.1 Methodological and Architectural Novelties
1. **First Longitudinal Temporal Shift Benchmark**: Formulation of predatory journal detection as an out-of-distribution temporal shift task. Creation of an audited corpus ($N=5,528$) separating pre-2021 historical data from an untouched post-2020 evaluation cohort ($N=1,800$), establishing the formal **temporal generalization ratio** ($F_1^{\text{temp}} / F_1^{\text{hist}} = 0.5354$).
2. **Sequential Cost-Aware Feature Acquisition Hierarchy**: Structuring forensic signals into a 4-tier cost hierarchy ($<0.01$s, $\sim 0.8$s, $\sim 3.5$s, $\sim 5.0$s) governed by an adaptive, entropy-bounded stopping controller that optimizes a cost-error Pareto objective.
3. **Progressive Shared Representation Network**: Designing a sequential neural encoder with layer-normalized shared latent embeddings ($\phi_1 \to \phi_4$) that simultaneously trains intermediate classification heads, regularizing early layers against covariate shift.
4. **Evidence-Grounded Selective Classification Schema**: Coupling statistical neural outputs with deterministic registry corroboration, enforcing automated human triage whenever confidence falls between $40\%$ and $60\%$ or when registry facts contradict public website claims.

### 4.2 Engineering & System Integration Contributions
- Decoupled, timeout-protected feature extractors with local SQLite caching.
- Production-grade serialization decoupling PyTorch state dicts from scikit-learn standard scalers, ensuring safe deserialization (`weights_only=True`).
- Interactive institutional Streamlit dashboard offering real-time single-journal verification, progressive audit traces, and high-throughput batch CSV screening.

### 4.3 Experimentally Validated Results
- **94.4% Latency Reduction**: Reducing mean inference latency from $9,310$ ms down to $519$ ms per journal.
- **Superior Generalization over Exhaustive Acquisition**: Increasing temporal Macro-$F_1$ from $0.4560$ (E2) to $0.5327$ (E3) by early-stopping clear cases before noisy downstream features can degrade predictions.
- **Robustness over Tabular Baselines**: Outperforming decoupled Random Forest ($F_1 = 0.1388$) and XGBoost ($F_1 = 0.0904$), which suffer complete recall/precision collapse on temporal data.
