import pandas as pd
from src.common import ROOT, load_config, get_logger
from src.validate import locate
log=get_logger("catalog")
def process_catalog():
    out=ROOT/"data"/"processed"/"item_properties"
    out.mkdir(parents=True,exist_ok=True)
    prop_files=list((ROOT/"data"/"raw").rglob("item_properties*.csv"))
    if not prop_files: prop_files=list((ROOT/"data"/"raw").rglob("item_properties.csv"))
    if not prop_files:
        log.warning("No item_properties CSV located; catalog property stage skipped.")
        return {"property_files":0,"rows":0}
    total=0
    for fi,p in enumerate(prop_files):
        for ci,chunk in enumerate(pd.read_csv(p,chunksize=load_config()["chunksize"])):
            required={"timestamp","itemid","property","value"}
            if not required.issubset(chunk.columns):
                raise ValueError(f"Unexpected item properties schema in {p.name}: {list(chunk.columns)}")
            chunk=chunk.dropna(subset=["itemid","property","value"])
            chunk["timestamp"]=pd.to_numeric(chunk.timestamp,errors="coerce")
            chunk=chunk.dropna(subset=["timestamp"])
            chunk["itemid"]=pd.to_numeric(chunk.itemid,errors="coerce")
            chunk=chunk.dropna(subset=["itemid"])
            chunk["itemid"]=chunk.itemid.astype("int64")
            dest=out/f"source={fi}"/f"chunk={ci}.parquet"
            dest.parent.mkdir(parents=True,exist_ok=True)
            chunk.to_parquet(dest,index=False)
            total+=len(chunk)
    tree_files=list((ROOT/"data"/"raw").rglob("category_tree.csv"))
    if tree_files:
        tree=pd.read_csv(tree_files[0])
        if not {"categoryid","parentid"}.issubset(tree.columns):
            raise ValueError("category_tree.csv must contain categoryid and parentid")
        tree.drop_duplicates().to_csv(ROOT/"data"/"processed"/"category_tree_clean.csv",index=False)
    log.info("Catalog processed in chunks: %s property rows across %s files",total,len(prop_files))
    return {"property_files":len(prop_files),"rows":total}
