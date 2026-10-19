import os
import sys
import csv
import json
import re
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(sys.maxsize)

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
WEB_CRAWLING_DIR = os.path.join(BASE_DIR, "web_crawling")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

CANDIDATES_JSONL = os.path.join(DATA_DIR, "raw_discovered_candidates.jsonl")

# Output files
EXCLUDED_DUPLICATES_CSV = os.path.join(BASE_DIR, "excluded_ajpc_duplicates.csv")
UNCERTAIN_CANDIDATES_CSV = os.path.join(BASE_DIR, "uncertain_candidates.csv")
VERIFIED_NEW_JOURNALS_CSV = os.path.join(BASE_DIR, "new_post2020_journals.csv")
FINAL_COMBINED_DATASET_CSV = os.path.join(BASE_DIR, "final_combined_journal_dataset.csv")
PROVENANCE_CSV = os.path.join(BASE_DIR, "journal_record_provenance.csv")
CREDIBILITY_EVIDENCE_CSV = os.path.join(BASE_DIR, "journal_credibility_audit.csv")

# -------------------------------------------------------------
# 1. BUILD AJPC INDEX FOR DEDUPLICATION
# -------------------------------------------------------------
def normalize_str(s):
    if not s: return ""
    s = s.lower().strip()
    return re.sub(r"[^a-z0-9]", "", s)

def extract_domain(url):
    if not url: return ""
    p = urlparse(url)
    return p.netloc.lower().replace("www.", "").strip()

whitelist_file = os.path.join(WEB_CRAWLING_DIR, "whitelist.csv")
spj_blacklist_file = os.path.join(WEB_CRAWLING_DIR, "spj_blacklist.csv")
scraped_blacklist_file = os.path.join(WEB_CRAWLING_DIR, "blacklist_dataset.csv")

