import urllib.request
import ssl
import json
import os
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def search_crossref(query):
    try:
        url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows=3"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data['message']['items']
            for item in items:
                title = item.get('title', [''])[0]
                doi = item.get('DOI', '')
                links = [l.get('URL') for l in item.get('link', []) if 'pdf' in l.get('content-type', '')]
                print(f"Title: {title[:60]} | DOI: {doi} | PDF links: {links}")
    except Exception as e:
        print("Crossref error:", e)

queries = [
    "Predatory publishers are corrupting open access Jeffrey Beall Nature 2012",
    "Who's afraid of peer review? John Bohannon Science 2013",
    "Principles of Transparency and Best Practice in Scholarly Publishing 2022",
    "Automated detection of fraudulent scholarly websites via DOM tree structural analysis",
    "Verification of forecasts expressed in terms of probability Brier 1950",
    "Discipline-specific characteristics of predatory publishing Severin 2021"
]

for q in queries:
    print("\n--- Query:", q)
    search_crossref(q)
