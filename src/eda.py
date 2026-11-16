import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.sparse import csr_matrix
from src.common import ROOT, get_logger
log=get_logger("eda")
def generate_eda(df):
    out=ROOT/"reports"/"figures"; out.mkdir(parents=True,exist_ok=True)
    counts=df["event"].value_counts()
    fig,ax=plt.subplots(figsize=(7,4)); counts.plot(kind="bar",ax=ax); ax.set_title("Retailrocket event distribution"); ax.set_ylabel("Events"); fig.tight_layout(); fig.savefig(out/"event_distribution.png",dpi=160); plt.close(fig)
    popular=df["itemid"].value_counts().head(20)
    fig,ax=plt.subplots(figsize=(9,4)); popular.plot(kind="bar",ax=ax); ax.set_title("Top 20 items by interaction count"); ax.set_ylabel("Events"); fig.tight_layout(); fig.savefig(out/"item_popularity_top20.png",dpi=160); plt.close(fig)
    uc=df.groupby("visitorid").size()
    fig,ax=plt.subplots(figsize=(7,4)); ax.hist(uc.clip(upper=uc.quantile(.99)),bins=40); ax.set_title("User activity distribution (99th percentile clipped)"); ax.set_xlabel("Events per visitor"); fig.tight_layout(); fig.savefig(out/"user_activity.png",dpi=160); plt.close(fig)
    nu=df.visitorid.nunique(); ni=df.itemid.nunique(); nn=df[["visitorid","itemid"]].drop_duplicates().shape[0]
    sparsity=1-(nn/(nu*ni)) if nu and ni else None
    summary={"events":len(df),"visitors":int(nu),"items":int(ni),"unique_user_item_pairs":int(nn),"matrix_sparsity":float(sparsity) if sparsity is not None else None,"event_distribution":{str(k):int(v) for k,v in counts.items()}}
    (ROOT/"reports"/"eda_summary.json").write_text(json.dumps(summary,indent=2))
    log.info("EDA generated: %s",summary)
    return summary
