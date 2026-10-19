import sys
import os
import re
import json
import pandas as pd
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
df_comb = pd.read_csv(os.path.join(BASE_DIR, "final_combined_journal_dataset.csv"))
df_new = pd.read_csv(os.path.join(BASE_DIR, "new_post2020_journals.csv"))
df_mal = pd.read_csv(os.path.join(BASE_DIR, "malformed_records.csv"))

print(f"Total combined records: {len(df_comb)}")
print(f"Total malformed record entries: {len(df_mal)}")

# 1. Inspect the 10 malformed URLs
mal_ids = df_mal[df_mal['issue_type'] == 'MALFORMED_URL']['journal_id'].tolist()
print(f"\n10 Malformed IDs: {mal_ids}")

# Clean and resolve each of the 10 malformed URLs
fixed_malformed = {}
for mid in mal_ids:
    row = df_comb[df_comb['id'] == mid].iloc[0]
    raw_url = str(row['url'])
    # Strip curly braces
    clean_urls = [u.strip() for u in raw_url.strip('{}').split(',') if u.strip()]
    # Select the most specific journal homepage URL
    best_url = clean_urls[0]
    for u in clean_urls:
        if any(kw in u for kw in ['journal', 'ojs', 'browse', 'detail', 'su-journal', 'ijmp', 'CJCS', 'frle', 'contrastive-ling']):
            best_url = u
            break
    fixed_malformed[mid] = {
        "id": mid,
        "journal_name": row['journal_name'],
        "raw_url": raw_url,
        "recovered_url": best_url,
        "source": "OPENALEX_CANONICAL_CONTAINER_PARSED",
        "status": "MALFORMED_FIXED"
    }

for k, v in fixed_malformed.items():
    print(f"  ID {k}: {v['journal_name'][:35]} -> {v['recovered_url']}")

# 2. Inspect the 1,246 records with MISSING_URL
miss_ids = df_mal[df_mal['issue_type'] == 'MISSING_URL']['journal_id'].tolist()
print(f"\nMissing URL count: {len(miss_ids)}")

# Check what metadata exists for these missing records
new_lookup = {}
for _, r in df_new.iterrows():
    # map to combined id
    try:
        cid = int(r['id'].replace('POST2020_', '')) + 2046
        new_lookup[cid] = r
    except:
        pass

missing_metadata = []
for mid in miss_ids:
    nr = new_lookup.get(mid)
    if nr is not None:
        missing_metadata.append({
            "id": mid,
            "title": nr['journal_name'],
            "publisher": nr['publisher'],
            "issn_l": nr['issn_l'],
            "issn_p": nr['issn_print'],
            "issn_e": nr['issn_electronic'],
            "source_urls": nr['source_urls'],
            "doaj_indexed": nr['open_access']
        })

df_mm = pd.DataFrame(missing_metadata)
print("Publisher breakdown for missing records:")
print(df_mm['publisher'].value_counts().head(20))
