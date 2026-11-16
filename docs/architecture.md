# RecoMart – End-to-End Data Pipeline Architecture

## 1. Objective

Design and implement an end-to-end data management pipeline
for an e-commerce recommendation system using the Retailrocket dataset.

The solution covers data ingestion, validation, cloud storage,
data preparation, feature engineering, data versioning,
model development, experiment tracking, orchestration and analytics.

## 2. Architecture Components

| Layer | Technology | Status |
|---|---|---|
| Data Source | Retailrocket CSV | Implemented |
| Data Ingestion | Python, Pandas | Implemented |
| Data Validation | Python validation and quality reports | Implemented |
| Cloud Storage | OCI Object Storage (Mumbai) | Implemented |
| Data Processing | Pandas, Parquet | Implemented |
| Feature Store | Custom Feature Registry | Implemented |
| Data Versioning | DVC 3.67.1 | Implemented and restore tested |
| Cloud Data Versioning | DVC with OCI S3-compatible API | Implemented |
| Data Lineage | SHA-256 manifests | Implemented |
| Model Training | TruncatedSVD | Implemented |
| Experiment Tracking | MLflow | Implemented |
| Orchestration | Prefect 3.9.3 | Implemented and successfully executed |
| Data Warehouse | DuckDB with SQL | Implemented |
| BI Dashboard | Looker / Power BI | Optional |

## 3. Architecture and Data Flow

### 3.1 Source and ingestion

- Retailrocket events, category tree and item properties datasets.
- Python-based ingestion into the local data lake.
- Ingestion manifests and SHA-256 checksums.

### 3.2 Storage and data versioning

- OCI Object Storage bucket in Mumbai stores raw and processed artifacts.
- DVC tracks the four original source CSV datasets.
- DVC metadata is version-controlled through GitHub.
- DVC dataset objects are stored in OCI Object Storage using its
  S3-compatible API.
- A clean Git clone and DVC pull successfully restored the datasets.

### 3.3 Processing and analytics

- Data validation checks missing values, duplicates, schema and formats.
- Data preparation and EDA use Python and Pandas.
- Processed data is stored in Parquet format.
- Feature engineering generates user, item and user-item features.
- A custom feature registry records feature metadata and versions.
- DuckDB stores curated interactions, features, catalog data and
  model evaluation metrics in an analytical warehouse.

### 3.4 Model development

- TruncatedSVD collaborative filtering model.
- Top-N recommendation evaluation.
- Precision@10, Recall@10 and NDCG@10 metrics.
- MLflow experiment tracking and model evaluation records.

### 3.5 Orchestration

Prefect orchestrates the following nine pipeline tasks:

1. Data ingestion
2. Data validation
3. Data preparation
4. Catalog processing
5. Exploratory data analysis
6. Feature engineering
7. Data lineage snapshot
8. Model training
9. DuckDB warehouse creation

The Prefect flow has been successfully executed and verified.

## 4. High-Level Architecture

Retailrocket Source Datasets
        |
        v
Python Data Ingestion
        |
        v
Data Validation and Quality Reporting
        |
        v
OCI Object Storage
        |
        v
Data Preparation and EDA
        |
        v
Feature Engineering
        |
        v
Custom Feature Store
        |
        +----------------------+
        |                      |
        v                      v
DuckDB Warehouse         TruncatedSVD Model
        |                      |
        |                      v
        |                MLflow Evaluation
        |                      |
        +----------------------+
                   |
                   v
          Analytical Outputs

DVC manages source dataset versions, with GitHub storing
DVC metadata and OCI Object Storage holding versioned data objects.

Prefect orchestrates the end-to-end processing and model pipeline.

## 5. Deployment Scope and Limitations

- Data processing, model training, DuckDB and Prefect orchestration
  execute in the local Linux environment.
- OCI Object Storage provides cloud-based artifact and dataset storage.
- DVC uses OCI's S3-compatible API for remote dataset storage.
- The project does not currently use OCI Compute or a managed cloud
  orchestration service.
- Looker and Power BI remain optional enhancements.

## 6. Future Enhancements

- Deploy processing workloads to OCI Compute.
- Introduce near-real-time ingestion using OCI Streaming.
- Add a BI dashboard using Looker or Power BI.
- Explore automated model deployment and recommendation serving.
