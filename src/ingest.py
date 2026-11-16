from pathlib import Path
import shutil, time, json
from datetime import datetime, timezone
from src.common import ROOT, get_logger, sha256
log=get_logger("ingest")
def ingest_local_to_lake():
    raw=ROOT/"data"/"raw"
    files=[p for p in raw.rglob("*") if p.is_file() and p.suffix.lower() in (".csv",".zip")]
    if not files: raise FileNotFoundError("No Retailrocket files found. Run: python scripts/download_kaggle.py")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest=[]
    for p in files:
        rel=p.relative_to(raw)
        target=ROOT/"data"/"lake"/"raw"/f"ingest_date={stamp[:8]}"/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        for attempt in range(1,4):
            try:
                shutil.copy2(p,target); break
            except OSError:
                if attempt==3: raise
                time.sleep(attempt*2)
        rec={"source":"Kaggle Retailrocket","path":str(target.relative_to(ROOT)),"bytes":target.stat().st_size,"sha256":sha256(target),"ingested_at_utc":stamp}
        manifest.append(rec); log.info("Ingested %s (%s bytes)",rel,target.stat().st_size)
    out=ROOT/"reports"/"ingestion_manifest.json"; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2))
    return [Path(x["path"]) for x in manifest]
