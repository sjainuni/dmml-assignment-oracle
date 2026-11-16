import pandas as pd, numpy as np, json
from src.common import ROOT, load_config, get_logger
from src.validate import locate
log=get_logger("prepare")
def prepare():
    cfg=load_config(); chunks=[]; n=0
    # Chunked read prevents full raw file from being loaded unnecessarily.
    for c in pd.read_csv(locate("events.csv"),chunksize=cfg["chunksize"]):
        c=c.dropna(subset=["visitorid","itemid","timestamp","event"])
        c["timestamp"]=pd.to_numeric(c.timestamp,errors="coerce")
        c=c.dropna(subset=["timestamp"])
        c["visitorid"]=c.visitorid.astype("int64"); c["itemid"]=c.itemid.astype("int64")
        c["event"]=c.event.astype(str).str.lower()
        c=c[c.event.isin(cfg["event_weights"])]
        c["event_weight"]=c.event.map(cfg["event_weights"]).astype(float)
        c["event_datetime"]=pd.to_datetime(c.timestamp,unit="ms",utc=True,errors="coerce")
        c=c.dropna(subset=["event_datetime"]).drop_duplicates()
        chunks.append(c); n+=len(c)
    if not chunks: raise ValueError("No valid events after preparation.")
    df=pd.concat(chunks,ignore_index=True)
    df["hour"]=df.event_datetime.dt.hour
    df["day_of_week"]=df.event_datetime.dt.dayofweek
    df["timestamp_minmax"]=(df.timestamp-df.timestamp.min())/(df.timestamp.max()-df.timestamp.min()+1e-9)
    out=ROOT/"data"/"processed"; out.mkdir(parents=True,exist_ok=True)
    df.to_parquet(out/"events_prepared.parquet",index=False)
    # category tree is a separate source and is loaded when available
    cat=list((ROOT/"data"/"raw").rglob("category_tree.csv"))
    if cat:
        tree=pd.read_csv(cat[0]); tree.to_csv(out/"category_tree_clean.csv",index=False)
    log.info("Prepared %s events",len(df))
    return df
