# RecoMart — End-to-End Data Management Pipeline (OCI + Retailrocket)

**Course:** Data Management for Machine Learning (S1-26_DSEZG529)  
**Submission date:** 22 November 2026  
**Student:** Sandeep Kumar Jain | **ID:** 2025NS04132  
**Team:** Five-member team (complete the table in `docs/SUBMISSION_REPORT.docx`)

## Important status
This repository is a reproducible project implementation package. It is **not yet a claim of completed OCI deployment**. The real Retailrocket data must be downloaded using your Kaggle account, OCI tenancy details must be configured locally, and the deployment/run evidence must be generated in your tenancy. Never commit OCI private keys, Kaggle tokens, auth files, or secrets.

## Architecture
Kaggle Retailrocket → local staging → OCI Object Storage (`raw/`) → chunked validation/preparation → curated Parquet/CSV (`processed/`) → engineered features (`features/`) → custom versioned feature registry → implicit-feedback recommendation model → MLflow experiment metadata → Prefect orchestration/logs.

The OCI bucket is private. Use the Mumbai region (`ap-mumbai-1`) unless your tenancy is provisioned elsewhere.

## Dataset
Kaggle dataset: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset  
Expected source files (actual Kaggle archive naming can vary):
- `events.csv`
- `item_properties_part1.csv`
- `item_properties_part2.csv`
- `category_tree.csv`

`transactionid` is naturally null for non-transaction events; it is not treated as a missing user/item key. Retailrocket has implicit feedback (`view`, `addtocart`, `transaction`), not explicit 1–5 ratings. The project therefore uses event-strength weights, documented in `config.json`, and evaluates ranking rather than inventing ratings.

## 1. Setup (Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install Kaggle CLI and configure credentials **locally** (do not send the token to anyone):
```bash
pip install kaggle
mkdir -p ~/.config/kaggle
# Place kaggle.json from your Kaggle account in ~/.config/kaggle/kaggle.json
chmod 600 ~/.config/kaggle/kaggle.json
python scripts/download_kaggle.py
```
If your Kaggle CLI uses `~/.kaggle/kaggle.json`, put the file there instead. The script calls the Kaggle CLI and checks the archive.

## 2. Configure OCI locally
Install OCI CLI and configure an API signing key using Oracle's official instructions:
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm

Set your default profile region to `ap-mumbai-1`, then verify:
```bash
oci iam region-subscription list --profile DEFAULT
oci os ns get --profile DEFAULT
```
Create a private Object Storage bucket in your chosen compartment (Console or CLI). Then copy:
```bash
cp .env.example .env
```
Edit `.env` with the bucket name, namespace, compartment OCID and region. `.env` is ignored by Git. Do not put private keys in this repository.
```bash
python scripts/make_quality_pdf.py  # after validation report exists
python scripts/oci_sync.py upload
```

OCI SDK upload manager supports multipart uploads for large objects. The script uses the SDK upload manager.

## 3. Run locally first (smoke test / pipeline)
```bash
python scripts/run_pipeline.py
```
For a full Retailrocket run:
```bash
python scripts/run_pipeline.py --full
```
The pipeline requires the real `events.csv`; catalog processing also reads `item_properties*.csv` and `category_tree.csv` when present. It reads item property files in chunks. The default run caps training interactions for laptop memory; configure limits in `config.json`. Raw originals remain unchanged.

## 4. Orchestration
The project includes a Prefect flow (`src/orchestration.py`). Start a local Prefect server if desired:
```bash
prefect server start
# In another terminal:
python -m src.orchestration
```
The flow records task states and logs. For a cloud demonstration, run the flow from the OCI Compute instance or another authenticated runner and save the real Prefect UI/terminal screenshots under `reports/screenshots/`.

## 5. Evidence to capture after successful execution
1. Kaggle downloaded archive and extracted source files (hide account details).
2. OCI Console showing the private bucket and `raw/`, `processed/`, `features/` objects.
3. Ingestion log with file names, sizes and timestamps.
4. Validation report and quality summary.
5. EDA plots and prepared dataset profile.
6. Feature registry JSON and successful versioned retrieval output.
7. Dataset manifest with SHA-256 hashes and lineage.
8. Model metrics JSON and MLflow run page/log.
9. Prefect flow graph / successful task run and logs.
10. OCI bucket objects after full run.

**Do not use mock screenshots in the final report.** The report contains clearly marked evidence placeholders until actual runs are complete.

## 6. Git hygiene
```bash
git init
git add .
git status
git commit -m "Initial RecoMart DMML pipeline"
```
Do not add `.env`, `~/.oci`, `~/.config/kaggle`, `kaggle.json`, private keys, large raw data or personal credentials. Use DVC for dataset tracking metadata; keep the actual large dataset in OCI Object Storage / approved Drive location.

## 7. Deliverables
- `docs/SUBMISSION_REPORT.docx`: editable report with five-member contribution table.
- `src/`, `scripts/`, `sql/`, `oci/`: implementation.
- `reports/`: generated quality/model reports and screenshots.
- `models/`: trained model artifact after a successful run.
- `logs/`: execution logs.
- `docs/DEMO_SCRIPT.md`: 5–10 minute walkthrough script.
- `docs/FINAL_CHECKLIST.md`: final verification and Drive upload checklist.

## 8. Cost and security
OCI Always Free eligibility and quotas vary by tenancy, region and service availability. Check the OCI Console before provisioning. Set budget/cost alerts, use a private bucket, apply least-privilege IAM policies, and delete temporary compute resources after the demo. Never assume a budget alert is a hard spending cap.
