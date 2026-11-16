# Demo video script (target 7–9 minutes)

**Important:** record only after the real dataset run and OCI deployment. Show genuine screens and hide OCIDs, email addresses, tokens and private-key paths.

1. **0:00–0:40 — Introduction:** RecoMart problem, five-person team and objective.
2. **0:40–1:30 — Architecture:** Kaggle source → staging → OCI Object Storage → processing → feature registry → SVD → MLflow → Prefect.
3. **1:30–2:20 — Ingestion:** show Kaggle source files, ingestion manifest, retries/logs and OCI bucket objects.
4. **2:20–3:10 — Validation:** show schema/key checks, duplicates, invalid timestamps/event types and quality JSON.
5. **3:10–4:00 — Preparation/EDA:** show event-type distribution, item popularity and user-item sparsity charts (generate/attach actual charts after execution).
6. **4:00–5:00 — Features:** explain user activity, item popularity, weighted affinity and co-occurrence; show SQL schema and versioned registry retrieval.
7. **5:00–6:10 — Versioning/model:** show SHA-256 lineage manifest, SVD parameters, ranking metrics and MLflow run ID.
8. **6:10–7:20 — Orchestration:** show Prefect flow graph, successful task states and logs.
9. **7:20–8:00 — Conclusion:** discuss cold-start, temporal evaluation limitations, scaling and monitoring improvements.

Do not narrate placeholder metrics or claim unexecuted cloud resources exist.
