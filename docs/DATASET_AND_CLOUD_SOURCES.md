# Sources and technical references

- Retailrocket dataset (Kaggle): https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- OCI Object Storage multipart uploads: https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingmultipartuploads.htm
- OCI Python SDK UploadManager: https://docs.oracle.com/en-us/iaas/tools/python/latest/upload-manager.html
- OCI API signing keys: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm

Dataset source files and schema must be verified against the archive downloaded by the team. The project treats `transactionid` nulls for non-purchase events as expected semantics, not a failed required field. Event weights are configurable modeling assumptions, not labels supplied by Kaggle.
