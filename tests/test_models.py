"""
Unit Tests for Baselines, Multi-Head Network, and Calibration
"""

import unittest
import numpy as np
import torch
from src.models.baselines import IndependentStageBaselines
from src.models.multi_head_model import ProgressiveMultiHeadNet, MultiHeadModelTrainer
from src.models.calibration import StageCalibrator, compute_ece, compute_entropy

class TestModels(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        torch.manual_seed(42)
        self.n_samples = 100
        self.X_dict = {
            "X_a": np.random.randn(self.n_samples, 16).astype(np.float32),
            "X_b": np.random.randn(self.n_samples, 13).astype(np.float32),
            "X_c": np.random.randn(self.n_samples, 6).astype(np.float32),
            "X_d": np.random.randn(self.n_samples, 7).astype(np.float32)
        }
        self.X_dict["X_stage1"] = self.X_dict["X_a"]
        self.X_dict["X_stage2"] = np.concatenate([self.X_dict["X_a"], self.X_dict["X_b"]], axis=1)
        self.X_dict["X_stage3"] = np.concatenate([self.X_dict["X_stage2"], self.X_dict["X_c"]], axis=1)
        self.X_dict["X_stage4"] = np.concatenate([self.X_dict["X_stage3"], self.X_dict["X_d"]], axis=1)

        self.y = np.random.randint(0, 2, size=self.n_samples)

    def test_multi_head_forward(self):
        net = ProgressiveMultiHeadNet()
        t_a = torch.tensor(self.X_dict["X_a"])
        t_b = torch.tensor(self.X_dict["X_b"])
        t_c = torch.tensor(self.X_dict["X_c"])
        t_d = torch.tensor(self.X_dict["X_d"])

        # Stage 1 only
        out1 = net(t_a)
        self.assertIn("p_1", out1)
        self.assertNotIn("p_2", out1)

        # Full forward
        out4 = net(t_a, t_b, t_c, t_d)
        self.assertIn("p_1", out4)
        self.assertIn("p_2", out4)
        self.assertIn("p_3", out4)
        self.assertIn("p_4", out4)
        self.assertEqual(out4["p_4"].shape[0], self.n_samples)

    def test_trainer_and_predict(self):
        trainer = MultiHeadModelTrainer(device="cpu")
        loss = trainer.train_network(
            self.X_dict, self.y, self.X_dict, self.y,
            epochs=2, batch_size=32
        )
        self.assertIsInstance(loss, float)

        probs_stage1 = trainer.predict_stage_proba(self.X_dict, stage=1)
        self.assertEqual(len(probs_stage1), self.n_samples)
        self.assertTrue(np.all((probs_stage1 >= 0.0) & (probs_stage1 <= 1.0)))

    def test_baselines(self):
        rf = IndependentStageBaselines(model_type="rf")
        rf.fit(self.X_dict, self.y)
        p1 = rf.predict_proba_stage(self.X_dict["X_stage1"], stage_num=1)
        self.assertEqual(p1.shape, (self.n_samples, 2))

    def test_calibration(self):
        probs = np.random.uniform(0.1, 0.9, size=self.n_samples)
        ece, diag = compute_ece(self.y, probs, n_bins=10)
        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)
        self.assertEqual(len(diag["bin_boundaries"]), 11)

if __name__ == "__main__":
    unittest.main()
