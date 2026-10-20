"""
Probability Calibration and Uncertainty Quantification Module
Implements Platt Scaling, Isotonic Regression, ECE (10 equal-width bins), and Brier Score.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> Tuple[float, Dict[str, Any]]:
    """
    Computes Expected Calibration Error (ECE) across 10 equal-width bins.
    Returns (ece_score, reliability_diagram_data).
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)

    bin_accs = []
    bin_confs = []
    bin_counts = []

    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        if i == n_bins - 1:
            mask = (y_prob >= low) & (y_prob <= high)
        else:
            mask = (y_prob >= low) & (y_prob < high)

        count = np.sum(mask)
        if count > 0:
            acc = np.mean(y_true[mask])
            conf = np.mean(y_prob[mask])
            ece += (count / total_samples) * np.abs(acc - conf)
            bin_accs.append(float(acc))
            bin_confs.append(float(conf))
            bin_counts.append(int(count))
        else:
            bin_accs.append(0.0)
            bin_confs.append((low + high) / 2.0)
            bin_counts.append(0)

    diagram_data = {
        "bin_boundaries": bin_boundaries.tolist(),
        "bin_accuracies": bin_accs,
        "bin_confidences": bin_confs,
        "bin_counts": bin_counts,
        "ece": float(round(ece, 4))
    }
    return float(round(ece, 4)), diagram_data

def compute_entropy(p: np.ndarray) -> np.ndarray:
    """Computes binary entropy H = -(p * ln(p) + (1-p) * ln(1-p))."""
    p_clipped = np.clip(p, 1e-7, 1 - 1e-7)
    return -(p_clipped * np.log(p_clipped) + (1 - p_clipped) * np.log(1 - p_clipped))

class StageCalibrator:
    def __init__(self, method: str = "platt"):
        """
        method: 'platt' (Logistic) or 'isotonic'
        """
        self.method = method.lower()
        self.calibrators: Dict[int, Any] = {}

    def fit_stage(self, stage: int, raw_probs: np.ndarray, y_val: np.ndarray):
        """
        Fits calibrator on HISTORICAL_VAL predictions for a given stage.
        """
        raw_p = np.clip(raw_probs, 1e-6, 1 - 1e-6)
        if self.method == "platt":
            # Platt scaling: log-odds as input to LogisticRegression
            log_odds = np.log(raw_p / (1 - raw_p)).reshape(-1, 1)
            clf = LogisticRegression(C=1.0, solver="lbfgs")
            clf.fit(log_odds, y_val)
            self.calibrators[stage] = clf
        else:
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            iso.fit(raw_p, y_val)
            self.calibrators[stage] = iso

    def calibrate(self, stage: int, raw_probs: np.ndarray) -> np.ndarray:
        """
        Calibrates raw probabilities for a given stage.
        """
        if stage not in self.calibrators:
            return raw_probs

        raw_p = np.clip(raw_probs, 1e-6, 1 - 1e-6)
        cal = self.calibrators[stage]

        if self.method == "platt":
            log_odds = np.log(raw_p / (1 - raw_p)).reshape(-1, 1)
            return cal.predict_proba(log_odds)[:, 1]
        else:
            return cal.predict(raw_p)

    def evaluate_calibration(self, y_true: np.ndarray, probs: np.ndarray) -> Dict[str, float]:
        brier = float(round(brier_score_loss(y_true, probs), 4))
        ece, _ = compute_ece(y_true, probs, n_bins=10)
        return {"brier_score": brier, "ece": ece}
