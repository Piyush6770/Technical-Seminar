# Experimental Evaluation Plan & Empirical Verification Protocol

**Document Purpose**: Formal specification of completed empirical evaluations (E1–E6) and roadmap for supplementary experiments, stress-testing, and multi-year longitudinal extensions.

---

## 1. Summary of Completed Formal Experiments (E1–E6)

The framework has completed six formal experiments executed across the frozen dataset splits:
- `HISTORICAL_TRAIN`: $1,636$ serials ($970$ legitimate, $666$ predatory).
- `HISTORICAL_VAL`: $410$ serials ($243$ legitimate, $167$ predatory).
- `TEMPORAL_TEST_UNTOUCHED`: $1,800$ serials ($1,621$ legitimate, $179$ predatory).

```
╔═════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                               PRIMARY BENCHMARK EXPERIMENT SUMMARY MATRIX                               ║
╠═════════╦══════════════════════════╦═══════════╦════════╦══════════╦══════════╦══════════════╦══════════╣
║ Exp ID  ║ Configuration            ║ Precision ║ Recall ║ Macro-F1 ║ ROC-AUC  ║ Latency (ms) ║ Stages   ║
╠═════════╬══════════════════════════╬═══════════╬════════╬══════════╬══════════╬══════════════╬══════════╣
║ **E1**  ║ Group A Only (URL)       ║ 0.1265    ║ 0.5866 ║ 0.4842   ║ 0.5721   ║ 10.0         ║ 1.00     ║
║ **E2**  ║ Full Acquisition (A-D)   ║ 0.1192    ║ 0.5363 ║ 0.4560   ║ 0.6326   ║ 9,310.0      ║ 4.00     ║
║ **E3**  ║ Adaptive Progressive     ║ 0.1581    ║ 0.6704 ║ 0.5327   ║ 0.6771   ║ 519.0        ║ 1.64     ║
║ **E4**  ║ Fixed Stage Ablations    ║ Fixed S1: 0.4842 | S2: 0.4907 | S3: 0.4804 | S4: 0.4560            ║
║ **E5**  ║ Baselines (RF / XGBoost) ║ RF: 0.1388 | XGBoost: 0.0904 (Collapses under temporal shift)    ║
║ **E6**  ║ Temporal Shift Test      ║ Historical Val: 0.9949 ──► Temporal Test: 0.5327 (Ratio: 0.5354)   ║
╚═════════╩══════════════════════════╩═══════════╩════════╩══════════╩══════════╩══════════════╩══════════╝
```

---

## 2. Experimental Verification Trace

All numerical values reported above have been extracted deterministically from:
- `artifacts/reports/benchmark_results.json`
- `artifacts/reports/benchmark_report.md`
- Code execution module: `src/evaluation/run_benchmarks.py`

### Key Empirical Findings Verified:
1. **The Fallacy of Static Benchmarks**: Evaluating on historical validation gives an illusion of near-perfection ($F_1 = 0.9949$), which drops to $0.5327$ when tested out-of-distribution on untouched post-2020 serials.
2. **Noise Pruning via Early Exiting**: Monolithic full acquisition (E2) achieves lower Macro-$F_1$ ($0.4560$) than our adaptive model ($0.5327$), because deceptive serials post-2020 present superficially valid OJS templates and partial Crossref deposits that confuse downstream heads. Early stopping on decisive cases avoids this noise.
3. **94.4% Latency Reduction**: Wall-clock acquisition latency drops from $9,310$ ms per journal to $519$ ms, resolving $36.3\%$ at Stage 1 and $63.7\%$ at Stage 2.

---

## 3. Supplementary Experimental Evaluation Plan

To further strengthen the paper for archival Q1 journals (e.g., *IEEE T-IFS*, *ACM TOIS*), the following supplementary experiments are designed:

### Experiment S1: Rolling-Year Temporal Degradation Analysis
- **Objective**: Track the degradation trajectory year-by-year ($2021 \to 2022 \to 2023 \to 2024 \to 2025 \to 2026$) rather than treating post-2020 as a single aggregate cohort.
- **Protocol**:
  1. Slice `TEMPORAL_TEST_UNTOUCHED` into annual inaugural subsets using publication metadata.
  2. Measure Macro-$F_1$, Brier score, and Expected Calibration Error (ECE) annually.
  3. Hypothesis: Performance degrades monotonically with increasing temporal distance from 2020.

### Experiment S2: Adversarial Web Cloaking Resistance
- **Objective**: Evaluate how robust the system is against adversarial publishers that detect web crawlers and serve sanitized static HTML.
- **Protocol**:
  1. Simulate crawler detection by injecting static legitimate templates while serving dynamic redirect scripts.
  2. Compare detection rates when Stage 3 dynamic headless browser rendering is forcibly triggered vs. bypassed.
  3. Metric: Change in recall under cloaking simulations.

### Experiment S3: Human-in-the-Loop Inter-Rater Agreement Benchmark
- **Objective**: Quantify human expert agreement on serials flagged with `abstention_status: "REQUIRES_HUMAN_EXPERT_REVIEW"`.
- **Protocol**:
  1. Sample 100 serials where the system triggered selective abstention (posterior risk $0.40 \le \hat{p} \le 0.60$ or registry contradiction).
  2. Have three independent scholarly integrity experts (librarians / bibliometricians) audit the 100 serials blindly.
  3. Calculate Fleiss' Kappa ($\kappa$) inter-rater reliability.
  4. Compare expert consensus against model risk scores.

### Experiment S4: Cross-Lingual Evaluation on Non-English Serials
- **Objective**: Measure feature stability and extraction degradation on non-English academic serials (e.g., Spanish, Portuguese, French, Indonesian).
- **Protocol**:
  1. Identify non-English publications within the quarantined pool (`audited_uncertain_records.csv`).
  2. Evaluate text-to-HTML ratios, editorial keyword matching, and registry verification across language boundaries.
  3. Propose multilingual keyword expansion vectors for Stage 2 HTML feature extractors.
