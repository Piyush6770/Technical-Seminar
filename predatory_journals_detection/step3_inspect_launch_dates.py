import sys
import os
import json
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\piyus\Technical Seminar\predatory_journals_detection"
df_new = pd.read_csv(os.path.join(BASE_DIR, "new_post2020_journals.csv"))
df_prov = pd.read_csv(os.path.join(BASE_DIR, "journal_record_provenance.csv"))

print(f"Total new post-2020 records: {len(df_new)}")
print("\nLaunch year value counts in new_post2020_journals:")
print(df_new['launch_year'].value_counts())

print("\nEarliest publication value counts (sample):")
print(df_new['earliest_publication'].value_counts().head(10))

# Check evidence strings
print("\nSample launch_date_evidence:")
print(df_new['launch_date_evidence'].head(10))
