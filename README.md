# RecoMart -- End-to-End Data Management Pipeline for a Recommendation System

**Course:** Data Mining & Machine Learning (DMML)\
**Project:** RecoMart\
**Team:** Group 1\
**Repository:** `dmml-assignment-oracle`

RecoMart is an end-to-end data management and recommendation-system
project built using the RetailRocket e-commerce events dataset. The
project demonstrates data ingestion, validation, preparation,
exploratory analysis, feature engineering, data/version lineage, model
training and evaluation, experiment tracking, workflow orchestration,
cloud object storage, and analytical warehousing.

This README is intended for the **Source Code** folder and the
`group1.zip` source-code archive.

------------------------------------------------------------------------

## 1. Project overview

The pipeline processes RetailRocket event data and builds an
interaction-based recommendation model.

The main stages are:

1.  **Ingestion** -- load the source event and item metadata files.
2.  **Data validation** -- check required fields, missing identifiers,
    duplicates, event labels, and timestamp validity.
3.  **Preparation** -- clean and prepare interaction data for downstream
    analysis and modelling.
4.  **Catalog processing** -- process item metadata and category
    information.
5.  **Exploratory data analysis (EDA)** -- examine event distributions,
    user activity, item popularity, and time-based patterns.
6.  **Feature engineering** -- generate user, item, and user-item
    features and maintain a feature registry.
7.  **Versioning and lineage** -- record dataset and pipeline artefacts
    to support traceability.
8.  **Model training and evaluation** -- train a TruncatedSVD-based
    recommendation model and calculate ranking and reconstruction
    metrics.
9.  **Experiment tracking** -- record model parameters and metrics with
    MLflow.
10. **Workflow orchestration** -- organise pipeline execution with
    Prefect.
11. **Analytical warehouse** -- load prepared data and feature tables
    into DuckDB.
12. **Cloud object storage** -- use Oracle Cloud Infrastructure (OCI)
    Object Storage for project data and artefacts.

### Model configuration

The recommendation model uses **TruncatedSVD with 32 components**. The
interaction matrix uses event weights:

  Event type      Weight
  ------------- --------
  View                 1
  Add to cart          3
  Transaction          5

These weights give stronger influence to higher-intent interactions.

### Recorded evaluation results

The final recorded model run is identified by:

`d96e8139d6aa4a0fa71dfe894c463124`

The metrics recorded for that run are:

  Metric                  Recorded value
  --------------------- ----------------
  Precision@10                 0.0007024
  Recall@10                    0.0070241
  NDCG@10                      0.0043398
  Reconstruction RMSE          0.0024734

These are the results of the project baseline and should be interpreted
in the context of the dataset, candidate set, and evaluation approach.
They should not be represented as production-level recommendation
performance.

------------------------------------------------------------------------

## 2. Technology stack

-   **Python** -- pipeline implementation and model development
-   **Pandas / NumPy / SciPy / scikit-learn** -- data processing and
    machine learning
-   **DuckDB** -- analytical warehouse
-   **DVC** -- data and artefact versioning
-   **MLflow** -- experiment tracking
-   **Prefect** -- workflow orchestration
-   **Oracle Cloud Infrastructure (OCI) Object Storage** -- cloud object
    storage
-   **DBeaver** -- optional graphical interface for inspecting the
    DuckDB database

The pipeline, Prefect server, MLflow tracking UI, and DuckDB warehouse
are run locally in the demonstrated setup. OCI Object Storage is the
cloud storage component.

------------------------------------------------------------------------

## 3. Project structure

The source archive should preserve the project-relative structure. The
following is a guide to the main directories and files; optional files
may differ between packaged versions.

``` text
RecoMart_DMML_OCI/
├── src/                         # Pipeline modules and model implementation
├── scripts/                     # Entry-point and utility scripts
├── sql/                         # Warehouse schema and SQL
├── data/
│   └── features/                 # Feature registry and feature metadata
├── reports/                      # Supporting reports, metrics, figures, screenshots
├── models/                       # Trained model artefact, if included
├── database/                     # DuckDB warehouse, if included
├── docs/                         # Supporting project documentation, if included
├── .dvc/                         # DVC metadata (do not include credentials)
├── .dvcignore
├── .gitignore
├── dvc.yaml                      # If present in the packaged project
├── requirements.txt
├── README.md
└── ...
```

