"""
Unit Tests for Adaptive Stopping Controller and Evidence Grounding
"""

import unittest
import numpy as np
from src.models.stopping_controller import AdaptiveStoppingController
from src.explainability.evidence_grounding import EvidenceGroundingEngine
from src.explainability.diagnostic_report import DiagnosticReportGenerator

class TestStoppingAndExplainability(unittest.TestCase):
    def setUp(self):
        self.controller = AdaptiveStoppingController(tau_1=0.85, tau_2=0.80, tau_3=0.75, lambda_penalty=10.0)
        self.grounding = EvidenceGroundingEngine()
        self.reporter = DiagnosticReportGenerator()

    def test_stopping_criterion(self):
        # Stage 1 with high confidence (0.95) -> should stop
        stop_high, conf_high, ent_high = self.controller.should_stop(stage=1, p_k=0.05)
        self.assertTrue(stop_high)
        self.assertAlmostEqual(conf_high, 0.95)

        # Stage 1 with ambiguous probability (0.52) -> should NOT stop
        stop_amb, conf_amb, ent_amb = self.controller.should_stop(stage=1, p_k=0.52)
        self.assertFalse(stop_amb)
        self.assertAlmostEqual(conf_amb, 0.52)

    def test_batch_evaluation(self):
        n = 50
        stage_probs = {
            1: np.array([0.98] * 25 + [0.52] * 25),
            2: np.array([0.95] * 25 + [0.96] * 25),
            3: np.array([0.90] * 50),
            4: np.array([0.90] * 50)
        }
        res = self.controller.evaluate_batch(stage_probs)
        self.assertEqual(len(res["stopped_stage"]), n)
        # First 25 should have stopped at Stage 1
        self.assertTrue(np.all(res["stopped_stage"][:25] == 1))
        # Next 25 should have stopped at Stage 2
        self.assertTrue(np.all(res["stopped_stage"][25:] == 2))

    def test_evidence_grounding(self):
        fa = {"is_academic_tld": 1.0, "is_suspicious_tld": 0.0}
        fb = {"has_editorial_board_link": 1.0, "is_freemail_contact": 0.0, "has_cope_declaration": 1.0}
        fc = {"has_ad_or_crypto_tracker": 0.0}
        fd = {"is_doaj_indexed": 1.0, "has_crossref_prefix": 1.0, "editorial_board_academic_match_score": 0.85}
        meta = {"journal_name": "Test Legitimate Journal"}

        corrob, contrad, severe = self.grounding.verify(fa, fb, fc, fd, meta)
        self.assertGreater(len(corrob), 0)
        self.assertEqual(len(contrad), 0)
        self.assertFalse(severe)

    def test_diagnostic_report_schema(self):
        report = self.reporter.generate_json_artifact(
            query_input="http://test.org",
            canonical_title="Journal of Test",
            issn_l="1234-5678",
            identity_status="IDENTITY_VERIFIED",
            verification_source="OpenAlex",
            stopping_stage=2,
            calibrated_risk_prob=0.08,
            corroborated_facts=["Fact 1"],
            contradicted_claims=[],
            has_severe_contradiction=False,
            acquisition_time_sec=0.81
        )
        self.assertIn("journal_identity", report)
        self.assertIn("progressive_assessment", report)
        self.assertIn("evidence_grounding", report)
        self.assertEqual(report["evidence_grounding"]["abstention_status"], "DECISION_FINAL")

if __name__ == "__main__":
    unittest.main()
