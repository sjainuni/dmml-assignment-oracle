from src.ingest import ingest_local_to_lake
from src.validate import validate_events
from src.prepare import prepare
from src.catalog import process_catalog
from src.eda import generate_eda
from src.features import build_features
from src.versioning import snapshot
from src.train import train
from src.common import get_logger
log=get_logger("pipeline")
def run():
    ingest_local_to_lake()
    quality=validate_events()
    if quality["quality_status"]!="PASS": log.warning("Quality report requires review; continuing with cleaning rules.")
    df=prepare()
    catalog=process_catalog()
    eda=generate_eda(df)
    ui,user,item=build_features(df)
    lineage=snapshot()
    metrics=train(ui)
    log.info("END-TO-END PIPELINE SUCCESS")
    return {"quality":quality,"catalog":catalog,"eda":eda,"rows_prepared":len(df),"metrics":metrics,"lineage_version":lineage["version"]}