### Important directories

  -----------------------------------------------------------------------
  Directory                           Purpose
  ----------------------------------- -----------------------------------
  `src/`                              Reusable Python modules for
                                      ingestion, validation, preparation,
                                      EDA, features, versioning,
                                      training, orchestration, storage,
                                      and warehouse operations

  `scripts/`                          Commands and helper scripts for
                                      running the pipeline, reports,
                                      periodic processing, and data
                                      utilities

  `sql/`                              SQL schema and warehouse-related
                                      SQL

  `data/features/`                    Feature registry metadata

  `reports/`                          Data-quality evidence, EDA outputs,
                                      metrics, manifests, plots, and
                                      screenshots

  `models/`                           Trained recommendation model, when
                                      distributed

  `database/`                         DuckDB database, when distributed
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Dataset

The project uses the **RetailRocket e-commerce events dataset**. The
source files used in the project include:

-   `events.csv`
-   `category_tree.csv`
-   `item_properties_part1.csv`
-   `item_properties_part2.csv`

The raw dataset is large. To keep the source ZIP and Git repository
manageable, raw CSV files and generated large artefacts may be stored
separately or managed through DVC rather than copied into the ZIP.

### If the raw dataset is not included

1.  Obtain the same RetailRocket dataset version used for the project.
2.  Place the source CSV files in the dataset location expected by the
    project configuration.
3.  Check the paths configured in the ingestion module or project
    configuration before running the pipeline.
4.  If the project is configured for DVC, configure access to the DVC
    remote and retrieve the tracked data with:

``` bash
dvc pull
```

DVC remote access requires the appropriate credentials and
configuration. Do not put OCI access keys, secret keys, authentication
tokens, or private configuration files in the ZIP or public Git
repository.

------------------------------------------------------------------------

## 5. Setup

### Requirements

-   Linux, macOS, or Windows with a compatible Python environment
-   Python version compatible with the packages in `requirements.txt`
-   Git
-   Access to the dataset
-   DVC and OCI configuration if retrieving data from the configured
    remote
-   Optional: DuckDB CLI or DBeaver for inspecting the warehouse

The project was developed in a Linux environment using Python 3.13.5.
Package compatibility should be checked against the supplied
`requirements.txt`.

### Create and activate a virtual environment

From the project root:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If a dependency is not listed in `requirements.txt`, install it only
after checking the relevant module and the project's tested package
versions.

------------------------------------------------------------------------

## 6. Run the pipeline

From the project root, activate the virtual environment and run:

``` bash
source .venv/bin/activate
python scripts/run_pipeline.py
```

The script is the project pipeline entry point. Check its command-line
options and the project configuration before running it if your local
dataset or storage paths differ.

**Note:** The complete pipeline can take a substantial amount of time
because it processes a large interaction dataset and builds the
analytical and modelling artefacts. Do not start a fresh full run merely
to view the saved reports or demonstration evidence.

------------------------------------------------------------------------

## 7. Prefect -- workflow orchestration

The project uses Prefect to organise pipeline stages into a workflow.

Start the local Prefect server in one terminal:

``` bash
source .venv/bin/activate
prefect server start
```

In a second terminal, from the project root:

``` bash
source .venv/bin/activate
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Open the Prefect interface:

<http://127.0.0.1:4200>

The demonstrated end-to-end flow is named:

`recomart-retailrocket-end-to-end`

The flow contains nine main tasks covering ingestion, validation,
preparation, catalog processing, EDA, feature generation,
versioning/lineage, model training, and DuckDB integration.

The demonstrated setup uses a locally started Prefect server. It should
not be described as a deployed cloud orchestration service or as an
automatically scheduled production pipeline.

------------------------------------------------------------------------

## 8. MLflow -- experiment tracking

The project stores MLflow tracking data in a local SQLite database named
`mlflow.db`.

Start the MLflow UI from the project root:

``` bash
source .venv/bin/activate
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5001
```

Open:

<http://127.0.0.1:5001>

Select the **Default** experiment and inspect the recorded runs. The
final run used in the report is:

`d96e8139d6aa4a0fa71dfe894c463124`

The MLflow UI displays recorded experiment parameters and metrics. It
does not mean model training is currently running.

If `mlflow.db` is not included in the distributed archive, the UI will
not contain the original recorded runs until the tracking database is
supplied or the experiment is run again. Do not substitute an older
`mlruns/` file-store directory for the SQLite tracking database used by
the final run.

------------------------------------------------------------------------

## 9. DuckDB -- analytical warehouse

The project uses DuckDB as a local analytical warehouse. The
demonstrated database path is:

``` text
database/recomart_warehouse.duckdb
```

Open this file using DBeaver or another DuckDB-compatible client.

Example query to count interactions by event type:

``` sql
SELECT
    event_type,
    COUNT(*) AS total_events
