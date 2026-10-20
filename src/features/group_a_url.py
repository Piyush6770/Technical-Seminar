"""
Group A: Inexpensive URL & Domain Geometry Extractor
Latency: < 0.01s (Pure local string & geometry computation)
"""

import math
import re
from urllib.parse import urlparse
import tldextract
from typing import Dict, Any, Optional
from src.config import SUSPICIOUS_TLDS, ACADEMIC_TLDS
from src.features.cache import default_cache

def calculate_shannon_entropy(s: str) -> float:
    """Computes Shannon entropy of string s."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)

class GroupAUrlExtractor:
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.tld_extractor = tldextract.TLDExtract()

    def extract(self, url: Optional[str], journal_name: Optional[str] = None) -> Dict[str, float]:
        """
        Extracts 16 geometrical and lexical domain signals.
        """
        if not url or pd_is_na(url):
            # Fallback representation for missing URL
            # Synthesize minimal representative features or baseline neutral vector
            return self._fallback_features(journal_name)

        clean_url = str(url).strip()
        if not clean_url.startswith(("http://", "https://")):
            clean_url = "http://" + clean_url

        cache_key = default_cache.generate_key(clean_url, journal_name or "", "group_a")
        if self.use_cache:
            cached = default_cache.get(cache_key)
            if cached:
                return cached

        parsed = urlparse(clean_url)
        extracted_tld = self.tld_extractor(clean_url)

        domain = extracted_tld.domain
        suffix = extracted_tld.suffix.lower()
        subdomain = extracted_tld.subdomain
        fqdn = f"{domain}.{suffix}" if suffix else domain

        path = parsed.path or ""
        url_len = len(clean_url)
        domain_len = len(fqdn)
        path_len = len(path)

        dot_count = clean_url.count(".")
        hyphen_count = clean_url.count("-")

        # Lexical ratios
        num_digits = sum(c.isdigit() for c in clean_url)
        numeric_ratio = num_digits / max(1, url_len)

        symbols = sum(not c.isalnum() for c in clean_url)
        symbol_ratio = symbols / max(1, url_len)

        entropy = calculate_shannon_entropy(clean_url)

        # HTTPS flag
        is_https = 1.0 if parsed.scheme.lower() == "https" else 0.0

        # TLD classification
        is_academic_tld = 1.0 if any(suffix.endswith(acad) or suffix == acad for acad in ACADEMIC_TLDS) else 0.0
        is_suspicious_tld = 1.0 if suffix in SUSPICIOUS_TLDS else 0.0
        is_generic_tld = 1.0 if (not is_academic_tld and not is_suspicious_tld) else 0.0

        subdomain_count = len(subdomain.split(".")) if subdomain else 0
        path_depth = len([segment for segment in path.split("/") if segment])

        digits_in_domain = sum(c.isdigit() for c in fqdn)

        # IPv4 pattern match
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        has_ip_in_url = 1.0 if re.match(ip_pattern, parsed.netloc.split(":")[0]) else 0.0

        features = {
            "url_length": float(url_len),
            "domain_length": float(domain_len),
            "path_length": float(path_len),
            "dot_count": float(dot_count),
            "hyphen_count": float(hyphen_count),
            "numeric_ratio": float(numeric_ratio),
            "symbol_ratio": float(symbol_ratio),
            "shannon_entropy": float(entropy),
            "is_https": float(is_https),
            "is_academic_tld": float(is_academic_tld),
            "is_suspicious_tld": float(is_suspicious_tld),
            "is_generic_tld": float(is_generic_tld),
            "subdomain_count": float(subdomain_count),
            "path_depth": float(path_depth),
            "digits_in_domain": float(digits_in_domain),
            "has_ip_in_url": float(has_ip_in_url)
        }

        if self.use_cache:
            default_cache.set(cache_key, "group_a", features)

        return features

    def _fallback_features(self, journal_name: Optional[str]) -> Dict[str, float]:
        """Provides neutral/expected features when journal lacks explicit URL."""
        name_len = len(str(journal_name or ""))
        return {
            "url_length": float(name_len + 15),
            "domain_length": float(name_len * 0.6),
            "path_length": 0.0,
            "dot_count": 2.0,
            "hyphen_count": 1.0,
            "numeric_ratio": 0.0,
            "symbol_ratio": 0.15,
            "shannon_entropy": 3.8,
            "is_https": 0.0,
            "is_academic_tld": 0.0,
            "is_suspicious_tld": 0.0,
            "is_generic_tld": 1.0,
            "subdomain_count": 1.0,
            "path_depth": 0.0,
            "digits_in_domain": 0.0,
            "has_ip_in_url": 0.0
        }

def pd_is_na(val):
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    if str(val).strip().lower() in ("nan", "none", "", "-"):
        return True
    return False
