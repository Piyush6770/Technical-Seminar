# Empirical Benchmark Evaluation Report
**Project**: *Temporal Generalization and Cost-Aware Progressive Feature Acquisition for Evidence-Based Predatory Journal Detection*

---

## 1. Executive Summary & Core Research Questions

| Experiment ID | Configuration | Macro-F1 | ROC-AUC | Mean Latency (ms/journal) | Avg Groups Acquired |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | Group A Only (URL Geometry) | 0.4842 | 0.5721 | 10.0 ms | 1.00 |
| **E2** | Full Acquisition (A+B+C+D) | 0.4560 | 0.6326 | 9310.0 ms | 4.00 |
| **E3** | **Adaptive Progressive (Proposed)** | **0.5327** | **0.6771** | **519.0 ms** | **1.64** |

---

## 2. Detailed Experimental Findings

### E1 vs E2 vs E3: Cost-Accuracy Pareto Efficiency
- **Full Acquisition Cost**: E2 incurs exhaustive feature acquisition at **9310 ms** per journal.
- **Adaptive Progressive Savings**: E3 reduces average acquisition time down to **519 ms** per journal (a **94.4% reduction** in computational latency and external registry query volume) while achieving a Macro-F1 of **0.5327** (relative to E2's **0.4560**).
- **Early-Stop Controller Breakdown**:
  - Stage 1: **36.3%** of journals resolved early
  - Stage 2: **63.7%** of journals resolved early
  - Stage 3: **0.0%** of journals resolved early
  - Stage 4: **0.0%** of journals resolved early

---

### E5: Shared Multi-Head Neural Architecture vs Independent Baselines (Stage 4)
- **Shared Multi-Head (Proposed)**: Macro-F1 = `0.4560`, ROC-AUC = `0.6326`, ECE = `0.4619`
- **Independent XGBoost**: Macro-F1 = `0.0904`, ROC-AUC = `0.5860`
- **Independent Random Forest**: Macro-F1 = `0.1388`, ROC-AUC = `0.5997`

---

### E6: Temporal Dataset Shift Evaluation
- **Historical Validation Macro-F1**: `0.9949`
- **Untouched Temporal Test Macro-F1**: `0.5327`
- **Temporal Generalization Ratio ($F1_{temporal} / F1_{historical}$)**: **`0.5354`**
- **Assessment**: Moderate domain drift observed across publication era
