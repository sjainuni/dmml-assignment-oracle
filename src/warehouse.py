from pathlib import Path
import duckdb
import json

from src.common import ROOT, get_logger

log = get_logger("warehouse")

DB_DIR = ROOT / "database"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "recomart_warehouse.duckdb"


def build_warehouse():
    con = duckdb.connect(str(DB_PATH))

    sources = {
        "events": ROOT / "data/processed/events_prepared.parquet",
        "users": ROOT / "data/features/user_features.parquet",
        "items": ROOT / "data/features/item_features.parquet",
        "user_items": ROOT / "data/features/user_item_features.parquet",
    }

    for name, path in sources.items():
        if not path.exists():
            raise FileNotFoundError(path)

    log.info("Loading prepared interactions")

    con.execute("""
        CREATE OR REPLACE TABLE fact_interaction AS
        SELECT
            visitorid,
            itemid,
            event_datetime AS event_timestamp,
            event AS event_type,
            event_weight,
            TRY_CAST(transactionid AS BIGINT) AS transactionid,
            CAST(event_datetime AS DATE) AS ingestion_date
        FROM read_parquet(?)
    """, [str(sources["events"])])

    log.info("Loading user features")

    con.execute("""
        CREATE OR REPLACE TABLE feature_user AS
        SELECT *,
            'v1' AS feature_version,
            CURRENT_TIMESTAMP AS computed_at
        FROM read_parquet(?)
    """, [str(sources["users"])])

    log.info("Loading item features")

    con.execute("""
        CREATE OR REPLACE TABLE feature_item AS
        SELECT *,
            'v1' AS feature_version,
            CURRENT_TIMESTAMP AS computed_at
        FROM read_parquet(?)
    """, [str(sources["items"])])

    log.info("Loading user-item features")

    con.execute("""
        CREATE OR REPLACE TABLE feature_user_item AS
        SELECT *
        FROM read_parquet(?)
    """, [str(sources["user_items"])])

    log.info("Loading item catalog")

    category_path = ROOT / "data/processed/category_tree_clean.csv"

    if category_path.exists():
        con.execute("""
            CREATE OR REPLACE TABLE category_tree AS
            SELECT *
            FROM read_csv_auto(?)
        """, [str(category_path)])

    property_files = sorted(
        (ROOT / "data/processed/item_properties").rglob("*.parquet")
    )

    if property_files:
        paths = [str(p) for p in property_files]
        con.execute("""
            CREATE OR REPLACE TABLE item_properties AS
            SELECT * FROM read_parquet(?, union_by_name=true)
        """, [paths])

    log.info("Loading model evaluation metrics")

    metrics_path = ROOT / "reports/model_metrics.json"

    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        con.execute("""
            CREATE TABLE IF NOT EXISTS model_run (
                run_id VARCHAR,
                algorithm VARCHAR,
                metrics_json JSON,
                created_at TIMESTAMP
            )
        """)
        con.execute("""
            INSERT INTO model_run
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            str(metrics.get("mlflow_run_id", "unknown")),
            "TruncatedSVD",
            json.dumps(metrics)
        ])

    log.info("Warehouse tables created")

    tables = con.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_name
    """).fetchall()

    for table in tables:
        count = con.execute(
            f'SELECT COUNT(*) FROM "{table[0]}"'
        ).fetchone()[0]
        print(f"{table[0]}: {count:,} rows")

    con.close()
    print(f"\nWarehouse created: {DB_PATH}")


if __name__ == "__main__":
    build_warehouse()
