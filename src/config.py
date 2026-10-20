"""
Configuration and Constants for Predatory Journal Detection Framework
"""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DIR = os.path.join(ROOT_DIR, "audit")
AUDIT_DATA_DIR = os.path.join(AUDIT_DIR, "data")
AUDIT_SPLITS_DIR = os.path.join(AUDIT_DIR, "splits")
CACHE_DIR = os.path.join(ROOT_DIR, "data_cache")

# Dataset files
FROZEN_DATASET_PATH = os.path.join(AUDIT_DATA_DIR, "final_combined_journal_dataset_frozen_readonly.csv")
HISTORICAL_TRAIN_PATH = os.path.join(AUDIT_SPLITS_DIR, "historical_train.csv")
HISTORICAL_VAL_PATH = os.path.join(AUDIT_SPLITS_DIR, "historical_val.csv")
TEMPORAL_TEST_PATH = os.path.join(AUDIT_SPLITS_DIR, "temporal_test_cohort_untouched.csv")
QUARANTINED_PATH = os.path.join(AUDIT_SPLITS_DIR, "audited_uncertain_records.csv")
MANIFEST_PATH = os.path.join(AUDIT_SPLITS_DIR, "evaluation_splits_manifest.csv")

# Feature Cache
FEATURE_CACHE_PATH = os.path.join(CACHE_DIR, "features_cache.db")

# Model artifacts
MODEL_DIR = os.path.join(ROOT_DIR, "artifacts", "models")
REPORTS_DIR = os.path.join(ROOT_DIR, "artifacts", "reports")

# Random seed
RANDOM_SEED = 42

# Stage costs (wall-clock seconds estimate according to specification)
STAGE_COSTS = {
    "stage_1": 0.01,  # Group A: URL & Domain Geometry
    "stage_2": 0.80,  # Group B: HTML Structure & Policies
    "stage_3": 3.50,  # Group C: JS & Dynamic Behavior
    "stage_4": 5.00   # Group D: External Scholarly Registries
}

# Cumulative costs
CUMULATIVE_STAGE_COSTS = {
    1: 0.01,
    2: 0.81,
    3: 4.31,
    4: 9.31
}

# Feature groups definitions
FEATURE_GROUPS = {
    "group_a": [
        "url_length", "domain_length", "path_length", "dot_count", "hyphen_count",
        "numeric_ratio", "symbol_ratio", "shannon_entropy", "is_https",
        "is_academic_tld", "is_suspicious_tld", "is_generic_tld", "subdomain_count",
        "path_depth", "digits_in_domain", "has_ip_in_url"
    ],
    "group_b": [
        "http_status_ok", "download_latency_sec", "dom_node_depth",
        "has_editorial_board_link", "editorial_board_depth", "has_peer_review_policy",
        "has_apc_disclosure", "apc_cost_extracted", "has_cope_declaration",
        "is_institutional_email", "is_freemail_contact", "copyright_age_delta",
        "text_to_html_ratio"
    ],
    "group_c": [
        "script_tag_count", "third_party_script_ratio", "has_ad_or_crypto_tracker",
        "raw_vs_rendered_word_delta", "redirect_count", "has_obfuscated_js"
    ],
    "group_d": [
        "is_issn_portal_verified", "has_crossref_prefix", "annual_pub_volume_variance",
        "mean_citation_velocity", "is_doaj_indexed", "scopus_wos_claim_verified",
        "editorial_board_academic_match_score"
    ]
}

# FreeMail domains for predatory heuristic detection
FREE_MAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "yandex.com",
    "mail.ru", "163.com", "rediffmail.com", "protonmail.com"
}

# Suspicious TLDs frequently abused by predatory operations
SUSPICIOUS_TLDS = {
    "top", "xyz", "club", "online", "vip", "icu", "click", "rest", "buzz", "site", "space", "fun"
}

# Academic TLDs
ACADEMIC_TLDS = {
    "edu", "ac.uk", "edu.cn", "edu.in", "ac.in", "edu.au", "ac.jp", "edu.br", "edu.ng", "ac.id"
}

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
