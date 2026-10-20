"""
Adaptive Progressive Stopping Controller & Decision Policy
Implements cost-aware early stopping with calibrated confidence and entropy thresholding.
"""

import json
import os
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from src.config import STAGE_COSTS, CUMULATIVE_STAGE_COSTS, MODEL_DIR
from src.models.calibration import compute_entropy

class AdaptiveStoppingController:
    def __init__(
        self,
        tau_1: float = 0.88,
        tau_2: float = 0.84,
        tau_3: float = 0.80,
        lambda_penalty: float = 12.0
    ):
        self.tau_1 = float(tau_1)
        self.tau_2 = float(tau_2)
        self.tau_3 = float(tau_3)
        self.lambda_penalty = float(lambda_penalty)
        self.is_frozen = False

    def get_threshold(self, stage: int) -> float:
        if stage == 1:
            return self.tau_1
        elif stage == 2:
            return self.tau_2
        elif stage == 3:
            return self.tau_3
        return 1.0  # Final stage 4 always terminates

    def should_stop(self, stage: int, p_k: float) -> Tuple[bool, float, float]:
        """
        Evaluates stopping criterion at stage k in {1, 2, 3}.
        Returns (stop_flag, confidence, entropy).
        """
        confidence = float(max(p_k, 1.0 - p_k))
        entropy = float(compute_entropy(np.array([p_k]))[0])

        if stage >= 4:
            return True, confidence, entropy

        tau_k = self.get_threshold(stage)

        # Cost delta to advance to next stage
        next_stage_cost = STAGE_COSTS[f"stage_{stage + 1}"]

        # Expected error reduction: remaining risk is (1 - confidence)
        expected_error_delta = float(1.0 - confidence)

        # Condition: high confidence AND incremental cost outweighs expected accuracy gain
        cost_hurdle = self.lambda_penalty * expected_error_delta
        condition_met = (confidence >= tau_k) and (next_stage_cost > cost_hurdle)

        return condition_met, confidence, entropy

    def evaluate_batch(
        self,
        stage_probs: Dict[int, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Simulates progressive acquisition on a batch of samples where stage_probs has keys 1, 2, 3, 4.
        Returns final predictions, stopped stages, costs, confidences, and early-stop ratios.
        """
        n_samples = len(stage_probs[1])
        stopped_stage = np.zeros(n_samples, dtype=int)
        final_probs = np.zeros(n_samples, dtype=float)
        final_confs = np.zeros(n_samples, dtype=float)
        total_costs = np.zeros(n_samples, dtype=float)

        for i in range(n_samples):
            stop = False
            for k in [1, 2, 3]:
                pk = stage_probs[k][i]
                should_halt, conf, _ = self.should_stop(k, pk)
                if should_halt:
                    stopped_stage[i] = k
                    final_probs[i] = pk
                    final_confs[i] = conf
                    total_costs[i] = CUMULATIVE_STAGE_COSTS[k]
                    stop = True
                    break

            if not stop:
                # Reached stage 4
                stopped_stage[i] = 4
                p4 = stage_probs[4][i]
                final_probs[i] = p4
                final_confs[i] = max(p4, 1.0 - p4)
                total_costs[i] = CUMULATIVE_STAGE_COSTS[4]

        # Early stop distributions
        counts = {k: int(np.sum(stopped_stage == k)) for k in [1, 2, 3, 4]}
        pcts = {k: float(round(counts[k] / n_samples * 100, 2)) for k in [1, 2, 3, 4]}

        return {
            "stopped_stage": stopped_stage,
            "final_probs": final_probs,
            "final_confs": final_confs,
            "total_costs": total_costs,
            "mean_cost_sec": float(round(np.mean(total_costs), 3)),
            "early_stop_counts": counts,
            "early_stop_percentages": pcts
        }

    def optimize_on_val(
        self,
        val_stage_probs: Dict[int, np.ndarray],
        y_val: np.ndarray,
        cost_weight: float = 0.05
    ):
        """
        Optimizes tau_1, tau_2, tau_3, and lambda on HISTORICAL_VAL using grid-search ROC optimization.
        Frezes thresholds once optimized.
        """
        assert not self.is_frozen, "Controller is already frozen!"

        best_score = -float("inf")
        best_params = (self.tau_1, self.tau_2, self.tau_3, self.lambda_penalty)

        tau_candidates = [0.80, 0.85, 0.90, 0.94]
        lambda_candidates = [8.0, 12.0, 16.0, 24.0]

        for t1 in tau_candidates:
            for t2 in [t for t in tau_candidates if t <= t1]:
                for t3 in [0.75, 0.80, 0.85]:
                    for lam in lambda_candidates:
                        self.tau_1 = t1
                        self.tau_2 = t2
                        self.tau_3 = t3
                        self.lambda_penalty = lam

                        res = self.evaluate_batch(val_stage_probs)
                        preds = (res["final_probs"] >= 0.5).astype(int)

                        # Compute macro F1
                        f1 = compute_macro_f1(y_val, preds)
                        # Normalize cost (relative to stage 4 max 9.31s)
                        norm_cost = res["mean_cost_sec"] / 9.31

                        # Objective: high accuracy with low acquisition cost
                        utility = f1 - (cost_weight * norm_cost)

                        if utility > best_score:
                            best_score = utility
                            best_params = (t1, t2, t3, lam)

        self.tau_1, self.tau_2, self.tau_3, self.lambda_penalty = best_params
        self.is_frozen = True
        return {
            "tau_1": self.tau_1,
            "tau_2": self.tau_2,
            "tau_3": self.tau_3,
            "lambda_penalty": self.lambda_penalty,
            "best_val_utility": round(best_score, 4)
        }

    def save(self, filepath: Optional[str] = None):
        path = filepath or os.path.join(MODEL_DIR, "stopping_controller_params.json")
        data = {
            "tau_1": self.tau_1,
            "tau_2": self.tau_2,
            "tau_3": self.tau_3,
            "lambda_penalty": self.lambda_penalty,
            "is_frozen": self.is_frozen
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        instance = cls(
            tau_1=data["tau_1"],
            tau_2=data["tau_2"],
            tau_3=data["tau_3"],
            lambda_penalty=data["lambda_penalty"]
        )
        instance.is_frozen = data.get("is_frozen", True)
        return instance

def compute_macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    from sklearn.metrics import f1_score
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))
