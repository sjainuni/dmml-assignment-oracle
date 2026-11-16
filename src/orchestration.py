from prefect import flow, task
from src.ingest import ingest_local_to_lake
from src.validate import validate_events
from src.prepare import prepare
from src.catalog import process_catalog
from src.eda import generate_eda
from src.features import build_features
from src.versioning import snapshot
from src.train import train
from src.common import get_logger
log=get_logger("prefect")
@task(retries=2,retry_delay_seconds=10,log_prints=True)
def ingest_task(): return ingest_local_to_lake()
@task(retries=1,log_prints=True)
def validate_task(): return validate_events()
@task(retries=1,log_prints=True)
def prepare_task(): return prepare()
@task(retries=1,log_prints=True)
def catalog_task(): return process_catalog()
@task(retries=1,log_prints=True)
def eda_task(df): return generate_eda(df)
@task(retries=1,log_prints=True)
def feature_task(df): return build_features(df)
@task(retries=1,log_prints=True)
def lineage_task(): return snapshot()
@task(retries=1,log_prints=True)
def train_task(feature_tuple): return train(feature_tuple[0])
@flow(name="recomart-retailrocket-end-to-end",log_prints=True)
def recomart_flow():
    log.info("Starting RecoMart orchestration")
    ingest_task()
    quality=validate_task()
    if quality["quality_status"]!="PASS": log.warning("Validation status REVIEW; cleaning will apply documented rules.")
    df=prepare_task()
    catalog=catalog_task()
    eda=eda_task(df)
    features=feature_task(df)
    lineage=lineage_task()
    metrics=train_task(features)
    log.info("Pipeline flow completed")
    return {"quality":quality,"catalog":catalog,"eda":eda,"lineage":lineage["version"],"metrics":metrics}
if __name__=="__main__":
    recomart_flow()
