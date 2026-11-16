from pathlib import Path
import pandas as pd, json
from src.common import ROOT, get_logger
log=get_logger("validate")
def locate(name):
    hits=list((ROOT/"data"/"raw").rglob(name))
    if not hits: raise FileNotFoundError(f"Missing {name} under data/raw")
    return hits[0]
def validate_events():
    p=locate("events.csv")
    df=pd.read_csv(p)
    required={"timestamp","visitorid","event","itemid"}
    missing_schema=sorted(required-set(df.columns))
    if missing_schema: raise ValueError(f"events.csv missing columns: {missing_schema}")
    report={
      "file":str(p.relative_to(ROOT)),"rows":int(len(df)),"columns":list(df.columns),
      "missing_visitorid":int(df.visitorid.isna().sum()),
      "missing_itemid":int(df.itemid.isna().sum()),
      "duplicate_rows":int(df.duplicated().sum()),
      "unknown_event_types":sorted(set(df.event.dropna().astype(str))-{"view","addtocart","transaction"}),
      "invalid_timestamp":int(pd.to_numeric(df.timestamp,errors="coerce").isna().sum()),
      "transactionid_null_expected_for_non_transactions":True
    }
    report["quality_status"]="PASS" if not report["missing_visitorid"] and not report["missing_itemid"] and not report["invalid_timestamp"] and not report["unknown_event_types"] else "REVIEW"
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports"/"data_quality_report.json").write_text(json.dumps(report,indent=2))
    log.info("Validation completed: %s",report["quality_status"])
    return report
