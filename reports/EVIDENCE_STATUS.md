# Evidence Status

## Execution Status

The RecoMart recommendation-system data pipeline was executed locally using the Retailrocket dataset.

The pipeline completed successfully through Prefect with nine tasks:

1. Data ingestion
2. Data validation
3. Data preparation
4. Item-property catalog processing
5. Exploratory data analysis
6. Feature engineering
7. Data lineage and versioning
8. Model training
9. DuckDB warehouse integration

## OCI Object Storage

- OCI Object Storage bucket: `recomart-dmml-data`
- Region: `ap-mumbai-1`
- Raw, processed, feature, and report objects were uploaded.
- Object presence was verified in the OCI Console.

Screenshots are available in `reports/screenshots/`.

## DVC Data Versioning

- Four Retailrocket source CSV files are tracked using DVC.
- DVC remote storage is configured on OCI Object Storage.
- `dvc push` completed successfully.
- A fresh-clone restoration was tested using `dvc pull`.

See `docs/DATA_VERSIONING.md` for the procedure and configuration details.

## Prefect Orchestration

The nine-task Prefect flow completed successfully.

Screenshots:
- `reports/screenshots/prefect_warehouse_dashboard.png`
- `reports/screenshots/_prefect_warehouse_execution.png`

Additional Prefect screenshots are available in the same directory.

## DuckDB Warehouse

The local DuckDB warehouse was generated and verified.

It contains interaction, user, item, user-item feature, item-property, category-tree, and model-run tables.

The database is retained locally and is excluded from Git because of its size.

## Model Evaluation

Model evaluation results are recorded in:

- `reports/model_metrics.json`

The trained model is available locally at:

- `models/recommender_svd.joblib`

## Supporting Evidence

- Data quality report: `reports/Data_Quality_Report.pdf`
- EDA report: `reports/EDA_REPORT.md`
- EDA charts: `reports/figures/`
- Ingestion manifest: `reports/ingestion_manifest.json`
- Lineage manifest: `reports/lineage_manifest.json`
- OCI deployment evidence: `reports/OCI_DEPLOYMENT_EVIDENCE.md`
- Screenshots: `reports/screenshots/`

## Execution Scope and Limitations

Data processing, model training, Prefect orchestration, and DuckDB warehouse generation were performed locally.

OCI Object Storage was used for cloud data storage and the DVC remote. The project did not deploy its processing pipeline or Prefect server on OCI Compute.

