import os
import sys
import csv
import json
import time
import re
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError

sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(sys.maxsize)

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DISCOVERY_LOG_FILE = os.path.join(OUTPUTS_DIR, "discovery_logs.jsonl")
RAW_CANDIDATES_FILE = os.path.join(DATA_DIR, "raw_discovered_candidates.jsonl")

HEADERS = {
    "User-Agent": "ScholarlyIntegrityResearch/2.0 (mailto:academic-journal-audit@openresearch.org)"
}

def log_event(event_type, details):
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "details": details
    }
    with open(DISCOVERY_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def fetch_json(url, max_retries=3, delay=1.0):
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8')
                return json.loads(content)
        except HTTPError as e:
            log_event("HTTP_ERROR", {"url": url, "code": e.code, "attempt": attempt})
            if e.code == 429:
                time.sleep(delay * 3 * attempt)
            else:
                time.sleep(delay * attempt)
        except URLError as e:
            log_event("URL_ERROR", {"url": url, "error": str(e.reason), "attempt": attempt})
            time.sleep(delay * attempt)
        except Exception as e:
            log_event("FETCH_EXCEPTION", {"url": url, "error": str(e), "attempt": attempt})
            time.sleep(delay * attempt)
    return None

def normalize_title(t):
    if not t:
        return ""
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9]", "", t)
    return t

# Load existing candidates from persistence file if resuming
seen_keys = set()
total_candidates = []

