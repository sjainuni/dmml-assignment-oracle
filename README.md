# RecoMart — End-to-End Data Management Pipeline
### OCI Object Storage + Retailrocket + DVC + Prefect + DuckDB

**Course:** Data Management for Machine Learning (S1-26_DSEZG529)  
**Submission date:** 22 November 2026  
**Student:** Sandeep Kumar Jain | **ID:** 2025NS04132  
**Team:** Five-member team (complete contribution table in the submission report)

## Project Overview

RecoMart implements an end-to-end data management pipeline for an
e-commerce recommendation system using the Retailrocket dataset.

The implementation covers:
- Data ingestion and validation.
- Local data lake and OCI Object Storage.
- Data preparation and exploratory data analysis.
- Feature engineering and a custom feature registry.
- Dataset versioning using DVC.
- Data lineage using SHA-256 manifests.
- Collaborative filtering using TruncatedSVD.
- Experiment tracking using MLflow.
- Pipeline orchestration using Prefect.
- Analytical warehouse using DuckDB.

**Execution scope:** Data processing, model training, DuckDB and
Prefect orchestration execute in the local Linux environment.
OCI Object Storage provides cloud-based data and artifact storage.
DVC uses OCI's S3-compatible API for remote dataset versioning.
This project does not claim deployment of the processing pipeline
on OCI Compute.

## Architecture

Retailrocket CSV datasets
    |
    v
Python ingestion and validation
    |
    v
OCI Object Storage
    |
    v
Data preparation and EDA
    |
    v
Feature engineering and feature registry
    |
    +-------------------------+
    |                         |
    v                         v
DuckDB warehouse        TruncatedSVD model
                              |
                              v
                         MLflow tracking

DVC manages dataset versions:
GitHub stores DVC metadata and OCI Object Storage stores
the versioned dataset objects.

Prefect orchestrates the end-to-end processing workflow.

See `docs/architecture.md` for details.

## Dataset

Kaggle dataset:
https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset

Source files:
- `events.csv`
- `item_properties_part1.csv`
- `item_properties_part2.csv`
- `category_tree.csv`

`transactionid` is naturally null for non-transaction events.
It is not treated as a missing user/item key.

Retailrocket provides implicit feedback (`view`, `addtocart`,
`transaction`), not explicit 1–5 ratings. The project therefore
uses event-strength weights documented in `config.json` and
evaluates ranking rather than inventing ratings.

## 1. Environment Setup (Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install DVC with S3-compatible storage support:

```bash
python -m pip install "dvc[s3]>=3,<4"
```

## 2. Dataset Setup

The project uses the four original Retailrocket CSV files.

For Kaggle download:

```bash
pip install kaggle
mkdir -p ~/.config/kaggle
chmod 600 ~/.config/kaggle/kaggle.json
python scripts/download_kaggle.py
```

Keep Kaggle credentials outside the repository.

The DVC-managed source dataset directory is:

```text
data/dvc_raw/
```

The DVC metadata file is:

```text
data/dvc_raw.dvc
```

## 3. DVC Dataset Versioning

DVC tracks the four source CSV files. The DVC metadata is stored
in GitHub, while the dataset objects are stored remotely in OCI
Object Storage.

Configured remote:
- Remote name: `oci-dvc`
- Bucket: `recomart-dmml-data`
- Prefix: `dvc-store`
- Region: `ap-mumbai-1`
- Storage interface: OCI S3-compatible API

### Configure credentials

Create an OCI Customer Secret Key for the OCI user.

Store the credentials locally in:

```text
~/.aws/credentials
```

Use this profile structure:

```ini
[dvc-oci]
aws_access_key_id = YOUR_OCI_ACCESS_KEY
aws_secret_access_key = YOUR_OCI_SECRET_KEY
```

The secret values must never be committed to GitHub.

### Restore versioned datasets

Clone the repository:

```bash
git clone git@github.com:sjainuni/dmml-assignment-oracle.git
cd dmml-assignment-oracle
```

Restore the dataset:

```bash
dvc pull
```

Verify:

```bash
dvc status -c
ls -lh data/dvc_raw/
```