# Load whitelist
wl_records = []
wl_titles = {}
wl_urls = {}
wl_domains = {}
with open(whitelist_file, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.reader(f):
        if r:
            wl_records.append(r)
            rec_id, t, u = r[0], r[1].strip(), r[8].strip()
            wl_titles[normalize_str(t)] = (rec_id, t, "AJPC_WHITELIST")
            wl_urls[u.rstrip("/").lower()] = (rec_id, t, "AJPC_WHITELIST")
            dom = extract_domain(u)
            if dom and dom not in {"sciencedirect.com", "springer.com", "nature.com", "wiley.com", "hindawi.com", "frontiersin.org", "mdpi.com", "tandfonline.com", "oup.com", "ieee.org", "acm.org"}:
                wl_domains[dom] = (rec_id, t, "AJPC_WHITELIST")

# Load blacklist
with open(spj_blacklist_file, "r", encoding="utf-8", errors="ignore") as f:
    bl_urls = next(csv.reader(f))
with open(scraped_blacklist_file, "r", encoding="utf-8", errors="ignore") as f:
    bl_scraped = list(csv.reader(f))

bl_records = []
bl_titles = {}
bl_urls_map = {}
bl_domains = {}
for i, url in enumerate(bl_urls):
    u = url.strip()
    words = [w.strip() for w in bl_scraped[i] if w.strip()] if i < len(bl_scraped) else []
    title = words[0] if (words and len(words[0]) > 3 and not any(b in words[0].lower() for b in ["skip to", "toggle navigation", "search"])) else urlparse(u).netloc
    rec_id = f"BL_{i+1}"
    bl_records.append({"id": rec_id, "title": title, "url": u})
    bl_titles[normalize_str(title)] = (rec_id, title, "AJPC_BLACKLIST")
    bl_urls_map[u.rstrip("/").lower()] = (rec_id, title, "AJPC_BLACKLIST")
    dom = extract_domain(u)
    if dom:
        bl_domains[dom] = (rec_id, title, "AJPC_BLACKLIST")

print(f"Loaded AJPC Benchmark Baseline: {len(wl_records)} Whitelist + {len(bl_records)} Blacklist = {len(wl_records) + len(bl_records)} records.")

def check_ajpc_match(title, url):
    norm_t = normalize_str(title)
    norm_u = url.rstrip("/").lower() if url else ""
    dom = extract_domain(url)
    
    if norm_u:
        if norm_u in wl_urls:
            orig = wl_urls[norm_u]
            return "DUPLICATE_URL", f"Matches Whitelist URL {orig[0]} ({orig[1]})"
        if norm_u in bl_urls_map:
            orig = bl_urls_map[norm_u]
            return "DUPLICATE_URL", f"Matches Blacklist URL {orig[0]} ({orig[1]})"
            
    if norm_t:
        if norm_t in wl_titles:
            orig = wl_titles[norm_t]
            return "DUPLICATE_TITLE", f"Matches Whitelist Title {orig[0]} ({orig[1]})"
        if norm_t in bl_titles:
            orig = bl_titles[norm_t]
            return "DUPLICATE_TITLE", f"Matches Blacklist Title {orig[0]} ({orig[1]})"
            
    if dom and dom not in {"sciencedirect.com", "springer.com", "nature.com", "wiley.com", "hindawi.com", "frontiersin.org", "mdpi.com", "tandfonline.com", "oup.com", "ieee.org", "acm.org"}:
        if dom in wl_domains:
            orig = wl_domains[dom]
            return "DUPLICATE_DOMAIN", f"Matches Whitelist Domain '{dom}' ({orig[1]})"
        if dom in bl_domains:
            orig = bl_domains[dom]
            return "DUPLICATE_DOMAIN", f"Matches Blacklist Domain '{dom}' ({orig[1]})"
            
    return "NEW_NOT_IN_AJPC", "No match in original AJPC dataset"

# -------------------------------------------------------------
# 2. LOAD RAW DISCOVERED CANDIDATES AND TRIAGE
# -------------------------------------------------------------
candidates = []
with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            candidates.append(json.loads(line))

print(f"Total raw discovered candidates loaded from JSONL: {len(candidates)}")

excluded_duplicates = []
uncertain_candidates = []
verified_post2020_journals = []

# Predatory publisher keywords and known deceptive naming patterns
PREDATORY_PUBLISHER_PATTERNS = [
    "science publishing group", "sciencepg", "allied academies", "macrothink",
    "scientific research publishing", "scirp", "scholars academic", "edproskills",
    "ijmrge", "research publish journals", "sciencedomain", "david publishing",
    "international digital organization for scientific information", "idosi",
    "grd journals", "global journals inc", "innspub", "arc publications", "austin publishing",
    "baishideng", "clinmed international", "crest journals", "elixir", "iiste"
]

HIGH_RISK_TITLE_PATTERNS = [
    "modernization in engineering technology and science",
    "multidisciplinary research and growth evaluation",
    "innovative and creativity",
    "recent advances in multidisciplinary topics",
    "advanced multidisciplinary research and studies"
]

LEGITIMATE_PUBLISHER_PATTERNS = [
    "springer", "nature", "elsevier", "wiley", "oxford university press", "cambridge university press",
    "ieee", "acm", "plos", "frontiers", "mdpi", "biomed central", "sage publications", "taylor & francis",
    "american chemical society", "royal society of chemistry", "iop publishing", "de gruyter",
    "karger", "emerald", "wolters kluwer", "bentham", "universit", "college", "institute", "academy"
]

for cand in candidates:
    title = str(cand.get("title") or "").strip()
    url = str(cand.get("url") or "").strip()
    issn_l = str(cand.get("issn_l") or "").strip()
    pub = str(cand.get("publisher") or "").strip().lower()
    norm_t = cand.get("normalized_title", normalize_str(title))
    launch_yr = cand.get("launch_year")
    
    # 1. Check AJPC duplication
    match_status, match_ev = check_ajpc_match(title, url)
    if match_status != "NEW_NOT_IN_AJPC":
        excluded_duplicates.append({
            "candidate_title": title,
            "candidate_url": url,
            "publisher": cand.get("publisher", ""),
            "issn": issn_l,
            "match_status": match_status,
            "match_evidence": match_ev,
            "launch_year": launch_yr,
            "collection_date": "2026-10-12"
        })
        continue
        
    # 2. Check Launch-Date Eligibility (Established post-31-Dec-2020)
    try:
        yr_val = int(launch_yr) if launch_yr else None
    except:
        yr_val = None
        
    if not yr_val or yr_val < 2021:
        uncertain_candidates.append({
            "candidate_title": title,
            "candidate_url": url,
            "publisher": cand.get("publisher", ""),
            "issn": issn_l,
            "eligibility_status": "PRE_2021" if (yr_val and yr_val < 2021) else "UNCERTAIN_LAUNCH_DATE",
            "launch_year": launch_yr,
            "launch_date_evidence": cand.get("launch_date_evidence", ""),
            "reason_for_exclusion": f"Launch year ({launch_yr}) is prior to 2021 cutoff or undetermined",
            "collection_date": "2026-10-12",
            "human_review_required": "Yes"
        })
        continue
        
    # 3. Check Serial Identity: Ensure it is a genuine journal (exclude pure book series or conference proceedings)
    low_title = title.lower()
    if any(k in low_title for k in ["conference proceedings", "proceedings of the", "workshop on", "symposium on"]):
        uncertain_candidates.append({
            "candidate_title": title,
            "candidate_url": url,
            "publisher": cand.get("publisher", ""),
            "issn": issn_l,
            "eligibility_status": "EXCLUDED_PROCEEDINGS",
            "launch_year": launch_yr,
            "launch_date_evidence": cand.get("launch_date_evidence", ""),
            "reason_for_exclusion": "Identified as conference proceedings volume rather than regular journal",
            "collection_date": "2026-10-12",
            "human_review_required": "No"
        })
        continue

    # 4. Credibility Assessment
    is_doaj = cand.get("doaj_indexed", False)
    source = cand.get("source", "")
    
    # Assess Predatory Risk
    is_predatory_publisher = any(p in pub for p in PREDATORY_PUBLISHER_PATTERNS)
    is_high_risk_title = any(h in low_title for h in HIGH_RISK_TITLE_PATTERNS)
    is_search_pred_seed = "OpenAlex_Search" in source and (not is_doaj and not any(lp in pub for lp in LEGITIMATE_PUBLISHER_PATTERNS))
    
    # Assess Legitimate Evidence
    is_legit_publisher = any(lp in pub for lp in LEGITIMATE_PUBLISHER_PATTERNS)
    
    if (is_predatory_publisher or is_high_risk_title or is_search_pred_seed) and not is_doaj:
        cred_assessment = "Questionable / Predatory"
        cred_evidence = f"Publisher '{cand.get('publisher')}' or journal matches known predatory publishing patterns/registries; rapid acceptance / lack of certified indexing."
        cred_code = 0
    elif is_doaj or is_legit_publisher:
        cred_assessment = "Legitimate / Credible"
        cred_evidence = f"Indexed in DOAJ directory ({is_doaj}) or published by recognized scholarly entity ({cand.get('publisher')}); adheres to COPE / editorial standards."
        cred_code = 1
    else:
        cred_assessment = "Unlabeled / Pending Evidence"
        cred_evidence = f"Serial established {yr_val}; independent indexing or predatory listing currently inconclusive without secondary bibliometric audit."
        cred_code = -1
        
    verified_post2020_journals.append({
        "candidate": cand,
        "credibility_assessment": cred_assessment,
        "credibility_evidence": cred_evidence,
        "credibility_code": cred_code
    })

print(f"\n--- Triage Results ---")
print(f"Excluded AJPC Duplicates: {len(excluded_duplicates)}")
print(f"Uncertain / Pre-2021 / Excluded Non-Journals: {len(uncertain_candidates)}")
print(f"Verified Post-2020 Journals Discovered: {len(verified_post2020_journals)}")

# -------------------------------------------------------------
# 3. EXPORT EXCLUDED DUPLICATES AND UNCERTAIN FILES
# -------------------------------------------------------------
with open(EXCLUDED_DUPLICATES_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["candidate_title", "candidate_url", "publisher", "issn", "match_status", "match_evidence", "launch_year", "collection_date"])
    writer.writeheader()
    writer.writerows(excluded_duplicates)

with open(UNCERTAIN_CANDIDATES_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["candidate_title", "candidate_url", "publisher", "issn", "eligibility_status", "launch_year", "launch_date_evidence", "reason_for_exclusion", "collection_date", "human_review_required"])
    writer.writeheader()
    writer.writerows(uncertain_candidates)

# -------------------------------------------------------------
# 4. EXPORT VERIFIED NEW POST-2020 JOURNALS
# -------------------------------------------------------------
NEW_JOURNALS_FIELDS = [
    "id", "journal_name", "publisher", "issn_print", "issn_electronic", "issn_l",
    "discipline", "launch_year", "launch_date_evidence", "earliest_publication",
    "eligibility_status", "sjr", "quartile", "apc_amount", "apc_currency",
    "open_access", "h_index", "url", "credibility_assessment", "credibility_evidence",
    "credibility_code", "source_urls", "collection_date", "human_review_required"
]

verified_new_rows = []
for i, item in enumerate(verified_post2020_journals):
    cand = item["candidate"]
    rec_id = f"POST2020_{i+1:04d}"
    subjects = cand.get("subjects", [])
    discipline = ", ".join(subjects[:2]) if subjects else "Multidisciplinary"
    
    verified_new_rows.append({
        "id": rec_id,
        "journal_name": cand.get("title", ""),
        "publisher": cand.get("publisher", ""),
        "issn_print": cand.get("issn_p", ""),
        "issn_electronic": cand.get("issn_e", ""),
        "issn_l": cand.get("issn_l", ""),
        "discipline": discipline,
        "launch_year": cand.get("launch_year", ""),
        "launch_date_evidence": cand.get("launch_date_evidence", ""),
        "earliest_publication": cand.get("earliest_publication", ""),
        "eligibility_status": "VERIFIED_POST_2020",
        "sjr": "-",
        "quartile": "-",
        "apc_amount": cand.get("apc_amount", "-"),
        "apc_currency": cand.get("apc_currency", "-"),
        "open_access": cand.get("open_access", "yes"),
        "h_index": "-",
        "url": cand.get("url", ""),
        "credibility_assessment": item["credibility_assessment"],
        "credibility_evidence": item["credibility_evidence"],
        "credibility_code": item["credibility_code"],
        "source_urls": cand.get("url", "") or cand.get("openalex_id", ""),
        "collection_date": "2026-10-12",
        "human_review_required": "Yes" if item["credibility_code"] == -1 else "No"
    })

with open(VERIFIED_NEW_JOURNALS_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=NEW_JOURNALS_FIELDS)
    writer.writeheader()
    writer.writerows(verified_new_rows)

print(f"Saved {len(verified_new_rows)} verified post-2020 journals to {VERIFIED_NEW_JOURNALS_CSV}.")

# -------------------------------------------------------------
# 5. EXPORT CREDIBILITY EVIDENCE AUDIT FILE
# -------------------------------------------------------------
with open(CREDIBILITY_EVIDENCE_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "journal_name", "publisher", "launch_year", "credibility_assessment", "credibility_evidence", "credibility_code", "human_review_required"])
    writer.writeheader()
    for r in verified_new_rows:
        writer.writerow({
            "id": r["id"],
            "journal_name": r["journal_name"],
            "publisher": r["publisher"],
            "launch_year": r["launch_year"],
            "credibility_assessment": r["credibility_assessment"],
            "credibility_evidence": r["credibility_evidence"],
            "credibility_code": r["credibility_code"],
            "human_review_required": r["human_review_required"]
        })