if os.path.exists(RAW_CANDIDATES_FILE):
    with open(RAW_CANDIDATES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                k = item.get("identity_key")
                if k:
                    seen_keys.add(k)
                    total_candidates.append(item)
    print(f"Resumed from {RAW_CANDIDATES_FILE}: loaded {len(total_candidates)} existing raw candidates.")

def save_candidate(cand):
    ident = cand.get("identity_key")
    if ident in seen_keys:
        return False
    seen_keys.add(ident)
    total_candidates.append(cand)
    with open(RAW_CANDIDATES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(cand, ensure_ascii=False) + "\n")
    return True

print("=== Starting Paginated Discovery Pipeline (OpenAlex, DOAJ, Crossref) ===")
log_event("PIPELINE_START", {"initial_candidates_count": len(total_candidates)})

# -----------------------------------------------------------------------------------
# SOURCE 1: DOAJ (Directory of Open Access Journals) - oa_start >= 2021
# -----------------------------------------------------------------------------------
print("\n[Source 1: DOAJ] Querying journals with bibjson.oa_start >= 2021...")
doaj_page = 1
doaj_page_size = 100
max_doaj_pages = 25  # Retrieve up to 2,500 candidates from DOAJ

while doaj_page <= max_doaj_pages:
    url = f"https://doaj.org/api/search/journals/bibjson.oa_start:%5B2021%20TO%202026%5D?page={doaj_page}&pageSize={doaj_page_size}"
    data = fetch_json(url)
    if not data or "results" not in data:
        print(f"  DOAJ Page {doaj_page} failed or empty. Stopping DOAJ retrieval.")
        break
    
    results = data["results"]
    if not results:
        print(f"  DOAJ Page {doaj_page} returned 0 results. Completed DOAJ.")
        break
    
    added_in_page = 0
    for item in results:
        bib = item.get("bibjson", {})
        title = bib.get("title", "").strip()
        if not title:
            continue
        
        pissn = bib.get("pissn", "")
        eissn = bib.get("eissn", "")
        issn_l = pissn or eissn
        
        norm_t = normalize_title(title)
        identity_key = f"ISSN:{issn_l}" if issn_l else f"TITLE:{norm_t}"
        
        # Extract publisher
        pub = bib.get("publisher", {})
        pub_name = pub.get("name", "") if isinstance(pub, dict) else str(pub)
        
        # Extract APC
        apc_data = bib.get("apc", {})
        has_apc = apc_data.get("has_apc", False) if isinstance(apc_data, dict) else False
        apc_amt = "-"
        apc_curr = "-"
        if has_apc and isinstance(apc_data, dict):
            max_val = apc_data.get("max", [])
            if max_val and isinstance(max_val, list) and len(max_val) > 0:
                apc_amt = str(max_val[0].get("price", "-"))
                apc_curr = str(max_val[0].get("currency", "-"))
        
        # Extract homepage URL
        ref = bib.get("ref", {})
        journal_url = ref.get("journal", "") if isinstance(ref, dict) else ""
        if not journal_url and "links" in bib:
            for lk in bib.get("links", []):
                if lk.get("type") == "homepage":
                    journal_url = lk.get("url", "")
                    break
                    
        # Extract subjects/discipline
        subjects = [s.get("term", "") for s in bib.get("subject", []) if isinstance(s, dict)]
        
        cand = {
            "source": "DOAJ",
            "identity_key": identity_key,
            "title": title,
            "normalized_title": norm_t,
            "publisher": pub_name,
            "issn_p": pissn,
            "issn_e": eissn,
            "issn_l": issn_l,
            "url": journal_url,
            "launch_year": bib.get("oa_start"),
            "earliest_publication": f"{bib.get('oa_start')}-01-01" if bib.get("oa_start") else "",
            "launch_date_evidence": f"DOAJ bibjson.oa_start is {bib.get('oa_start')}; registered in DOAJ catalogue",
            "subjects": subjects,
            "apc_amount": apc_amt,
            "apc_currency": apc_curr,
            "open_access": "yes",
            "doaj_indexed": True,
            "openalex_id": "",
            "raw_metadata": {
                "created_date": item.get("created_date"),
                "publication_time_weeks": bib.get("publication_time_weeks")
            }
        }
        
        if save_candidate(cand):
            added_in_page += 1
            
    print(f"  DOAJ Page {doaj_page}/{max_doaj_pages}: Processed {len(results)} items, added {added_in_page} unique new candidates. Total candidates: {len(total_candidates)}")
    log_event("DOAJ_PAGE_COMPLETED", {"page": doaj_page, "fetched": len(results), "added": added_in_page})
    doaj_page += 1
    time.sleep(0.5)

# -----------------------------------------------------------------------------------
# SOURCE 2: OpenAlex API - Journals with first_publication_year > 2020
# -----------------------------------------------------------------------------------
print("\n[Source 2: OpenAlex] Querying post-2020 journal sources...")
# Query broadly by pages (first_publication_year > 2020)
oa_page = 1
oa_page_size = 100
max_oa_pages = 25  # Retrieve up to 2,500 candidates from OpenAlex

while oa_page <= max_oa_pages:
    url = f"https://api.openalex.org/sources?filter=type:journal,first_publication_year:>2020&per-page={oa_page_size}&page={oa_page}"
    data = fetch_json(url)
    if not data or "results" not in data:
        print(f"  OpenAlex Page {oa_page} failed or empty. Stopping OpenAlex retrieval.")
        break
    
    results = data["results"]
    if not results:
        print(f"  OpenAlex Page {oa_page} returned 0 results. Completed OpenAlex.")
        break
        
    added_in_page = 0
    for s in results:
        title = s.get("display_name", "").strip()
        if not title:
            continue
            
        issn_l = s.get("issn_l", "")
        issns = s.get("issn", []) or []
        pissn = issns[0] if len(issns) > 0 else ""
        eissn = issns[1] if len(issns) > 1 else (pissn if pissn else "")
        if not issn_l and issns:
            issn_l = issns[0]
            
        norm_t = normalize_title(title)
        identity_key = f"ISSN:{issn_l}" if issn_l else f"TITLE:{norm_t}"
        
        first_year = s.get("first_publication_year")
        works_count = s.get("works_count", 0)
        host_org = s.get("host_organization_name", "")
        homepage = s.get("homepage_url", "")
        is_oa = "yes" if s.get("is_oa") else "no"
        apc_usd = str(s.get("apc_usd", "-")) if s.get("apc_usd") is not None else "-"
        
        topics = [t.get("display_name", "") for t in s.get("topics", [])[:3] if isinstance(t, dict)]
        
        cand = {
            "source": "OpenAlex",
            "identity_key": identity_key,
            "title": title,
            "normalized_title": norm_t,
            "publisher": host_org or "Unknown / Independent",
            "issn_p": pissn,
            "issn_e": eissn,
            "issn_l": issn_l,
            "url": homepage,
            "launch_year": first_year,
            "earliest_publication": f"{first_year}-01-01" if first_year else "",
            "launch_date_evidence": f"OpenAlex first_publication_year is {first_year}; total works indexed: {works_count}",
            "subjects": topics,
            "apc_amount": apc_usd,
            "apc_currency": "USD" if apc_usd != "-" else "-",
            "open_access": is_oa,
            "doaj_indexed": s.get("is_in_doaj", False),
            "openalex_id": s.get("id", ""),
            "raw_metadata": {
                "works_count": works_count,
                "cited_by_count": s.get("cited_by_count", 0),
                "is_oa": s.get("is_oa"),
                "is_in_doaj": s.get("is_in_doaj")
            }
        }
        
        if save_candidate(cand):
            added_in_page += 1
            
    print(f"  OpenAlex Page {oa_page}/{max_oa_pages}: Processed {len(results)} items, added {added_in_page} unique new candidates. Total candidates: {len(total_candidates)}")
    log_event("OPENALEX_PAGE_COMPLETED", {"page": oa_page, "fetched": len(results), "added": added_in_page})
    oa_page += 1
    time.sleep(0.5)

# -----------------------------------------------------------------------------------
# SOURCE 3: OpenAlex Targeted Keyword Searches for Potential Predatory / Standalone OA
# -----------------------------------------------------------------------------------
print("\n[Source 3: Targeted Serial Discovery] Running pattern queries for standalone & high-volume serials...")
target_queries = [
    "International Journal of Recent",
    "International Journal of Advanced",
    "World Journal of",
    "Global Journal of",
    "Universal Journal of",
    "European Journal of Applied",
    "Asian Journal of Multidisciplinary",
    "International Journal of Current"
]

for q in target_queries:
    enc_q = urllib.parse.quote_plus(q)
    url = f"https://api.openalex.org/sources?search={enc_q}&filter=type:journal,first_publication_year:>2020&per-page=50"
    data = fetch_json(url)
    if not data or "results" not in data:
        continue
    results = data["results"]
    added_in_q = 0
    for s in results:
        title = s.get("display_name", "").strip()
        if not title:
            continue
        issn_l = s.get("issn_l", "")
        norm_t = normalize_title(title)
        identity_key = f"ISSN:{issn_l}" if issn_l else f"TITLE:{norm_t}"
        first_year = s.get("first_publication_year")
        works_count = s.get("works_count", 0)
        host_org = s.get("host_organization_name", "")
        homepage = s.get("homepage_url", "")
        
        cand = {
            "source": f"OpenAlex_Search:{q}",
            "identity_key": identity_key,
            "title": title,
            "normalized_title": norm_t,
            "publisher": host_org or "Unknown / Independent",
            "issn_p": s.get("issn", [""])[0] if s.get("issn") else "",
            "issn_e": s.get("issn", [""])[-1] if s.get("issn") else "",
            "issn_l": issn_l,
            "url": homepage,
            "launch_year": first_year,
            "earliest_publication": f"{first_year}-01-01" if first_year else "",
            "launch_date_evidence": f"OpenAlex first_publication_year is {first_year} for query '{q}'; works count: {works_count}",
            "subjects": [t.get("display_name", "") for t in s.get("topics", [])[:2]],
            "apc_amount": str(s.get("apc_usd", "-")) if s.get("apc_usd") is not None else "-",
            "apc_currency": "USD" if s.get("apc_usd") is not None else "-",
            "open_access": "yes" if s.get("is_oa") else "no",
            "doaj_indexed": s.get("is_in_doaj", False),
            "openalex_id": s.get("id", ""),
            "raw_metadata": {
                "works_count": works_count,
                "cited_by_count": s.get("cited_by_count", 0)
            }
        }
        if save_candidate(cand):
            added_in_q += 1
    print(f"  Query '{q}': Added {added_in_q} unique candidates. Total candidates: {len(total_candidates)}")
    log_event("TARGETED_QUERY_COMPLETED", {"query": q, "added": added_in_q})
    time.sleep(0.5)

print(f"\n=== Finished Discovery Phase! Total Raw Candidates Discovered: {len(total_candidates)} ===")
log_event("PIPELINE_COMPLETE", {"total_raw_candidates": len(total_candidates)})
