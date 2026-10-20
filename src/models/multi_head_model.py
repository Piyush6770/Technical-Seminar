"""
Progressive Shared Multi-Head Neural Network Architecture
Implements sequential progressive feature representations phi_1 to phi_4 with prediction heads.
"""

import os
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Tuple, List, Optional
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_SEED, MODEL_DIR

torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

class ProgressiveMultiHeadNet(nn.Module):
    def __init__(
        self,
        dim_a: int = 16,
        dim_b: int = 13,
        dim_c: int = 6,
        dim_d: int = 7,
        hidden_dim: int = 64
    ):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Stage 1 Encoder: x_A -> h_1
        self.encoder_1 = nn.Sequential(
            nn.Linear(dim_a, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.15)
        )
        self.head_1 = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

        # Stage 2 Encoder: [h_1, x_B] -> h_2
        self.encoder_2 = nn.Sequential(
            nn.Linear(hidden_dim + dim_b, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.15)
        )
        self.head_2 = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

        # Stage 3 Encoder: [h_2, x_C] -> h_3
        self.encoder_3 = nn.Sequential(
            nn.Linear(hidden_dim + dim_c, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.15)
        )
        self.head_3 = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

        # Stage 4 Encoder: [h_3, x_D] -> h_4
        self.encoder_4 = nn.Sequential(
            nn.Linear(hidden_dim + dim_d, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.15)
        )
        self.head_4 = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

    def forward(
        self,
        x_a: torch.Tensor,
        x_b: Optional[torch.Tensor] = None,
        x_c: Optional[torch.Tensor] = None,
        x_d: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward evaluation. Can evaluate up to whatever stage features are provided.
        Returns dict with logits 'logit_1', 'logit_2', 'logit_3', 'logit_4' and probabilities.
        """
        outputs = {}

        # Stage 1
        h1 = self.encoder_1(x_a)
        l1 = self.head_1(h1).squeeze(-1)
        outputs["logit_1"] = l1
        outputs["p_1"] = torch.sigmoid(l1)

        if x_b is not None:
            # Stage 2
            cat_2 = torch.cat([h1, x_b], dim=-1)
            h2 = self.encoder_2(cat_2)
            l2 = self.head_2(h2).squeeze(-1)
            outputs["logit_2"] = l2
            outputs["p_2"] = torch.sigmoid(l2)

            if x_c is not None:
                # Stage 3
                cat_3 = torch.cat([h2, x_c], dim=-1)
                h3 = self.encoder_3(cat_3)
                l3 = self.head_3(h3).squeeze(-1)
                outputs["logit_3"] = l3
                outputs["p_3"] = torch.sigmoid(l3)

                if x_d is not None:
                    # Stage 4
                    cat_4 = torch.cat([h3, x_d], dim=-1)
                    h4 = self.encoder_4(cat_4)
                    l4 = self.head_4(h4).squeeze(-1)
                    outputs["logit_4"] = l4
                    outputs["p_4"] = torch.sigmoid(l4)

        return outputs

class MultiHeadModelTrainer:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = ProgressiveMultiHeadNet().to(self.device)
        self.scalers = {
            "a": StandardScaler(),
            "b": StandardScaler(),
            "c": StandardScaler(),
            "d": StandardScaler()
        }

    def fit_scalers(self, X_dict: Dict[str, np.ndarray]):
        for key in ["a", "b", "c", "d"]:
            self.scalers[key].fit(X_dict[f"X_{key}"])

    def transform(self, X_dict: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        res = {}
        for key in ["a", "b", "c", "d"]:
            if X_dict.get(f"X_{key}") is not None:
                res[f"X_{key}"] = self.scalers[key].transform(X_dict[f"X_{key}"])
            else:
                res[f"X_{key}"] = None
        return res

    def train_network(
        self,
        X_train_dict: Dict[str, np.ndarray],
        y_train: np.ndarray,
        X_val_dict: Dict[str, np.ndarray],
        y_val: np.ndarray,
        epochs: int = 60,
        batch_size: int = 32,
        lr: float = 1e-3,
        weight_decay: float = 1e-4
    ):
        # 1. Fit scalers on train set
        self.fit_scalers(X_train_dict)
        Xt = self.transform(X_train_dict)
        Xv = self.transform(X_val_dict)

        # 2. Setup DataLoaders
        t_a = torch.tensor(Xt["X_a"], dtype=torch.float32)
        t_b = torch.tensor(Xt["X_b"], dtype=torch.float32)
        t_c = torch.tensor(Xt["X_c"], dtype=torch.float32)
        t_d = torch.tensor(Xt["X_d"], dtype=torch.float32)
        t_y = torch.tensor(y_train, dtype=torch.float32)

        v_a = torch.tensor(Xv["X_a"], dtype=torch.float32).to(self.device)
        v_b = torch.tensor(Xv["X_b"], dtype=torch.float32).to(self.device)
        v_c = torch.tensor(Xv["X_c"], dtype=torch.float32).to(self.device)
        v_d = torch.tensor(Xv["X_d"], dtype=torch.float32).to(self.device)
        v_y = torch.tensor(y_val, dtype=torch.float32).to(self.device)

        dataset = TensorDataset(t_a, t_b, t_c, t_d, t_y)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        criterion = nn.BCEWithLogitsLoss()

        best_val_loss = float("inf")
        best_state = None

        self.model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            for batch_a, batch_b, batch_c, batch_d, batch_y in loader:
                batch_a = batch_a.to(self.device)
                batch_b = batch_b.to(self.device)
                batch_c = batch_c.to(self.device)
                batch_d = batch_d.to(self.device)
                batch_y = batch_y.to(self.device)

                optimizer.zero_grad()
                out = self.model(batch_a, batch_b, batch_c, batch_d)

                # Progressive multi-head joint loss
                loss1 = criterion(out["logit_1"], batch_y)
                loss2 = criterion(out["logit_2"], batch_y)
                loss3 = criterion(out["logit_3"], batch_y)
                loss4 = criterion(out["logit_4"], batch_y)

                # We weight all active heads
                loss = 0.2 * loss1 + 0.25 * loss2 + 0.25 * loss3 + 0.3 * loss4
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            # Validation evaluation
            self.model.eval()
            with torch.no_grad():
                vout = self.model(v_a, v_b, v_c, v_d)
                vloss = (
                    0.2 * criterion(vout["logit_1"], v_y) +
                    0.25 * criterion(vout["logit_2"], v_y) +
                    0.25 * criterion(vout["logit_3"], v_y) +
                    0.3 * criterion(vout["logit_4"], v_y)
                ).item()

            if vloss < best_val_loss:
                best_val_loss = vloss
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            self.model.train()

        if best_state is not None:
            self.model.load_state_dict(best_state)
        self.model.eval()
        return best_val_loss

    def predict_stage_proba(self, X_dict: Dict[str, np.ndarray], stage: int) -> np.ndarray:
        """
        Inference at a given stage (1, 2, 3, or 4).
        """
        self.model.eval()
        Xt = self.transform(X_dict)
        with torch.no_grad():
            ta = torch.tensor(Xt["X_a"], dtype=torch.float32).to(self.device)
            tb = torch.tensor(Xt["X_b"], dtype=torch.float32).to(self.device) if stage >= 2 else None
            tc = torch.tensor(Xt["X_c"], dtype=torch.float32).to(self.device) if stage >= 3 else None
            td = torch.tensor(Xt["X_d"], dtype=torch.float32).to(self.device) if stage >= 4 else None

            out = self.model(ta, tb, tc, td)
            probs = out[f"p_{stage}"].cpu().numpy()
        return probs

    def save(self, filepath: Optional[str] = None):
        path = filepath or os.path.join(MODEL_DIR, "progressive_multi_head.pt")
        scalers_path = path.replace(".pt", "_scalers.joblib")
        torch.save(self.model.state_dict(), path)
        joblib.dump(self.scalers, scalers_path)
        return path

    @classmethod
    def load(cls, filepath: str, device: str = "cpu"):
        instance = cls(device=device)
        loaded = torch.load(filepath, map_location=instance.device, weights_only=True)
        if isinstance(loaded, dict) and "model_state" in loaded:
            instance.model.load_state_dict(loaded["model_state"])
        else:
            instance.model.load_state_dict(loaded)

        scalers_path = filepath.replace(".pt", "_scalers.joblib")
        if os.path.exists(scalers_path):
            instance.scalers = joblib.load(scalers_path)
        instance.model.eval()
        return instance
