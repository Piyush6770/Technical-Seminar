# MASTER RESEARCH PROMPT & SPECIFICATION

**Project Title**: *Temporal Generalization and Cost-Aware Progressive Feature Acquisition for Evidence-Based Predatory Journal Detection*

---

## 1. System Role & Project Purpose
Act as a Principal Research Engineer, Applied Machine Learning Scientist, and Scholarly Integrity Investigator. Your objective is to design, implement, evaluate, and document a complete, reproducible research system that detects predatory academic journals under **temporal dataset shift**, utilizing **adaptive progressive feature acquisition** and **verifiable multi-source evidence grounding**.

You are not merely training a binary classifier on a static benchmark. You are constructing an end-to-end research framework that addresses three core scientific problems:
1. **Temporal Generalization**: Do machine-learning models trained on historical (pre-2021) publishing patterns retain efficacy on journals established after 2020?
2. **Cost-Aware Progressive Feature Acquisition**: Can an adaptive stopping controller dynamically halt inference at low-cost stages (URL/domain or HTML) without sacrificing diagnostic accuracy, deferring expensive dynamic rendering and external registry queries only to ambiguous cases?
3. **Evidence-Grounded Explanations**: Can the system output verifiable, source-linked provenance (confirmations, contradictions, registry evidence) alongside calibrated confidence scores, abstaining when evidence is contradictory or insufficient?

---

## 2. Empirical Ground-Truth Baseline & Dataset Architecture
All experiments must be conducted on the audited dataset artifacts produced in this repository. **Do not use unverified or unpartitioned data.**

### Reconciled Dataset Inventory
- **Historical AJPC Benchmark Baseline**: Exactly **2,046 records** (1,213 legitimate whitelist + 833 predatory blacklist). Derived from the NCTU DCS Lab baseline (*Scientific Reports*, 2023). Every historical split and feature representation matches this sum ($1,636$ training + $410$ testing). The earlier 2,700 figure was an unverified estimate from unmerged web crawling lists.
- **Post-2020 Discovered Serials**: Exactly **3,482 serial records** with confirmed inaugural publication dates between 2021 and 2026.
- **Combined Frozen Collection**: Exactly **5,528 data rows** (plus header row = 5,529 lines) in [`final_combined_journal_dataset.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/final_combined_journal_dataset.csv), frozen as read-only in [`audit/data/final_combined_journal_dataset_frozen_readonly.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/data/final_combined_journal_dataset_frozen_readonly.csv) (`SHA-256: d775c92cbda31fdc72c45b4f473e45de6bf0580f31d8ac61e960df8894c4f328`).

