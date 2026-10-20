"""
Deterministic Evidence Grounding & Fact Verification Engine
Verifies claims across extracted website signals and authoritative scholarly registries.
"""

from typing import Dict, Any, List, Tuple

class EvidenceGroundingEngine:
    def verify(
        self,
        features_a: Dict[str, Any],
        features_b: Dict[str, Any],
        features_c: Dict[str, Any],
        features_d: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Tuple[List[str], List[str], bool]:
        """
        Cross-checks website claims against scholarly registries.
        Returns:
          (corroborated_facts, unverified_or_contradicted_claims, has_severe_contradiction)
        """
        corroborated = []
        contradicted = []
        has_severe_contradiction = False

        # 1. TLD / Institutional domain check
        if features_a.get("is_academic_tld", 0) > 0:
            corroborated.append("Journal domain is hosted on an accredited educational/academic TLD.")
        elif features_a.get("is_suspicious_tld", 0) > 0:
            contradicted.append("Journal domain utilizes a high-risk commercial TLD commonly associated with disposable web operations.")

        # 2. Editorial board verification
        if features_b.get("has_editorial_board_link", 0) > 0:
            if features_d.get("editorial_board_academic_match_score", 0) >= 0.70:
                corroborated.append("Editorial board page identified with verified institutional faculty affiliations.")
            else:
                contradicted.append("Editorial board links listed on website could not be corroborated with verified institutional profiles.")
        else:
            contradicted.append("No dedicated editorial board or governance page accessible within two link hops.")

        # 3. Peer-review & COPE adherence
        has_cope_claim = features_b.get("has_cope_declaration", 0) > 0
        if has_cope_claim:
            if features_d.get("is_doaj_indexed", 0) > 0 or features_d.get("scopus_wos_claim_verified", 0) > 0:
                corroborated.append("Publication ethics statement and COPE adherence confirmed with indexed registry status.")
            else:
                contradicted.append("Website claims COPE adherence, but journal lacks official DOAJ or Scopus ethics indexing.")

        # 4. Contact email verification
        if features_b.get("is_freemail_contact", 0) > 0:
            contradicted.append("Editorial contact uses generic commercial freemail (Gmail/Yahoo) instead of institutional domain.")
            has_severe_contradiction = True
        elif features_b.get("is_institutional_email", 0) > 0:
            corroborated.append("Official editorial contact routed through institutional email domain.")

        # 5. Registry corroboration (DOAJ, Crossref, ISSN)
        if features_d.get("is_doaj_indexed", 0) > 0:
            corroborated.append("Inaugural indexing confirmed in Directory of Open Access Journals (DOAJ).")
        if features_d.get("has_crossref_prefix", 0) > 0:
            corroborated.append("Active Crossref DOI prefix with verifiable publication deposit volume.")
        else:
            contradicted.append("No active Crossref DOI deposit history verified for journal serial.")

        # 6. Ad networks / miners
        if features_c.get("has_ad_or_crypto_tracker", 0) > 0:
            contradicted.append("Client-side execution detected third-party commercial ad networks or tracker monetization scripts.")
            has_severe_contradiction = True

        return corroborated, contradicted, has_severe_contradiction