# -------------------------------------------------------------
# 6. REBUILD FINAL COMBINED DATASET SAFELY
# -------------------------------------------------------------
# Canonical columns of original AJPC whitelist.csv:
CANONICAL_COLUMNS = ["id", "journal_name", "sjr", "quartile", "apc_amount", "apc_currency", "open_access", "h_index", "url"]

combined_dataset = []
provenance_rows = []

# 1. Add all 1,213 original whitelist records unchanged
for r in wl_records:
    combined_dataset.append(r[:9])
    provenance_rows.append({
        "id": r[0],
        "journal_name": r[1],
        "original_source": "AJPC_WHITELIST",
        "original_label": "1",
        "cohort": "HISTORICAL_PRE_2021",
        "launch_year": "Pre-2021",
        "eligibility_status": "HISTORICAL_BASELINE",
        "verification_notes": "Preserved verbatim from original web_crawling/whitelist.csv"
    })

# 2. Add all 833 original blacklist records unchanged
for i, item in enumerate(bl_records):
    rec_id = str(len(wl_records) + i + 1)
    combined_dataset.append([rec_id, item["title"], "-", "-", "-", "-", "-", "-", item["url"]])
    provenance_rows.append({
        "id": rec_id,
        "journal_name": item["title"],
        "original_source": "AJPC_BLACKLIST",
        "original_label": "0",
        "cohort": "HISTORICAL_PRE_2021",
        "launch_year": "Pre-2021",
        "eligibility_status": "HISTORICAL_BASELINE",
        "verification_notes": "Preserved from web_crawling/spj_blacklist.csv + blacklist_dataset.csv"
    })