### Defensible Experimental Partitions
Supervised evaluation must be conducted **strictly** using the partitioned cohorts defined in [`audit/splits/evaluation_splits_manifest.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/splits/evaluation_splits_manifest.csv):
1. **Historical Training Split (`HISTORICAL_TRAIN`)**:
   - **1,636 records** (Pre-2021 historical baseline; 970 legitimate, 666 predatory).
   - Dedicated exclusively to representation learning and model optimization.
2. **Historical Validation Split (`HISTORICAL_VAL`)**:
   - **410 records** (Pre-2021 historical baseline; 243 legitimate, 167 predatory).
   - Dedicated to hyperparameter tuning, probability calibration, and stopping policy threshold selection.
3. **Untouched Temporal Test Cohort (`TEMPORAL_TEST_UNTOUCHED`)**:
   - **1,800 records** (Post-2020 verified cohort; 1,621 legitimate, 179 predatory) saved in [`audit/splits/temporal_test_cohort_untouched.csv`](file:///c:/Users/piyus/Technical%20Seminar/predatory_journals_detection/audit/splits/temporal_test_cohort_untouched.csv).
   - **Strictly Held Out**: Never seen during feature scaling, model fitting, or threshold selection. Evaluates out-of-distribution temporal generalization.
4. **Quarantined Unlabeled Pool (`audited_uncertain_records.csv`)**:
   - **1,682 serials** confirmed post-2020 but lacking definitive whitelist/blacklist listings. Quarantined to prevent label noise. Used only for zero-shot or semi-supervised exploration.

---

## 3. Four-Stage Progressive Feature Hierarchy
Features are organized into four hierarchical groups with monotonically increasing acquisition and computational costs. Each stage must be implemented in a decoupled, robust extractor module with local disk caching and timeout protection.

```
       [Input: Journal URL, Title, ISSN, Publisher]
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 1: Group A — URL & Domain Geometry (Cost ~ 0.01s)│
└────────────────────────────────────────────────────────┘
                           │
                           ▼
              [Adaptive Stopping Controller] ───(High Confidence)──► [Early Stop 1]
                           │ (Uncertain)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 2: Group B — HTML & Page Structure (Cost ~ 0.8s) │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
              [Adaptive Stopping Controller] ───(High Confidence)──► [Early Stop 2]
                           │ (Uncertain)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 3: Group C — JS & Dynamic Behavior (Cost ~ 3.5s) │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
              [Adaptive Stopping Controller] ───(High Confidence)──► [Early Stop 3]
                           │ (Uncertain)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 4: Group D — External Scholarly Registries (~5s) │
│           (Crossref, OpenAlex, DOAJ, ISSN Portal)      │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
               [Final Stage 4 Prediction]
```

### Feature Group Specifications
- **Group A (Inexpensive URL & Domain Geometry)**:
  - *Signals*: Total URL length, domain length, path length, dot count, hyphen count, numeric character ratio, symbol ratio, Shannon entropy of URL string, HTTPS boolean flag, top-level domain classification (generic, academic, free/suspicious), subdomain count.
  - *Acquisition Cost*: Negligible ($< 0.01$ s, purely local string computation).
  - *Limitation*: Captures domain naming heuristics, but cannot verify actual editorial governance or peer-review conduct.

- **Group B (HTML Structure & Published Editorial Policies)**:
  - *Signals*: HTTP status code, page download latency, DOM node depth, presence and link depth of editorial board page (`/editorial-board`, `/editors`), peer-review statement accessibility, article processing charge (APC) disclosure, publication ethics / COPE adherence declarations, contact email domain matching (institutional vs generic freemail like Gmail/Yahoo), copyright notice freshness, text-to-HTML ratio.
  - *Acquisition Cost*: Moderate ($\sim 0.5 - 1.2$ s per journal; single static HTTP GET request).
  - *Limitation*: Static HTML may omit content injected via client-side JavaScript or single-page applications.

- **Group C (JavaScript, Dynamic Rendering & Client-Side Behavior)**:
  - *Signals*: Script tag count, ratio of external third-party script domains to first-party scripts, presence of known intrusive ad networks or crypto miners, difference between raw HTML word count and rendered DOM word count, automated redirect count, presence of client-side obfuscation.
  - *Acquisition Cost*: High ($\sim 3.0 - 5.0$ s per journal; headless browser execution via Playwright/Selenium in an isolated sandbox).
  - *Limitation*: Resource-heavy; must demonstrate whether the marginal predictive lift justifies browser rendering overhead.

- **Group D (External Scholarly Metadata & Registry Corroboration)**:
  - *Signals*: ISSN Portal registration validity, Crossref DOI prefix existence, annual publication volume variance in Crossref/OpenAlex, citation metrics, DOAJ indexing confirmation, Scopus/Web of Science claims verification, editorial board institutional identity match score.
  - *Acquisition Cost*: Highest ($\sim 2.0 - 6.0$ s per journal; dependent on external network APIs, rate limits, and network latency).
  - *Limitation*: External registries have differing ingestion lag; absence from DOAJ is not proof of predatory practice.

---

## 4. Multi-Stage Progressive Model Architecture
The architecture comprises a unified shared feature encoder with four sequential prediction heads:

$$\hat{y}_1 = f_{\text{head}_1}(\phi_1(x_A))$$
$$\hat{y}_2 = f_{\text{head}_2}(\phi_2(x_A, x_B))$$
$$\hat{y}_3 = f_{\text{head}_3}(\phi_3(x_A, x_B, x_C))$$
$$\hat{y}_4 = f_{\text{head}_4}(\phi_4(x_A, x_B, x_C, x_D))$$

### Adaptive Stopping Controller & Decision Policy
At stage $k \in \{1, 2, 3\}$, the system computes:
1. **Calibrated Confidence**: $c_k = \max(\hat{p}_k, 1 - \hat{p}_k)$, where $\hat{p}_k$ is calibrated via Platt scaling or Isotonic regression fitted on `HISTORICAL_VAL`.
2. **Predictive Uncertainty**: Entropy $H_k = - \sum_{i} \hat{p}_{k,i} \log \hat{p}_{k,i}$.
3. **Stopping Criterion**:
   $$\text{Stop if } c_k \ge \tau_k \quad \text{AND} \quad \Delta_{\text{cost}}(k \to k+1) > \lambda \cdot \mathbb{E}[\Delta_{\text{error}}]$$
   where thresholds $\tau_1, \tau_2, \tau_3$ and cost-penalty parameter $\lambda$ are optimized on the validation set using cost-sensitive ROC optimization, then **frozen** prior to testing.

### Baseline Comparisons Required
The progressive architecture must be benchmarked against:
1. **Independent Stage Baselines**: Decoupled Random Forest and XGBoost models trained independently on $\{A\}$, $\{A,B\}$, $\{A,B,C\}$, and $\{A,B,C,D\}$.
2. **Full-Acquisition Non-Adaptive Baseline**: Monolithic model always acquiring all four groups $\{A,B,C,D\}$ regardless of cost.
3. **Cheap-Only Baseline**: Model relying exclusively on Group A.

---

## 5. Experimental Benchmark Matrix
Implement automated evaluation scripts that execute and report the following six formal research experiments:

| Exp ID | Configuration | Core Research Question |
| :--- | :--- | :--- |
| **E1** | Group A Only | Baseline detection performance and acquisition latency using only cheap URL/domain signals. |
| **E2** | Full Acquisition (A+B+C+D) | Theoretical performance upper-bound when all feature groups are exhaustively acquired. |
| **E3** | Adaptive Progressive Acquisition | Can adaptive stopping match E2's accuracy while substantially reducing average acquisition cost? |
| **E4** | Fixed Progressive Acquisition | Does data-driven adaptive stopping outperform fixed heuristic stopping stages? |
| **E5** | Shared Multi-Head vs. Independent Baselines | Does representation sharing provide statistical advantage over independent tabular ensembles? |
| **E6** | Historical vs. Temporal Test Shift | Quantitative degradation of models trained on pre-2021 data when evaluated on post-2020 serials. |

### Required Quantitative Reporting Metrics
- **Classification Performance**: Precision, Recall, Macro-F1, Specificity, False Positive Rate (FPR), ROC-AUC, PR-AUC.
- **Probability Calibration**: Brier Score, Expected Calibration Error (ECE) with 10 equal-width bins, Reliability Diagrams.
- **Resource & Acquisition Efficiency**: Average feature groups acquired per journal, % early stopped at Stage 1 / 2 / 3, mean wall-clock latency (ms/journal), memory footprint (peak RAM MB), external API call volume.
- **Temporal Generalization Ratio**: $\text{Degradation} = \text{F1}_{\text{temporal}} / \text{F1}_{\text{historical}}$.

---

## 6. Explainability & Evidence-Grounded Diagnostic Output
The output for any query journal must **never** be a raw ungrounded probability score. It must produce a structured, machine-readable JSON artifact and a human-readable diagnostic report distinguishing model estimates from verified facts:

```json
{
  "journal_identity": {
    "query_input": "https://example-journal.org",
    "canonical_title": "Example Journal of Applied Engineering",
    "issn_l": "2834-XXXX",
    "identity_status": "IDENTITY_VERIFIED",
    "verification_source": "OpenAlex Serial Registry"
  },
  "progressive_assessment": {
    "stopping_stage": "Stage 2 (Groups A + B)",
    "calibrated_risk_probability": 0.082,
    "confidence_level": "High (91.8%)",
    "risk_classification": "Legitimate / Credible",
    "feature_groups_acquired": ["Group A", "Group B"],
    "groups_skipped_due_to_confidence": ["Group C", "Group D"],
    "total_acquisition_time_sec": 0.84
  },
  "evidence_grounding": {
    "corroborated_facts": [
      "Publisher is an established university press with active COPE membership.",
      "Editorial board members have verified institutional faculty profiles."
    ],
    "unverified_or_contradicted_claims": [],
    "abstention_status": "DECISION_FINAL"
  }
}
```

If risk probability is between $0.40$ and $0.60$ or if evidence from registries directly contradicts extracted website content, the system must explicitly output `abstention_status: "REQUIRES_HUMAN_EXPERT_REVIEW"`.

---

## 7. Recommended Technology Stack & Engineering Standards
- **Core Environment**: Python 3.10+ in a clean virtual environment.
- **Data Engineering**: `pandas`, `numpy`, `scipy`.
- **Parsing & Static Extraction**: `BeautifulSoup4`, `lxml`, `tldextract`.
- **Dynamic Browser Rendering**: `playwright` (headless, isolated network sandbox, 10s strict timeout).
- **External Scholarly APIs**: Direct REST clients for `Crossref`, `OpenAlex`, `DOAJ`, and `ISSN Portal` with backoff retry handlers.
- **Machine Learning & Calibration**: `scikit-learn`, `xgboost`, `torch` (for shared multi-head architecture).
- **Explainability**: `shap` for feature attribution, paired with deterministic rule-based evidence extraction.
- **Demonstration UI**: Modern `React 19` + `FastAPI` web application for interactive single-journal audit and benchmark analysis.
- **Reproducibility**: Seed `42` pinned across all stochastic processes; strict isolation between training and temporal test splits.

---

## 8. Implementation Roadmap
1. **Module 1: Feature Extraction Pipeline** (`src/features/`): Implement `group_a_url.py`, `group_b_html.py`, `group_c_dynamic.py`, and `group_d_scholarly.py` with caching and offline fallback.
2. **Module 2: Model Training & Multi-Head Encoder** (`src/models/`): Train independent baselines and the progressive multi-head neural architecture on `HISTORICAL_TRAIN`.
3. **Module 3: Calibration & Stopping Policy** (`src/models/stopping_controller.py`): Optimize confidence thresholds on `HISTORICAL_VAL`.
4. **Module 4: Temporal Generalization Evaluation** (`src/evaluation/`): Run full evaluation on `TEMPORAL_TEST_UNTOUCHED` across E1–E6.
5. **Module 5: Interactive Diagnostic Dashboard** (`frontend/` & `src/api_server.py`): Provide real-time URL inspection with cost breakdown, evidence trace, and calibrated risk score.
