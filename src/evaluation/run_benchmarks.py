"""
Formal Experimental Benchmark Suite (E1 - E6)
Automates the execution of experiments E1 to E6 defined in Section 5 of the specification.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import time
import tracemalloc
import pandas as pd
import numpy as np

from src.config import (
    HISTORICAL_TRAIN_PATH, HISTORICAL_VAL_PATH, TEMPORAL_TEST_PATH,
    STAGE_COSTS, CUMULATIVE_STAGE_COSTS, REPORTS_DIR, MODEL_DIR
)
from src.features.pipeline import FeaturePipeline
from src.models.baselines import IndependentStageBaselines
from src.models.multi_head_model import MultiHeadModelTrainer
from src.models.calibration import StageCalibrator
from src.models.stopping_controller import AdaptiveStoppingController
from src.evaluation.metrics import calculate_comprehensive_metrics

def run_all_benchmarks():
    print("=" * 70)
    print("STARTING EXPERIMENTAL BENCHMARK SUITE (E1 - E6)")
    print("=" * 70)

    # 1. Load partitioned datasets
    print("\n[Step 1/6] Loading canonical partitioned cohorts...")
    df_train = pd.read_csv(HISTORICAL_TRAIN_PATH)
    df_val = pd.read_csv(HISTORICAL_VAL_PATH)
    df_temporal = pd.read_csv(TEMPORAL_TEST_PATH)

    y_train = df_train["label"].values
    y_val = df_val["label"].values
    y_temporal = df_temporal["label"].values

    print(f"Historical Train: {len(df_train)} records (Legit: {(y_train==0).sum()}, Pred: {(y_train==1).sum()})")
    print(f"Historical Val:   {len(df_val)} records (Legit: {(y_val==0).sum()}, Pred: {(y_val==1).sum()})")
    print(f"Temporal Test:    {len(df_temporal)} records (Legit: {(y_temporal==0).sum()}, Pred: {(y_temporal==1).sum()})")

    # 2. Extract multi-stage features
    print("\n[Step 2/6] Extracting multi-stage features (Groups A, B, C, D)...")
    pipeline = FeaturePipeline(use_cache=True)

    t0 = time.perf_counter()
    train_feats = pipeline.extract_dataframe(df_train, up_to_stage=4)
    val_feats = pipeline.extract_dataframe(df_val, up_to_stage=4)
    temporal_feats = pipeline.extract_dataframe(df_temporal, up_to_stage=4)
    extract_time = time.perf_counter() - t0
    print(f"Feature extraction completed in {extract_time:.2f}s across all cohorts.")

    # 3. Fit Independent Baselines (RF and XGBoost)
    print("\n[Step 3/6] Training Independent Baselines (Random Forest & XGBoost)...")
    rf_baselines = IndependentStageBaselines(model_type="rf")
    rf_baselines.fit(train_feats, y_train)
    rf_baselines.save("independent_baseline")

    xgb_baselines = IndependentStageBaselines(model_type="xgboost")
    xgb_baselines.fit(train_feats, y_train)
    xgb_baselines.save("independent_baseline")

    # 4. Train Progressive Shared Multi-Head Neural Network
    print("\n[Step 4/6] Training Progressive Shared Multi-Head Neural Network on HISTORICAL_TRAIN...")
    tracemalloc.start()
    nn_trainer = MultiHeadModelTrainer(device="cpu")
    nn_trainer.train_network(
        train_feats, y_train, val_feats, y_val,
        epochs=70, batch_size=32, lr=1e-3
    )
    current_ram, peak_ram = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_ram_mb = peak_ram / (1024 * 1024)
    nn_trainer.save()
    print(f"Neural model trained and saved. Peak memory during training: {peak_ram_mb:.2f} MB")

    # 5. Fit Calibrator on HISTORICAL_VAL
    print("\n[Step 5/6] Fitting Platt Scaling Calibrator on HISTORICAL_VAL...")
    calibrator = StageCalibrator(method="platt")
    raw_val_probs = {}
    cal_val_probs = {}

    for stage in [1, 2, 3, 4]:
        raw_p = nn_trainer.predict_stage_proba(val_feats, stage=stage)
        raw_val_probs[stage] = raw_p
        calibrator.fit_stage(stage, raw_p, y_val)
        cal_val_probs[stage] = calibrator.calibrate(stage, raw_p)

    # 6. Optimize Adaptive Stopping Controller on HISTORICAL_VAL
    print("\n[Step 6/6] Optimizing Adaptive Stopping Controller on HISTORICAL_VAL...")
    controller = AdaptiveStoppingController()
    opt_info = controller.optimize_on_val(cal_val_probs, y_val, cost_weight=0.04)
    controller.save()
    print(f"Optimized Stopping Policy: tau_1={controller.tau_1:.2f}, tau_2={controller.tau_2:.2f}, "
          f"tau_3={controller.tau_3:.2f}, lambda={controller.lambda_penalty:.1f}")

    # Compute calibrated probabilities on TEMPORAL_TEST_UNTOUCHED
    raw_temp_probs = {}
    cal_temp_probs = {}
    for stage in [1, 2, 3, 4]:
        p = nn_trainer.predict_stage_proba(temporal_feats, stage=stage)
        raw_temp_probs[stage] = p
        cal_temp_probs[stage] = calibrator.calibrate(stage, p)

    # =========================================================================
    # FORMAL EXPERIMENTAL EVALUATION (E1 - E6)
    # =========================================================================
    results = {}

    # -------------------------------------------------------------------------
    # E1: Group A Only Baseline
    # -------------------------------------------------------------------------
    print("\nExecuting E1: Group A Only Baseline...")
    e1_preds = (cal_temp_probs[1] >= 0.5).astype(int)
    results["E1_group_a_only"] = calculate_comprehensive_metrics(
        y_true=y_temporal,
        y_pred=e1_preds,
        y_prob=cal_temp_probs[1],
        wall_clock_ms_per_journal=STAGE_COSTS["stage_1"] * 1000,
        peak_ram_mb=peak_ram_mb,
        early_stop_distribution={"stopped_stage": np.ones(len(y_temporal)), "early_stop_percentages": {"Stage 1": 100.0}}
    )

    # -------------------------------------------------------------------------
    # E2: Full Acquisition (A+B+C+D) Upper Bound
    # -------------------------------------------------------------------------
    print("Executing E2: Full Acquisition (A+B+C+D) Upper Bound...")
    e2_preds = (cal_temp_probs[4] >= 0.5).astype(int)
    results["E2_full_acquisition"] = calculate_comprehensive_metrics(
        y_true=y_temporal,
        y_pred=e2_preds,
        y_prob=cal_temp_probs[4],
        wall_clock_ms_per_journal=CUMULATIVE_STAGE_COSTS[4] * 1000,
        peak_ram_mb=peak_ram_mb,
        early_stop_distribution={"stopped_stage": np.full(len(y_temporal), 4), "early_stop_percentages": {"Stage 4": 100.0}}
    )

    # -------------------------------------------------------------------------
    # E3: Adaptive Progressive Acquisition
    # -------------------------------------------------------------------------
    print("Executing E3: Adaptive Progressive Acquisition...")
    e3_eval = controller.evaluate_batch(cal_temp_probs)
    e3_preds = (e3_eval["final_probs"] >= 0.5).astype(int)
    results["E3_adaptive_progressive"] = calculate_comprehensive_metrics(
        y_true=y_temporal,
        y_pred=e3_preds,
        y_prob=e3_eval["final_probs"],
        wall_clock_ms_per_journal=e3_eval["mean_cost_sec"] * 1000,
        peak_ram_mb=peak_ram_mb,
        early_stop_distribution=e3_eval
    )

    # -------------------------------------------------------------------------
    # E4: Fixed Progressive Acquisition (Stages 1, 2, 3, 4)
    # -------------------------------------------------------------------------
    print("Executing E4: Fixed Progressive Acquisition Comparisons...")
    e4_stages = {}
    for stg in [1, 2, 3, 4]:
        stg_preds = (cal_temp_probs[stg] >= 0.5).astype(int)
        e4_stages[f"fixed_stage_{stg}"] = calculate_comprehensive_metrics(
            y_true=y_temporal,
            y_pred=stg_preds,
            y_prob=cal_temp_probs[stg],
            wall_clock_ms_per_journal=CUMULATIVE_STAGE_COSTS[stg] * 1000,
            peak_ram_mb=peak_ram_mb,
            early_stop_distribution={"stopped_stage": np.full(len(y_temporal), stg)}
        )
    results["E4_fixed_stages"] = e4_stages

    # -------------------------------------------------------------------------
    # E5: Shared Multi-Head vs Independent Baselines
    # -------------------------------------------------------------------------
    print("Executing E5: Shared Multi-Head vs Independent Baselines...")
    e5_comparison = {}
    for stg in [1, 2, 3, 4]:
        # XGBoost baseline at stage
        xgb_prob = xgb_baselines.predict_proba_stage(temporal_feats[f"X_stage{stg}"], stage_num=stg)[:, 1]
        xgb_pred = (xgb_prob >= 0.5).astype(int)

        # RF baseline at stage
        rf_prob = rf_baselines.predict_proba_stage(temporal_feats[f"X_stage{stg}"], stage_num=stg)[:, 1]
        rf_pred = (rf_prob >= 0.5).astype(int)

        # Multi-head NN at stage
        nn_prob = cal_temp_probs[stg]
        nn_pred = (nn_prob >= 0.5).astype(int)

        e5_comparison[f"stage_{stg}"] = {
            "xgboost": calculate_comprehensive_metrics(y_temporal, xgb_pred, xgb_prob),
            "random_forest": calculate_comprehensive_metrics(y_temporal, rf_pred, rf_prob),
            "shared_multi_head": calculate_comprehensive_metrics(y_temporal, nn_pred, nn_prob)
        }
    results["E5_architecture_comparison"] = e5_comparison

    # -------------------------------------------------------------------------
    # E6: Historical vs. Temporal Test Shift Degradation
    # -------------------------------------------------------------------------
    print("Executing E6: Historical vs Temporal Test Shift Degradation...")
    # Evaluate Historical Validation performance under E3 policy
    val_e3_eval = controller.evaluate_batch(cal_val_probs)
    val_e3_preds = (val_e3_eval["final_probs"] >= 0.5).astype(int)
    val_metrics = calculate_comprehensive_metrics(
        y_true=y_val,
        y_pred=val_e3_preds,
        y_prob=val_e3_eval["final_probs"],
        wall_clock_ms_per_journal=val_e3_eval["mean_cost_sec"] * 1000
    )

    temporal_macro_f1 = results["E3_adaptive_progressive"]["macro_f1"]
    historical_macro_f1 = val_metrics["macro_f1"]
    degradation_ratio = round(temporal_macro_f1 / max(1e-5, historical_macro_f1), 4)

    results["E6_temporal_shift"] = {
        "historical_val_metrics": val_metrics,
        "temporal_test_metrics": results["E3_adaptive_progressive"],
        "historical_macro_f1": historical_macro_f1,
        "temporal_macro_f1": temporal_macro_f1,
        "temporal_generalization_ratio": degradation_ratio,
        "shift_interpretation": (
            "Temporal shift shows robust generalization with ratio > 0.85"
            if degradation_ratio >= 0.85 else "Moderate domain drift observed across publication era"
        )
    }

    # Save benchmark results
    json_path = os.path.join(REPORTS_DIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll benchmark results exported to: {json_path}")

    # Generate research report markdown
    report_md_path = os.path.join(REPORTS_DIR, "benchmark_report.md")
    generate_markdown_report(results, report_md_path)
    print(f"Comprehensive markdown research report generated: {report_md_path}")

    return results

def generate_markdown_report(results: Dict[str, Any], output_path: str):
    e1 = results["E1_group_a_only"]
    e2 = results["E2_full_acquisition"]
    e3 = results["E3_adaptive_progressive"]
    e6 = results["E6_temporal_shift"]

    md = f"""# Empirical Benchmark Evaluation Report
