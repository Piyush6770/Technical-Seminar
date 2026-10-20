"""
Independent Stage Baselines: Decoupled Random Forest and XGBoost Models
Trained independently on {A}, {A,B}, {A,B,C}, and {A,B,C,D}.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from src.config import RANDOM_SEED, MODEL_DIR

class IndependentStageBaselines:
    def __init__(self, model_type: str = "xgboost"):
        """
        model_type: 'rf' or 'xgboost'
        """
        self.model_type = model_type.lower()
        self.models: Dict[int, Any] = {}
        self.scalers: Dict[int, StandardScaler] = {}

    def _init_estimator(self):
        if self.model_type == "rf":
            return RandomForestClassifier(
                n_estimators=150,
                max_depth=8,
                min_samples_split=4,
                random_state=RANDOM_SEED,
                n_jobs=-1
            )
        else:
            return XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                eval_metric="logloss",
                random_state=RANDOM_SEED,
                n_jobs=-1
            )

    def fit(self, features_dict: Dict[str, np.ndarray], y_train: np.ndarray):
        """
        Fits 4 independent models for stage 1 (A), stage 2 (A+B), stage 3 (A+B+C), stage 4 (A+B+C+D).
        """
        stages = [
            (1, features_dict["X_stage1"]),
            (2, features_dict["X_stage2"]),
            (3, features_dict["X_stage3"]),
            (4, features_dict["X_stage4"])
        ]

        for stage_num, X in stages:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            clf = self._init_estimator()
            clf.fit(X_scaled, y_train)
            self.scalers[stage_num] = scaler
            self.models[stage_num] = clf

    def predict_proba_stage(self, X: np.ndarray, stage_num: int) -> np.ndarray:
        """
        Returns probabilities [P(y=0), P(y=1)] for a specific stage.
        """
        assert stage_num in self.models, f"Stage {stage_num} not fitted!"
        X_scaled = self.scalers[stage_num].transform(X)
        return self.models[stage_num].predict_proba(X_scaled)

    def predict_stage(self, X: np.ndarray, stage_num: int, threshold: float = 0.5) -> np.ndarray:
        proba = self.predict_proba_stage(X, stage_num)[:, 1]
        return (proba >= threshold).astype(int)

    def save(self, prefix: str = "baseline"):
        save_path = os.path.join(MODEL_DIR, f"{prefix}_{self.model_type}.joblib")
        joblib.dump({"models": self.models, "scalers": self.scalers, "type": self.model_type}, save_path)
        return save_path

    @classmethod
    def load(cls, filepath: str):
        data = joblib.load(filepath)
        instance = cls(model_type=data["type"])
        instance.models = data["models"]
        instance.scalers = data["scalers"]
        return instance
