# RecoMart OCI Object Storage Deployment

## Cloud Configuration
- Cloud Provider: Oracle Cloud Infrastructure
- Service: Object Storage
- Home Region: India West (Mumbai)
- Region Identifier: ap-mumbai-1
- Bucket: recomart-dmml-data
- Namespace: bmyxec10ufou
- Storage Tier: Standard
- Public Access: NoPublicAccess

## Uploaded Data
- Raw Retailrocket CSV files
- Ingestion-date raw copies
- Prepared event data
- Category tree
- Item property Parquet chunks
- User and item features
- User-item interaction features
- EDA reports and visualizations
- Data quality report
- Model evaluation metrics
- Ingestion and lineage manifests

## Architecture Note
Data preparation, feature engineering and model training
were executed on the local Linux environment.
OCI Object Storage was used for cloud storage of the
dataset and generated pipeline artifacts.

## Evidence
See reports/screenshots/ for OCI Console screenshots.
