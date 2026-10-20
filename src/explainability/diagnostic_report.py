"""
Diagnostic Report Generator
Generates structured JSON artifacts strictly following Section 6 specification,
plus comprehensive human-readable executive summaries.
"""

import json
from typing import Dict, Any, List, Optional
from src.config import CUMULATIVE_STAGE_COSTS

class DiagnosticReportGenerator:
    STAGE_NAMES = {
        1: "Stage 1 (Group A: URL Geometry)",
        2: "Stage 2 (Groups A + B: HTML & Policies)",
        3: "Stage 3 (Groups A + B + C: Dynamic Behavior)",
        4: "Stage 4 (Groups A + B + C + D: Full Registries)"
    }

    GROUP_LABELS = {
        1: ["Group A"],
        2: ["Group A", "Group B"],
        3: ["Group A", "Group B", "Group C"],
        4: ["Group A", "Group B", "Group C", "Group D"]
    }

    ALL_GROUPS = ["Group A", "Group B", "Group C", "Group D"]

    def generate_json_artifact(
        self,
        query_input: str,
        canonical_title: str,
        issn_l: Optional[str],
        identity_status: str,
        verification_source: str,
        stopping_stage: int,
        calibrated_risk_prob: float,
        corroborated_facts: List[str],
        contradicted_claims: List[str],
        has_severe_contradiction: bool,
        acquisition_time_sec: float
    ) -> Dict[str, Any]:
        """
        Creates machine-readable JSON report conforming exactly to Section 6 schema.
        """
        prob = float(round(calibrated_risk_prob, 3))
        confidence = float(round(max(prob, 1.0 - prob) * 100, 1))

        # Risk classification
        if prob >= 0.60:
            classification = "Predatory / Deceptive"
        elif prob <= 0.40:
            classification = "Legitimate / Credible"
        else:
            classification = "Ambiguous / Inconclusive Risk"

        # Abstention decision
        # Prompt: "If risk probability is between 0.40 and 0.60 or if evidence from registries
        # directly contradicts extracted website content, the system must explicitly output
        # abstention_status: 'REQUIRES_HUMAN_EXPERT_REVIEW'."
        if (0.40 <= prob <= 0.60) or has_severe_contradiction:
            abstention_status = "REQUIRES_HUMAN_EXPERT_REVIEW"
        else:
            abstention_status = "DECISION_FINAL"

        acquired_groups = self.GROUP_LABELS.get(stopping_stage, ["Group A"])
        skipped_groups = [g for g in self.ALL_GROUPS if g not in acquired_groups]

        report = {
            "journal_identity": {
                "query_input": query_input or "N/A",
                "canonical_title": canonical_title or "Unverified Serial",
                "issn_l": issn_l or "N/A",
                "identity_status": identity_status or "IDENTITY_VERIFIED",
                "verification_source": verification_source or "OpenAlex Serial Registry"
            },
            "progressive_assessment": {
                "stopping_stage": self.STAGE_NAMES.get(stopping_stage, f"Stage {stopping_stage}"),
                "calibrated_risk_probability": prob,
                "confidence_level": f"High ({confidence}%)" if confidence >= 80 else f"Moderate ({confidence}%)",
                "risk_classification": classification,
                "feature_groups_acquired": acquired_groups,
                "groups_skipped_due_to_confidence": skipped_groups,
                "total_acquisition_time_sec": float(round(acquisition_time_sec, 2))
            },
            "evidence_grounding": {
                "corroborated_facts": corroborated_facts,
                "unverified_or_contradicted_claims": contradicted_claims,
                "abstention_status": abstention_status
            }
        }
        return report

    def format_markdown_summary(self, report: Dict[str, Any]) -> str:
        ident = report["journal_identity"]
        prog = report["progressive_assessment"]
        ev = report["evidence_grounding"]

        md = f"""# Scholarly Integrity Diagnostic Audit

### Journal Identity
- **Title**: {ident['canonical_title']}
- **Query URL**: `{ident['query_input']}`
- **ISSN**: `{ident['issn_l']}`
- **Identity Status**: `{ident['identity_status']}` (Source: {ident['verification_source']})

---

### Progressive Assessment
- **Stopping Controller Action**: **{prog['stopping_stage']}**
- **Calibrated Predatory Risk**: `{prog['calibrated_risk_probability']:.1%}`
- **Confidence Level**: **{prog['confidence_level']}**
- **Risk Classification**: **{prog['risk_classification']}**
- **Feature Groups Acquired**: {', '.join(prog['feature_groups_acquired'])}
- **Feature Groups Skipped**: {', '.join(prog['groups_skipped_due_to_confidence']) or 'None (Full Acquisition)'}
- **Total Acquisition Latency**: `{prog['total_acquisition_time_sec']:.2f}s`

---

### Evidence Grounding & Provenance
- **Abstention Status**: `{ev['abstention_status']}`

**Corroborated Facts**:
"""
        if ev["corroborated_facts"]:
            for f in ev["corroborated_facts"]:
                md += f"- [x] {f}\n"
        else:
            md += "- None verified.\n"

        md += "\n**Unverified or Contradicted Claims**:\n"
        if ev["unverified_or_contradicted_claims"]:
            for c in ev["unverified_or_contradicted_claims"]:
                md += f"- [!] {c}\n"
        else:
            md += "- No registry contradictions detected.\n"

        return md
