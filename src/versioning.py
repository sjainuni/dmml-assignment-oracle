import json, hashlib
from datetime import datetime, timezone
from src.common import ROOT, sha256, get_logger
log=get_logger("lineage")
def snapshot():
    paths=[]
    for folder in [ROOT/"data"/"raw",ROOT/"data"/"processed",ROOT/"data"/"features"]:
        if folder.exists():
            for p in folder.rglob("*"):
                if p.is_file():
                    paths.append({"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha256(p)})
    record={"version":"retailrocket-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
      "created_at_utc":datetime.now(timezone.utc).isoformat(),"source":"Kaggle retailrocket/ecommerce-dataset",
      "transformations":["drop missing visitor/item/timestamp/event","deduplicate exact rows","map implicit event weights","derive user/item aggregates"],
      "artifacts":paths}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports"/"lineage_manifest.json").write_text(json.dumps(record,indent=2))
    log.info("Lineage manifest created for %s files",len(paths))
    return record
