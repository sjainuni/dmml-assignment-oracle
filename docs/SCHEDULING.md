# Periodic execution

For a simple Linux cron schedule, after validating the first full run:

```cron
0 2 * * * /absolute/path/RecoMart_DMML_OCI/scripts/run_periodic.sh >> /absolute/path/RecoMart_DMML_OCI/logs/cron.log 2>&1
```

Retailrocket is a historical static dataset; this schedule reruns ingestion/processing and records a new audit manifest. It does not create new source events. For a true near-real-time production system, replace the static source with a consented event API/stream (e.g. OCI Streaming) and process micro-batches. That live source is a future extension, not a capability claimed for this historical Kaggle dataset.