FROM fact_interaction
GROUP BY event_type
ORDER BY total_events DESC;
```

The demonstrated warehouse includes interaction, user-feature,
item-feature, user-item-feature, item-property, category-tree, and
model-run tables.

The DuckDB database is a generated binary artefact and is large. Include
it in the ZIP only if the submission size limit permits. Otherwise,
include the SQL/schema and the instructions needed to regenerate it.

------------------------------------------------------------------------

## 10. OCI Object Storage

The project uses **Oracle Cloud Infrastructure (OCI) Object Storage**.
The demonstrated bucket is:

-   **Bucket:** `recomart-dmml-data`
-   **Region:** `ap-mumbai-1`
-   **Storage namespace:** `bmyxec10ufou`

The DVC remote uses the S3-compatible interface to communicate with OCI
Object Storage. This does **not** mean that the project uses Amazon S3.

Access to the bucket is private and depends on the configured OCI
credentials and permissions. Do not include private keys, OCI
configuration files containing secrets, access tokens, or credentials in
the source archive.

A reviewer without access to the OCI tenancy can still inspect the
source code and locally supplied project evidence, but cannot retrieve
private bucket objects.

------------------------------------------------------------------------

## 11. Reports and supporting evidence

The `reports/` directory contains supporting project outputs, which may
include:

-   Data-quality report and validation evidence
-   EDA reports and plots
-   Model metrics
-   Dataset/version manifests
-   Architecture diagram
-   DuckDB and MLflow screenshots
-   Other generated pipeline evidence

The final academic submission report and demonstration video should be
placed in their designated submission folders. The source ZIP may
include technical supporting evidence, but it does not need to contain
duplicate copies of every top-level submission document.

------------------------------------------------------------------------

## 12. Reproducibility and packaging notes

The source archive should include the code and configuration needed to
understand and reproduce the project, while avoiding machine-specific
and sensitive files.

### Include

-   `src/`
-   `scripts/`
-   `sql/`
-   `requirements.txt`
-   `README.md`
-   Relevant project configuration files
-   DVC metadata required to identify tracked data
-   `data/features/feature_registry.json`
-   Supporting reports, metrics, manifests, plots, and screenshots
-   The trained model and DuckDB database only if practical within the
    submission size limit

### Exclude

-   `.venv/`
-   `.git/`
-   `__pycache__/` and `*.pyc`
-   Temporary files, editor caches, and logs
-   MLflow temporary or obsolete tracking directories
-   OCI private keys, credentials, tokens, and secret configuration
-   Local machine-specific absolute paths
-   Large raw data files if they are separately supplied or retrievable
    through DVC

Before creating the ZIP, inspect `.gitignore` and DVC configuration to
ensure that required source files are not accidentally omitted and that
secrets are not included.

------------------------------------------------------------------------

## 13. Known implementation boundaries

For an accurate description of the delivered project:

-   OCI Object Storage is the cloud storage component; pipeline
    execution and the demonstrated warehouse/model workflow are local.
-   Prefect is demonstrated using a local server.
-   MLflow records completed experiment runs; the UI is a tracking
    interface, not a live training monitor.
-   DuckDB is a local analytical warehouse; the project does not claim a
    deployed BI dashboard.
-   The periodic-processing script supports processing a historical
    snapshot; it should not be described as a live streaming system or
    an active recurring production schedule.
-   The TruncatedSVD model and reported ranking metrics represent a
    baseline implementation and should be evaluated accordingly.

------------------------------------------------------------------------

## 14. Team

**DMML -- Group 1**

  Name                          Student ID
  ----------------------------- -------------
  Sandeep Kumar Jain            2025NS04132
  Deepa Mohan                   2025NS04095
  Yash Gupta                    2025NS04096
  Kothapalli Bhargava Avinash   2025NS04077
  Mumtaz Hanif Shaikh           2025NS04082

------------------------------------------------------------------------

## 15. Repository

GitHub repository:

<https://github.com/sjainuni/dmml-assignment-oracle>

For questions about the project implementation, refer first to the
relevant modules in `src/`, execution utilities in `scripts/`, and
warehouse definitions in `sql/`.
