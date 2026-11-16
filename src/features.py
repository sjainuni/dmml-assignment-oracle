import pandas as pd, json
from src.common import ROOT, get_logger
log=get_logger("features")
def build_features(df):
    # User/item interaction activity and weighted affinity features
    user=df.groupby("visitorid").agg(user_event_count=("itemid","size"),user_unique_items=("itemid","nunique"),user_mean_event_weight=("event_weight","mean")).reset_index()
    item=df.groupby("itemid").agg(item_event_count=("visitorid","size"),item_unique_visitors=("visitorid","nunique"),item_mean_event_weight=("event_weight","mean")).reset_index()
    ui=df.groupby(["visitorid","itemid"]).agg(affinity=("event_weight","sum"),last_event=("timestamp","max"),interaction_count=("event","size")).reset_index()
    # co-occurrence pairs among a capped number of most active items for practical scale
    top_items=item.nlargest(300,"item_event_count").itemid.tolist()
    sample=df[df.itemid.isin(top_items)][["visitorid","itemid"]].drop_duplicates()
    pair=sample.merge(sample,on="visitorid")
    pair=pair[pair.itemid_x<pair.itemid_y].groupby(["itemid_x","itemid_y"]).size().reset_index(name="cooccurrence")
    out=ROOT/"data"/"features"; out.mkdir(parents=True,exist_ok=True)
    user.to_parquet(out/"user_features.parquet",index=False); item.to_parquet(out/"item_features.parquet",index=False)
    ui.to_parquet(out/"user_item_features.parquet",index=False); pair.to_csv(out/"item_cooccurrence.csv",index=False)
    metadata={
      "feature_set":"recomart_retailrocket_v1",
      "version":"1.0.0",
      "features":[
        {"name":"user_event_count","entity":"visitorid","source":"events.csv","transformation":"count of retained events"},
        {"name":"user_unique_items","entity":"visitorid","source":"events.csv","transformation":"distinct item count"},
        {"name":"user_mean_event_weight","entity":"visitorid","source":"events.csv","transformation":"mean configured implicit event weight"},
        {"name":"item_event_count","entity":"itemid","source":"events.csv","transformation":"count of retained events"},
        {"name":"item_unique_visitors","entity":"itemid","source":"events.csv","transformation":"distinct visitors"},
        {"name":"affinity","entity":"visitorid,itemid","source":"events.csv","transformation":"sum of view/add-to-cart/transaction weights"}
      ]
    }
    (out/"feature_registry.json").write_text(json.dumps(metadata,indent=2))
    log.info("Feature tables written; user=%s item=%s interactions=%s",len(user),len(item),len(ui))
    return ui,user,item
def retrieve_feature(feature_name, entity_id, version="1.0.0"):
    meta=json.loads((ROOT/"data"/"features"/"feature_registry.json").read_text())
    if meta["version"]!=version: raise ValueError(f"Requested {version}; available {meta['version']}")
    mapping={"visitorid":"user_features.parquet","itemid":"item_features.parquet"}
    spec=next((x for x in meta["features"] if x["name"]==feature_name),None)
    if not spec: raise KeyError(feature_name)
    entity=spec["entity"]
    if entity not in mapping: raise ValueError("Use visitorid or itemid entity for scalar retrieval")
    frame=pd.read_parquet(ROOT/"data"/"features"/mapping[entity])
    return frame[frame[entity]==entity_id][[entity,feature_name]]