### Upload updated dataset versions

After modifying tracked data:

```bash
dvc status
dvc add data/dvc_raw
dvc push
```

Commit the updated DVC metadata:

```bash
git add data/dvc_raw.dvc data/.gitignore
git commit -m "Update DVC dataset version"
git push origin main
```

## 4. OCI Object Storage

OCI Object Storage is configured in the Mumbai region (`ap-mumbai-1`).

The project uses a private bucket:

```text
recomart-dmml-data
```

The bucket stores raw, processed, feature and report artifacts,
as well as the DVC remote objects.

The OCI CLI session authentication used for project uploads
is separate from the Customer Secret Key used by DVC's
S3-compatible remote.

For native OCI uploads:

```bash
python scripts/oci_sync.py upload
```

Never commit OCI private keys, session tokens or `.env` files.

## 5. Run the Data Pipeline

Run the local pipeline:

```bash
PYTHONPATH=. python -m src.orchestration
```

For a local Prefect UI:

```bash
prefect server start
```

In another terminal:

```bash
export PREFECT_API_URL="http://127.0.0.1:4200/api"
PYTHONPATH=. python -m src.orchestration
```

The Prefect flow includes nine tasks:

1. Data ingestion
2. Data validation
3. Data preparation
4. Catalog processing
5. Exploratory data analysis
6. Feature engineering
7. Data lineage snapshot
8. Model training
9. DuckDB warehouse creation

The flow has been successfully executed and verified.

## 6. DuckDB Analytical Warehouse

The analytical warehouse is stored locally at:

```text
database/recomart_warehouse.duckdb
```

Build or refresh the warehouse:

```bash
PYTHONPATH=. python -m src.warehouse
```

The warehouse includes:
- `fact_interaction`
- `feature_user`
- `feature_item`
- `feature_user_item`
- `item_properties`
- `category_tree`
- `model_run`

Example SQL:

```sql
SELECT event_type, COUNT(*) AS total
FROM fact_interaction
GROUP BY event_type
ORDER BY total DESC;
```

The generated DuckDB database is excluded from Git because
it is a large local analytical artifact.

## 7. Model and Evaluation

The project uses TruncatedSVD collaborative filtering
for implicit-feedback recommendation.

Model evaluation metrics include:
- Precision@10
- Recall@10
- NDCG@10
- Sampled reconstruction RMSE

Model metrics are stored in:

```text
reports/model_metrics.json
```

MLflow stores experiment tracking information and model run metadata.

## 8. Evidence

Evidence is maintained under `reports/` and includes:
- Data quality PDF and validation summary.
- EDA plots and methodology.
- Feature registry and lineage manifests.
- Model evaluation metrics.
- Prefect dashboard and flow execution screenshots.
- DuckDB warehouse validation.
- DVC metadata and OCI remote restoration evidence.

Use actual execution screenshots and logs. Do not use mock evidence.

## 9. Git Hygiene and Security

Never commit:
- `.env`
- `.venv/`
- OCI private keys or session tokens.
- Kaggle credentials.
- AWS-compatible credential files.
- Raw CSV datasets.
- Parquet data files.
- Model binaries.
- Local DuckDB databases.
- DVC cache contents.

Commit DVC metadata files, source code, SQL schemas,
documentation and appropriate small evidence files.

## 10. Deliverables

- Source code under `src/`.
- Utility scripts under `scripts/`.
- SQL schema under `sql/`.
- Architecture and methodology documentation under `docs/`.
- Data quality, EDA and model reports under `reports/`.
- Trained model artifact under `models/`.
- Prefect execution evidence.
- DVC metadata and versioned dataset in OCI.
- Editable submission report.
- Five-to-ten-minute demonstration video.
- Final project ZIP.

Complete the five-member contribution table in the submission
report and share final deliverables through the approved
BITS submission/Google Drive process.

## 11. Cost and Security

OCI Always Free eligibility and quotas vary by tenancy,
region and service availability.

Use a private bucket, apply least-privilege IAM policies,
monitor storage and request costs, and remove temporary
resources after the demonstration.

Never assume a budget alert is a hard spending cap.
