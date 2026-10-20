import sys
import os
import json
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
df_new = pd.read_csv(os.path.join(BASE_DIR, "new_post2020_journals.csv"))
raw_candidates_path = os.path.join(BASE_DIR, "data", "raw_discovered_candidates.jsonl")

# Load raw candidate metadata to check works_count and raw fields
cand_lookup = {}
with open(raw_candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            c = json.loads(line)
            title = c.get("title", "").strip().lower()
            cand_lookup[title] = c

print(f"Loaded {len(cand_lookup)} raw candidates.")

# Check works count distribution
works_counts = []
for idx, r in df_new.iterrows():
    t = r['journal_name'].strip().lower()
    c = cand_lookup.get(t, {})
    meta = c.get("raw_metadata", {})
    wc = meta.get("works_count", 0)
    works_counts.append(wc)

df_new['works_count'] = works_counts
print("Works count summary:")
print(df_new['works_count'].describe())

# Check extreme works count (e.g. > 2000 works in a journal supposedly launched after 2020)
high_works = df_new[df_new['works_count'] > 2000]
print(f"\nJournals with > 2000 works claimed launched post-2020: {len(high_works)}")
for idx, r in high_works.head(10).iterrows():
    print(f"Title: {r['journal_name']} | Pub: {r['publisher']} | LaunchYr: {r['launch_year']} | Works: {r['works_count']}")
