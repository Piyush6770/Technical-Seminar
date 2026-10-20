"""
Unit Tests for Feature Extraction Modules
"""

import unittest
import numpy as np
from src.features.group_a_url import GroupAUrlExtractor
from src.features.group_b_html import GroupBHtmlExtractor
from src.features.group_c_dynamic import GroupCDynamicExtractor
from src.features.group_d_scholarly import GroupDScholarlyExtractor
from src.features.pipeline import FeaturePipeline

class TestFeatures(unittest.TestCase):
    def setUp(self):
        self.sample_url = "http://bmcanesthesiol.biomedcentral.com"
        self.sample_name = "BMC Anesthesiology"
        self.metadata = {
            "journal_name": self.sample_name,
            "url": self.sample_url,
            "sjr": "0.718",
            "quartile": "Q2",
            "apc_amount": "1370",
            "open_access": "yes",
            "h_index": "24"
        }

    def test_group_a(self):
        extractor = GroupAUrlExtractor(use_cache=False)
        feats = extractor.extract(self.sample_url, self.sample_name)
        self.assertEqual(len(feats), 16)
        self.assertIn("url_length", feats)
        self.assertIn("shannon_entropy", feats)
        self.assertGreater(feats["shannon_entropy"], 0.0)

    def test_group_b(self):
        extractor = GroupBHtmlExtractor(timeout_sec=0.5, use_cache=False)
        feats = extractor.extract(self.sample_url, self.metadata)
        self.assertEqual(len(feats), 13)
        self.assertIn("http_status_ok", feats)
        self.assertIn("apc_cost_extracted", feats)

    def test_group_c(self):
        extractor = GroupCDynamicExtractor(timeout_sec=0.5, use_cache=False)
        feats = extractor.extract(self.sample_url, self.metadata)
        self.assertEqual(len(feats), 6)
        self.assertIn("script_tag_count", feats)
        self.assertIn("third_party_script_ratio", feats)

    def test_group_d(self):
        extractor = GroupDScholarlyExtractor(timeout_sec=0.5, use_cache=False)
        feats = extractor.extract(self.sample_name, None, self.metadata)
        self.assertEqual(len(feats), 7)
        self.assertIn("is_issn_portal_verified", feats)
        self.assertIn("scopus_wos_claim_verified", feats)

    def test_pipeline(self):
        pipe = FeaturePipeline(use_cache=False)
        res = pipe.extract_single(self.sample_url, self.sample_name, None, self.metadata, up_to_stage=4)
        self.assertEqual(len(res["vector_cumulative"]), 42)
        self.assertEqual(len(res["vector_a"]), 16)
        self.assertEqual(len(res["vector_b"]), 13)
        self.assertEqual(len(res["vector_c"]), 6)
        self.assertEqual(len(res["vector_d"]), 7)

if __name__ == "__main__":
    unittest.main()
