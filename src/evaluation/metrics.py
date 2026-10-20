"""
Evaluation Metrics & Benchmark Reporting Engine
Calculates: Precision, Recall, Macro-F1, Specificity, FPR, ROC-AUC, PR-AUC, Brier, ECE, Efficiency.
"""

import numpy as np
from typing import Dict, Any, Optional
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, brier_score_loss
)
from src.models.calibration import compute_ece

def calculate_comprehensive_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    wall_clock_ms_per_journal: float = 0.0,
    peak_ram_mb: float = 0.0,
    early_stop_distribution: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes all standard scholarly metrics required by the research prompt.
    """
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    precision = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0))
    recall = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    pred_f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))

    specificity = float(tn / max(1, tn + fp))
    fpr = float(fp / max(1, tn + fp))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except ValueError:
        pr_auc = 0.0

    brier = float(brier_score_loss(y_true, y_prob))
    ece, diagram_data = compute_ece(y_true, y_prob, n_bins=10)

    # Average feature groups acquired
    avg_groups = 4.0
    if early_stop_distribution and "stopped_stage" in early_stop_distribution:
        stages = early_stop_distribution["stopped_stage"]
        avg_groups = float(np.mean(stages))

    metrics = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "macro_f1": round(macro_f1, 4),
        "predatory_f1": round(pred_f1, 4),
        "specificity": round(specificity, 4),
        "false_positive_rate": round(fpr, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "expected_calibration_error": round(ece, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "efficiency": {
            "avg_groups_acquired": round(avg_groups, 2),
            "mean_wall_clock_ms_per_journal": round(wall_clock_ms_per_journal, 2),
            "peak_ram_mb": round(peak_ram_mb, 2),
            "early_stopping_breakdown": early_stop_distribution.get("early_stop_percentages", {}) if early_stop_distribution else {}
        },
        "reliability_diagram": diagram_data
    }
    return metrics