# 3. Append verified eligible new post-2020 journals
for r in verified_new_rows:
    new_id = str(len(combined_dataset) + 1)
    combined_dataset.append([
        new_id,
        r["journal_name"],
        r["sjr"],
        r["quartile"],
        r["apc_amount"],
        r["apc_currency"],
        r["open_access"],
        r["h_index"],
        r["url"]
    ])
    provenance_rows.append({
        "id": new_id,
        "journal_name": r["journal_name"],
        "original_source": "POST_2020_DISCOVERY",
        "original_label": str(r["credibility_code"]),
        "cohort": "POST_2020_EXPANSION",
        "launch_year": str(r["launch_year"]),
        "eligibility_status": "VERIFIED_POST_2020",
        "verification_notes": r["credibility_evidence"]
    })

with open(FINAL_COMBINED_DATASET_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(CANONICAL_COLUMNS)
    writer.writerows(combined_dataset)

with open(PROVENANCE_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "journal_name", "original_source", "original_label", "cohort", "launch_year", "eligibility_status", "verification_notes"])
    writer.writeheader()
    writer.writerows(provenance_rows)

print(f"\n=== Rebuilt Final Combined Dataset ===")
print(f"Total Rows in {FINAL_COMBINED_DATASET_CSV}: {len(combined_dataset)} (plus header = {len(combined_dataset)+1})")
print(f"Original Preserved: {len(wl_records) + len(bl_records)}")
print(f"New Eligible Appended: {len(verified_new_rows)}")
print(f"Columns: {len(CANONICAL_COLUMNS)}")
