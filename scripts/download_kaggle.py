from pathlib import Path
import subprocess, zipfile, sys
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/"data"/"raw"; raw.mkdir(parents=True,exist_ok=True)
cmd=["kaggle","datasets","download","-d","retailrocket/ecommerce-dataset","-p",str(raw),"--force"]
print("Downloading Retailrocket from Kaggle. Kaggle authentication must already be configured locally.")
subprocess.run(cmd,check=True)
archives=list(raw.glob("*.zip"))
if not archives: raise SystemExit("Kaggle CLI completed but no ZIP archive was found.")
archive=max(archives,key=lambda p:p.stat().st_mtime)
with zipfile.ZipFile(archive) as z:
    bad=z.testzip()
    if bad: raise SystemExit(f"Corrupt archive member: {bad}")
    z.extractall(raw)
print("Extracted files:")
for p in sorted(raw.rglob("*.csv")): print(p.relative_to(ROOT),p.stat().st_size,"bytes")
