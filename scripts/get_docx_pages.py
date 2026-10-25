import subprocess

ps_script = """
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$docPath = (Resolve-Path "research_paper/research_paper.docx").Path
$doc = $word.Documents.Open($docPath, $false, $true, $false)
$pages = $doc.ComputeStatistics(2)
Write-Output "PAGE_COUNT: $pages"
$doc.Close([ref]$false)
$word.Quit()
"""

proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=20)
print(proc.stdout)
if proc.stderr:
    print("ERROR:", proc.stderr)
