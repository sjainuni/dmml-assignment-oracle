# RecoMart – End-to-End Data Pipeline Architecture

## 1. Objective
Design a scalable and maintainable data management pipeline
for an e-commerce recommendation system.

## 2. Architecture Components

| Layer | Technology | Status |
|---|---|---|
| Data Source | Retailrocket CSV | Implemented |
| Data Ingestion | Python, Pandas | Implemented |
| Data Validation | Python | Implemented |
| Cloud Storage | OCI Object Storage (Mumbai) | Implemented |
| Data Processing | Pandas, Parquet | Implemented |
| Feature Store | Custom Feature Registry | Implemented |
| Data Lineage | SHA-256 manifests | Implemented |
| Model Training | TruncatedSVD | Implemented |
| Experiment Tracking | MLflow | Implemented |
| Orchestration | Prefect | Pending verification |
| Data Warehouse | DuckDB / SQL | Proposed |
| BI Dashboard | Looker / Power BI | Optional |

## 3. Data Flow

Retailrocket Dataset
        |
        v
Python Ingestion
        |
        v
Data Validation
        |
        v
OCI Object Storage (Mumbai)
        |
        v
Data Preparation and EDA
        |
        v
Feature Engineering
        |
        v
Feature Store
        |
        v
Recommendation Model (SVD)
        |
        v
MLflow Evaluation and Tracking
        |
        v
Top-N Recommendations

Prefect will orchestrate the pipeline stages.

## 4. Future Enhancements
- Automated orchestration using Prefect
- Analytical warehouse using DuckDB
- Dataset versioning using DVC
- Optional BI dashboard
- Near-real-time ingestion using OCI Streaming
