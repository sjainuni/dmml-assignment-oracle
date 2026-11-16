# Final acceptance checklist — do not submit until every applicable item is verified

- [ ] 1. Problem formulation: objective, data sources, expected outputs, ranking metrics documented.
- [ ] 2. Ingestion: at least two source files ingested; scheduled/periodic trigger documented; retries, logs and manifest demonstrated.
- [ ] 3. Raw data storage: private OCI Object Storage bucket; source/type/date partitioning; upload verified.
- [ ] 4. Validation: missing keys, duplicates, schema, event types, timestamp format; quality report reviewed.
- [ ] 5. Preparation: cleaning, categorical/time features, timestamp normalisation, EDA distributions/popularity/sparsity, plots.
- [ ] 6. Feature engineering: user/item activity, weighted affinity, co-occurrence, SQL schema.
- [ ] 7. Feature store: metadata, source/logic, versioned retrieval demonstrated for training/inference.
- [ ] 8. Versioning/lineage: DVC or Git LFS workflow; source, ingestion date, transformations, SHA-256 hashes.
- [ ] 9. Model: collaborative filtering/matrix factorization; Precision@K, Recall@K, NDCG; MLflow parameters/metrics/run ID.
- [ ] 10. Orchestration: Prefect DAG, retries, logs, successful execution evidence.
- [ ] Additional: modular code, error handling, reproducibility, 5–10 minute video.
- [ ] Report includes title, team, problem, objectives, methodology, implementation, results, real screenshots, conclusion/future scope.
- [ ] Google Drive project ZIP and video links inserted; permissions set for any BITS ID.
- [ ] ZIP includes code, data or data acquisition instructions, trained model, documentation and support files.
- [ ] Five team-member IDs, names and real contributions completed and verified by team.
- [ ] Remove credentials, `.env`, private keys, Kaggle tokens and local auth files from Git and ZIP.
