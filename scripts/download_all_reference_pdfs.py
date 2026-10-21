import urllib.request
import ssl
import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(PROJECT_ROOT, "research_paper", "reference_papers")
os.makedirs(REF_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def download_file(url, target_path):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read()
            if data.startswith(b'%PDF'):
                with open(target_path, 'wb') as f:
                    f.write(data)
                print(f"[SUCCESS] {os.path.basename(target_path)} ({len(data)} bytes)")
                return True
            else:
                print(f"[NOT PDF] {os.path.basename(target_path)} from {url} - starts with {data[:40]}")
                return False
    except Exception as e:
        print(f"[ERROR] {os.path.basename(target_path)} from {url}: {e}")
        return False

# Target downloads
TARGETS = [
    # 01 Beall 2012 Nature
    ("01_Beall_2012_Predatory_Publishers_Nature.pdf", [
        "https://raw.githubusercontent.com/Piyush6770/Technical-Seminar/main/research_paper/reference_papers/01_Beall_2012.pdf",
        "https://www.nature.com/articles/489179a.pdf",
        "https://web.archive.org/web/20120915000000/http://www.nature.com/nature/journal/v489/n7415/pdf/489179a.pdf"
    ]),
    # 05 Bohannon 2013 Science
    ("05_Bohannon_2013_Whos_Afraid_of_Peer_Review.pdf", [
        "https://www.science.org/doi/pdf/10.1126/science.342.6154.60",
        "https://web.archive.org/web/20131004183856/http://www.sciencemag.org/content/342/6154/60.full.pdf",
        "https://m.eet.com/media/1191060/who-s-afraid-of-peer-review.pdf"
    ]),
    # 07 Vence 2022 The Scientist
    ("07_Vence_2022_Paper_Mills_The_Dark_Side.pdf", [
        "https://www.the-scientist.com/pdf/paper-mills-2022.pdf"
    ]),
    # 09 Gasparyan 2016 JKMS
    ("09_Gasparyan_2016_Predatory_Publishing_Threat.pdf", [
        "https://synapse.koreamed.org/upload/SynapseData/PDFData/0063jkms/jkms-31-1864.pdf",
        "https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC5143324&blobtype=pdf"
    ]),
    # 10 Eriksson 2016 Learned Publishing
    ("10_Eriksson_2016_The_Blacklists_Are_Dying.pdf", [
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/leap.1055"
    ]),
    # 11 Strinzel 2019 Learned Publishing
    ("11_Strinzel_2019_Blacklists_and_Whitelists.pdf", [
        "https://boris.unibe.ch/132470/1/leap.1242.pdf",
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/leap.1242"
    ]),
    # 12 Dadkhah 2016 Science and Engineering Ethics
    ("12_Dadkhah_2016_Ranking_Predatory_Journals.pdf", [
        "https://link.springer.com/content/pdf/10.1007/s11948-015-9653-x.pdf"
    ]),
    # 14 Bano 2023 IEEE TKDE
    ("14_Bano_2023_Automated_Detection_Fraudulent_Websites.pdf", [
        "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9667232"
    ]),
    # 15 Severin 2019 Learned Publishing
    ("15_Severin_2019_Predatory_Publishing_Guide.pdf", [
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/leap.1232"
    ]),
    # 18 Severin 2021 Learned Publishing
    ("18_Severin_2021_Discipline_Specific_Characteristics.pdf", [
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/leap.1361?download=true"
    ]),
    # 28 COPE Principles
    ("28_COPE_2022_Principles_of_Transparency.pdf", [
        "https://publicationethics.org/files/principles-of-transparency-and-best-practice-in-scholarly-publishing-4th-edition.pdf",
        "https://doaj.org/documents/principles-of-transparency-and-best-practice-in-scholarly-publishing.pdf"
    ]),
    # 29 Brier 1950 Monthly Weather Review
    ("29_Brier_1950_Verification_of_Forecasts_in_Terms_of_Probability.pdf", [
        "https://docs.lib.noaa.gov/rescue/mwr/078/mwr-078-01-0001.pdf"
    ])
]

for filename, urls in TARGETS:
    target = os.path.join(REF_DIR, filename)
    if os.path.exists(target) and os.path.getsize(target) > 5000:
        print(f"[EXISTS] {filename} ({os.path.getsize(target)} bytes)")
        continue
    downloaded = False
    for url in urls:
        if download_file(url, target):
            downloaded = True
            break
    if not downloaded:
        print(f"[RETRY NEEDED] {filename}")
