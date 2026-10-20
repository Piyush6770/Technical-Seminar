"""
Unified Multi-Stage Feature Extraction Pipeline
Supports single-journal live extraction and high-throughput batch extraction.
"""

import time
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd

from src.config import FEATURE_GROUPS
from src.features.group_a_url import GroupAUrlExtractor
from src.features.group_b_html import GroupBHtmlExtractor
from src.features.group_c_dynamic import GroupCDynamicExtractor
from src.features.group_d_scholarly import GroupDScholarlyExtractor

class FeaturePipeline:
    def __init__(self, use_cache: bool = True):
        self.extractor_a = GroupAUrlExtractor(use_cache=use_cache)
        self.extractor_b = GroupBHtmlExtractor(use_cache=use_cache)
        self.extractor_c = GroupCDynamicExtractor(use_cache=use_cache)
        self.extractor_d = GroupDScholarlyExtractor(use_cache=use_cache)

        self.names_a = FEATURE_GROUPS["group_a"]
        self.names_b = FEATURE_GROUPS["group_b"]
        self.names_c = FEATURE_GROUPS["group_c"]
        self.names_d = FEATURE_GROUPS["group_d"]

    def extract_single(
        self,
        url: Optional[str],
        journal_name: Optional[str] = None,
        issn: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        up_to_stage: int = 4,
        live: bool = True
    ) -> Dict[str, Any]:
        """
        Extracts features progressively up to stage k in {1, 2, 3, 4}.
        Returns dict containing feature arrays, raw dicts, and timings per stage.
        """
        meta = metadata.copy() if metadata else {}
        if journal_name:
            meta["journal_name"] = journal_name

        results = {
            "features_a": {},
            "features_b": {},
            "features_c": {},
            "features_d": {},
            "latencies": {},
            "vector_a": None,
            "vector_b": None,
            "vector_c": None,
            "vector_d": None,
            "vector_cumulative": None
        }

        # Stage 1: Group A
        t0 = time.perf_counter()
        feat_a = self.extractor_a.extract(url, journal_name)
        results["latencies"]["stage_1"] = time.perf_counter() - t0
        results["features_a"] = feat_a
        results["vector_a"] = np.array([feat_a.get(k, 0.0) for k in self.names_a], dtype=np.float32)

        if up_to_stage >= 2:
            # Stage 2: Group B
            t0 = time.perf_counter()
            feat_b = self.extractor_b.extract(url, meta, live=live)
            results["latencies"]["stage_2"] = time.perf_counter() - t0
            results["features_b"] = feat_b
            results["vector_b"] = np.array([feat_b.get(k, 0.0) for k in self.names_b], dtype=np.float32)

        if up_to_stage >= 3:
            # Stage 3: Group C
            t0 = time.perf_counter()
            feat_c = self.extractor_c.extract(url, meta, live=live)
            results["latencies"]["stage_3"] = time.perf_counter() - t0
            results["features_c"] = feat_c
            results["vector_c"] = np.array([feat_c.get(k, 0.0) for k in self.names_c], dtype=np.float32)

        if up_to_stage >= 4:
            # Stage 4: Group D
            t0 = time.perf_counter()
            feat_d = self.extractor_d.extract(journal_name or "", issn, meta, live=live)
            results["latencies"]["stage_4"] = time.perf_counter() - t0
            results["features_d"] = feat_d
            results["vector_d"] = np.array([feat_d.get(k, 0.0) for k in self.names_d], dtype=np.float32)

        # Assemble cumulative vector
        vec_parts = [results["vector_a"]]
        if results["vector_b"] is not None:
            vec_parts.append(results["vector_b"])
        if results["vector_c"] is not None:
            vec_parts.append(results["vector_c"])
        if results["vector_d"] is not None:
            vec_parts.append(results["vector_d"])

        results["vector_cumulative"] = np.concatenate(vec_parts)
        return results

    def extract_dataframe(self, df: pd.DataFrame, up_to_stage: int = 4, live: bool = False) -> Dict[str, np.ndarray]:
        """
        Extracts features for all rows in a DataFrame.
        Returns dictionary of numpy arrays:
          'X_a': (N, 16), 'X_b': (N, 13), 'X_c': (N, 6), 'X_d': (N, 7)
          'X_stage1', 'X_stage2', 'X_stage3', 'X_stage4'
        """
        list_a, list_b, list_c, list_d = [], [], [], []

        for _, row in df.iterrows():
            meta = row.to_dict()
            url = row.get("url")
            name = row.get("journal_name")

            # Group A
            fa = self.extractor_a.extract(url, name)
            va = [fa.get(k, 0.0) for k in self.names_a]
            list_a.append(va)

            if up_to_stage >= 2:
                fb = self.extractor_b.extract(url, meta, live=live)
                vb = [fb.get(k, 0.0) for k in self.names_b]
                list_b.append(vb)

            if up_to_stage >= 3:
                fc = self.extractor_c.extract(url, meta, live=live)
                vc = [fc.get(k, 0.0) for k in self.names_c]
                list_c.append(vc)

            if up_to_stage >= 4:
                fd = self.extractor_d.extract(name, None, meta, live=live)
                vd = [fd.get(k, 0.0) for k in self.names_d]
                list_d.append(vd)

        X_a = np.array(list_a, dtype=np.float32)
        X_b = np.array(list_b, dtype=np.float32) if list_b else None
        X_c = np.array(list_c, dtype=np.float32) if list_c else None
        X_d = np.array(list_d, dtype=np.float32) if list_d else None

        res = {"X_a": X_a, "X_b": X_b, "X_c": X_c, "X_d": X_d}
        res["X_stage1"] = X_a
        if X_b is not None:
            res["X_stage2"] = np.concatenate([X_a, X_b], axis=1)
        if X_c is not None:
            res["X_stage3"] = np.concatenate([X_a, X_b, X_c], axis=1)
        if X_d is not None:
            res["X_stage4"] = np.concatenate([X_a, X_b, X_c, X_d], axis=1)

        return res