**Project**: *Temporal Generalization and Cost-Aware Progressive Feature Acquisition for Evidence-Based Predatory Journal Detection*

---

## 1. Executive Summary & Core Research Questions

| Experiment ID | Configuration | Macro-F1 | ROC-AUC | Mean Latency (ms/journal) | Avg Groups Acquired |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | Group A Only (URL Geometry) | {e1['macro_f1']:.4f} | {e1['roc_auc']:.4f} | {e1['efficiency']['mean_wall_clock_ms_per_journal']:.1f} ms | 1.00 |
| **E2** | Full Acquisition (A+B+C+D) | {e2['macro_f1']:.4f} | {e2['roc_auc']:.4f} | {e2['efficiency']['mean_wall_clock_ms_per_journal']:.1f} ms | 4.00 |
| **E3** | **Adaptive Progressive (Proposed)** | **{e3['macro_f1']:.4f}** | **{e3['roc_auc']:.4f}** | **{e3['efficiency']['mean_wall_clock_ms_per_journal']:.1f} ms** | **{e3['efficiency']['avg_groups_acquired']:.2f}** |

---

## 2. Detailed Experimental Findings

### E1 vs E2 vs E3: Cost-Accuracy Pareto Efficiency
- **Full Acquisition Cost**: E2 incurs exhaustive feature acquisition at **{e2['efficiency']['mean_wall_clock_ms_per_journal']:.0f} ms** per journal.
- **Adaptive Progressive Savings**: E3 reduces average acquisition time down to **{e3['efficiency']['mean_wall_clock_ms_per_journal']:.0f} ms** per journal (a **{(1.0 - e3['efficiency']['mean_wall_clock_ms_per_journal']/e2['efficiency']['mean_wall_clock_ms_per_journal'])*100:.1f}% reduction** in computational latency and external registry query volume) while achieving a Macro-F1 of **{e3['macro_f1']:.4f}** (relative to E2's **{e2['macro_f1']:.4f}**).
- **Early-Stop Controller Breakdown**:
"""
    breakdown = e3['efficiency']['early_stopping_breakdown']
    for k, v in breakdown.items():
        md += f"  - Stage {k}: **{v:.1f}%** of journals resolved early\n"

    md += f"""
---

### E5: Shared Multi-Head Neural Architecture vs Independent Baselines (Stage 4)
- **Shared Multi-Head (Proposed)**: Macro-F1 = `{results['E5_architecture_comparison']['stage_4']['shared_multi_head']['macro_f1']:.4f}`, ROC-AUC = `{results['E5_architecture_comparison']['stage_4']['shared_multi_head']['roc_auc']:.4f}`, ECE = `{results['E5_architecture_comparison']['stage_4']['shared_multi_head']['expected_calibration_error']:.4f}`
- **Independent XGBoost**: Macro-F1 = `{results['E5_architecture_comparison']['stage_4']['xgboost']['macro_f1']:.4f}`, ROC-AUC = `{results['E5_architecture_comparison']['stage_4']['xgboost']['roc_auc']:.4f}`
- **Independent Random Forest**: Macro-F1 = `{results['E5_architecture_comparison']['stage_4']['random_forest']['macro_f1']:.4f}`, ROC-AUC = `{results['E5_architecture_comparison']['stage_4']['random_forest']['roc_auc']:.4f}`

---

### E6: Temporal Dataset Shift Evaluation
- **Historical Validation Macro-F1**: `{e6['historical_macro_f1']:.4f}`
- **Untouched Temporal Test Macro-F1**: `{e6['temporal_macro_f1']:.4f}`
- **Temporal Generalization Ratio ($F1_{{temporal}} / F1_{{historical}}$)**: **`{e6['temporal_generalization_ratio']:.4f}`**
- **Assessment**: {e6['shift_interpretation']}
"""

    with open(output_path, "w") as f:
        f.write(md)

if __name__ == "__main__":
    run_all_benchmarks()
