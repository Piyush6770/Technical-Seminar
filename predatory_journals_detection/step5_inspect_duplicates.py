import sys
import os
import re
import pandas as pd
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
df_comb = pd.read_csv(os.path.join(BASE_DIR, "final_combined_journal_dataset.csv"))
df_new = pd.read_csv(os.path.join(BASE_DIR, "new_post2020_journals.csv"))
df_ex_dup = pd.read_csv(os.path.join(BASE_DIR, "excluded_ajpc_duplicates.csv"))
df_dup_cand = pd.read_csv(os.path.join(BASE_DIR, "duplicate_candidates.csv"))

print(f"Total rows in duplicate_candidates.csv: {len(df_dup_cand)}")
print("Match type breakdown in duplicate_candidates.csv:")
print(df_dup_cand['match_type'].value_counts())

print(f"\nTotal rows in excluded_ajpc_duplicates.csv: {len(df_ex_dup)}")
print("Match status in excluded_ajpc_duplicates.csv:")
print(df_ex_dup['match_status'].value_counts())

# Let's inspect the 16 duplicate canonical URLs in df_comb
url_counts = df_comb['url'].dropna().value_counts()
dup_urls = url_counts[url_counts > 1]
print(f"\nDuplicate URLs in final_combined_journal_dataset: {len(dup_urls)} distinct URLs appearing across {dup_urls.sum()} records")
for u, cnt in dup_urls.items():
    matching = df_comb[df_comb['url'] == u]
    print(f"  URL: {u} (Count: {cnt})")
    for _, m in matching.iterrows():
        print(f"    ID {m['id']}: {m['journal_name']}")

# Let's inspect the duplicate normalized titles in df_comb
def norm_t(t):
    if not t or pd.isna(t): return ""
    return re.sub(r'[^a-z0-9]', '', str(t).lower())

df_comb['norm_title'] = df_comb['journal_name'].apply(norm_t)
title_counts = df_comb['norm_title'].value_counts()
dup_titles = title_counts[title_counts > 1]
print(f"\nDuplicate Normalized Titles in final_combined_journal_dataset: {len(dup_titles)} distinct normalized titles across {dup_titles.sum()} records")
print("Top 10 duplicate titles by frequency:")
for t, cnt in dup_titles.head(10).items():
    matching = df_comb[df_comb['norm_title'] == t]
    sample_names = list(matching['journal_name'].unique())[:3]
    sample_urls = list(matching['url'].dropna().unique())[:3]
    print(f"  NormTitle: '{t}' (Count: {cnt}) -> Names: {sample_names} | URLs: {sample_urls}")
