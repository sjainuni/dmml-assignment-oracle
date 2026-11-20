
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CHART_ZIP = REPORTS / "EDA_Charts.zip"
OUTPUT = REPORTS / "RecoMart_DMML_Final_Report.docx"

doc = Document()

# Page and typography
section = doc.sections[0]
section.top_margin = Inches(0.7)
section.bottom_margin = Inches(0.7)
section.left_margin = Inches(0.8)
section.right_margin = Inches(0.8)

styles = doc.styles
styles["Normal"].font.name = "Calibri"
styles["Normal"].font.size = Pt(10)
styles["Normal"].paragraph_format.space_after = Pt(6)

for name, size in [("Title", 26), ("Heading 1", 17), ("Heading 2", 13)]:
    styles[name].font.name = "Calibri"
    styles[name].font.size = Pt(size)
    styles[name].font.color.rgb = RGBColor(31, 78, 121)

def heading(text, level=1):
    doc.add_heading(text, level=level)

def para(text, bold_start=None):
    p = doc.add_paragraph()
    if bold_start and text.startswith(bold_start):
        p.add_run(bold_start).bold = True
        p.add_run(text[len(bold_start):])
    else:
        p.add_run(text)
    return p

def bullet(text):
    doc.add_paragraph(text, style="List Bullet")

def table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Shading Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, value in zip(t.rows[0].cells, headers):
        cell.text = str(value)
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for row in rows:
        cells = t.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc.add_paragraph()
    return t

def add_chart_from_zip(zf, filename, caption):
    matches = [n for n in zf.namelist()
               if Path(n).name.lower() == filename.lower()]
    if not matches:
        para(f"[Chart not found in EDA_Charts.zip: {filename}]")
        return
    data = BytesIO(zf.read(matches[0]))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(data, width=Inches(5.8))
    cp = doc.add_paragraph(caption)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in cp.runs:
        r.italic = True
        r.font.size = Pt(9)

def add_screenshot(path, caption):
    if path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(5.8))
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cp.runs:
            r.italic = True
            r.font.size = Pt(9)

# COVER
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("\n\nBITS PILANI\n").bold = True
p.add_run("Data Mining and Machine Learning (DMML)\n")
p.add_run("Semester 1 – 2026\n\n")

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("End-to-End Data Management Pipeline\nfor a Recommendation System")
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = RGBColor(31, 78, 121)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("\nRecoMart – Retailrocket Dataset\n\n")
p.add_run("Cloud Storage: Oracle Cloud Infrastructure (OCI)\n")
p.add_run("Pipeline Orchestration: Prefect\n")
p.add_run("Feature Warehouse: DuckDB\n")
p.add_run("Recommendation Model: Truncated SVD\n\n")
p.add_run("Submission Date: 22 November 2026\n")

doc.add_page_break()

# TEAM
heading("Team Members and Responsibilities")
table(
    ["Team member", "Student ID", "Proposed responsibility"],
    [
        ["Sandeep Kumar Jain", "2025NS04132",
         "End-to-end pipeline architecture, implementation and integration; Prefect orchestration; OCI and DVC integration; technical coordination."],
        ["Deepa Mohan", "2025NS04095",
         "Dataset review, ingestion and validation requirements, data-quality analysis and documentation."],
        ["Yash Gupta", "2025NS04096",
         "Data preparation, exploratory data analysis and interpretation of user/item interaction patterns."],
        ["Kothapalli Bhargava Avinash", "2025NS04077",
         "Feature engineering, feature definitions, warehouse schema and feature-registry documentation."],
        ["Mumtaz Hanif Shaikh", "2025NS04082",
         "Recommendation-model methodology, evaluation metrics, limitations and report/presentation support."],
    ]
)
para("Responsibility note: The allocation above is a suggested division prepared for this report. "
     "The team should review and confirm that it accurately reflects each member's actual contribution before submission.")

# EXECUTIVE SUMMARY
heading("1. Executive Summary")
para("This project implements an end-to-end batch data-management pipeline for a recommendation-system "
     "use case using the Retailrocket e-commerce interaction dataset. The pipeline covers data ingestion, "
     "raw-data storage, validation, preparation, exploratory analysis, feature engineering, feature metadata "
     "and retrieval, data versioning, model training, experiment tracking and warehouse integration.")
para("The implementation uses Oracle Cloud Infrastructure Object Storage for private cloud object storage, "
     "DVC for data versioning, Prefect for local workflow orchestration, DuckDB for analytical storage, "
     "and a Truncated SVD collaborative-filtering baseline for recommendation modelling.")
para("The work is a reproducible batch-processing prototype over a historical dataset. It is not a live "
     "streaming system and does not claim to be a production online recommendation service.")

heading("2. Problem Formulation and Objectives")
para("RecoMart needs to transform raw customer-item interaction records into reliable, reusable data "
     "assets and a baseline recommendation model. Raw events alone are not sufficient: they must be "
     "validated, cleaned, explored and transformed into user, item and interaction features before "
     "they can support model training and evaluation.")
heading("2.1 Project objectives", 2)
for x in [
    "Ingest and organize source data from the Retailrocket dataset.",
    "Validate data quality, including missing identifiers, duplicate records, event labels and timestamps.",
    "Prepare analytical data and perform exploratory data analysis.",
    "Engineer reusable user, item and user-item features.",
    "Store analytical tables and feature outputs in a queryable warehouse.",
    "Maintain data versions and lineage information.",
    "Train and evaluate a collaborative-filtering recommendation baseline.",
    "Orchestrate the pipeline and retain execution evidence."
]:
    bullet(x)

heading("2.2 Expected outputs", 2)
for x in [
    "Validated and prepared interaction data.",
    "EDA summaries and visualizations.",
    "Feature datasets and a versioned feature metadata registry.",
    "Data lineage and version manifests.",
    "A trained recommendation-model artifact and evaluation metrics.",
    "A DuckDB analytical warehouse and Prefect execution evidence."
]:
    bullet(x)

# DATA
heading("3. Dataset and Data Sources")
para("The project uses the Retailrocket e-commerce dataset. The source files include event interactions, "
     "a category hierarchy and item-property records.")
table(
    ["Source file", "Purpose"],
    [
        ["events.csv", "Visitor-item events, including views, add-to-cart actions and transactions."],
        ["category_tree.csv", "Category hierarchy and parent-child category relationships."],
        ["item_properties_part1.csv", "Item property records."],
        ["item_properties_part2.csv", "Additional item property records."]
    ]
)
para("The events dataset contains visitor identifiers, item identifiers, event types and timestamps. "
     "Item-property data provides additional product attributes, while the category tree provides "
     "categorical hierarchy information.")

# ARCHITECTURE / INGESTION
heading("4. Pipeline Architecture and Ingestion")
para("The implementation is organized into modular Python components under src/. The main stages are "
     "ingestion, validation, preparation, catalog processing, EDA, feature engineering, versioning, "
     "model training and warehouse integration.")
table(
    ["Stage", "Implementation"],
    [
        ["Ingestion", "src/ingest.py; local source files are copied into a date-partitioned raw data lake with a manifest and SHA-256 checksums."],
        ["Validation", "src/validate.py; checks schema, missing visitor/item identifiers, duplicates, event labels and timestamp validity."],
        ["Preparation", "src/prepare.py; chunk-based processing and cleaned Parquet output."],
        ["Catalog", "src/catalog.py; item-property and category-tree processing."],
        ["EDA", "src/eda.py and scripts/generate_eda_plots.py; summary statistics and charts."],
        ["Features", "src/features.py; user, item and user-item feature generation."],
        ["Versioning", "src/versioning.py; checksums, manifests and lineage metadata."],
        ["Training", "src/train.py; Truncated SVD training and evaluation."],
        ["Warehouse", "src/warehouse.py; integration of prepared data and feature outputs into DuckDB."]
    ]
)
para("The dataset is a historical snapshot. The pipeline supports batch reprocessing; it should not be "
     "described as a live event-streaming ingestion service.")

# STORAGE
heading("5. Raw Storage and Cloud Integration")
para("Raw source data and generated project assets are organized locally and synchronized to a private "
     "Oracle Cloud Infrastructure Object Storage bucket named recomart-dmml-data in the ap-mumbai-1 region.")
para("The OCI bucket is private. DVC uses an OCI S3-compatible object-storage endpoint as its remote "
     "storage location. DVC push and pull were tested, including restoration of the four source files "
     "into a fresh working copy.")
para("The cloud component in this implementation is object storage. Pipeline execution, Prefect, "
     "DuckDB and model training were run locally; this project does not claim an OCI Compute deployment.")

# VALIDATION
heading("6. Data Validation and Quality")
table(
    ["Validation check", "Observed result"],
    [
        ["Raw event rows", "2,756,101"],
        ["Missing visitor IDs", "0"],
        ["Missing item IDs", "0"],
        ["Duplicate rows reported", "460"],
        ["Unknown event types", "0"],
        ["Invalid timestamps", "0"],
        ["Overall validation", "PASS"]
    ]
)
para("The prepared interaction dataset contains 2,755,651 rows. This is the reported prepared-data "
     "count; the difference from the raw row count should not be attributed solely to duplicate removal "
     "without a separate reconciliation of every preparation step.")
para("A data-quality PDF report is generated as part of the project evidence. The report should be "
     "reviewed alongside the validation output when presenting the implementation.")

# PREPARATION / EDA
heading("7. Data Preparation and Exploratory Data Analysis")
para("The preparation stage produces cleaned interaction data in Parquet format. The prepared dataset "
     "contains 2,755,651 interactions, 1,407,580 unique visitors, 235,061 unique items and "
     "2,145,179 unique visitor-item pairs.")
para("The visitor-item interaction matrix is extremely sparse, with reported sparsity of approximately "
     "99.99935%. This is an important characteristic of the dataset and a challenge for collaborative filtering.")
table(
    ["Event type", "Count", "Share"],
    [
        ["View", "2,664,219", "96.682%"],
        ["Add to cart", "68,975", "2.503%"],
        ["Transaction", "22,457", "0.815%"]
    ]
)
para("The event distribution is highly imbalanced: views dominate the dataset, while add-to-cart and "
     "transaction events are much less frequent. User activity is also long-tailed: the median user "
     "has one recorded event, while the 99th percentile has 13 events. Item activity is similarly "
     "skewed, with a median of three events and a 99th percentile of 143 events.")
para("Hourly activity peaks around 20:00 UTC. These times are in UTC and should not be interpreted as "
     "local time without conversion.")

heading("7.1 EDA visualizations", 2)
if CHART_ZIP.exists():
    with ZipFile(CHART_ZIP) as zf:
        charts = [
            ("event_distribution.png", "Figure 1. Interaction counts by event type."),
            ("event_percentage.png", "Figure 2. Relative share of each event type."),
            ("user_activity.png", "Figure 3. User activity distribution."),
            ("user_activity_detailed.png", "Figure 4. Detailed user activity distribution."),
            ("item_activity_distribution.png", "Figure 5. Item activity distribution."),
            ("item_popularity_top20.png", "Figure 6. Twenty most frequently interacted-with items."),
            ("hourly_activity.png", "Figure 7. Interaction activity by hour (UTC)."),
            ("weekday_activity.png", "Figure 8. Interaction activity by weekday.")
        ]
        for filename, caption in charts:
            add_chart_from_zip(zf, filename, caption)
else:
    para("EDA_Charts.zip was not found. Copy the chart archive into reports/ and regenerate this report.")

# FEATURES / WAREHOUSE
heading("8. Feature Engineering and Warehouse")
para("The feature-engineering stage generates user-level, item-level and user-item interaction features. "
     "Examples include user event count, number of unique items per user, mean event weight, item event "
     "count, unique visitors per item and visitor-item affinity.")
para("The feature registry is stored in data/features/feature_registry.json. It identifies the feature "
     "set, version, feature names, entities and metadata. The retrieval function checks the requested "
     "version before returning a scalar user or item feature.")
para("A retrieval demonstration was performed for visitor ID 1 and item ID 461686. The item event-count "
     "example returned 2,975. A request for version 9.9.9 was rejected, demonstrating version checking. "
     "Scalar retrieval is supported for visitor and item entities; visitor-item affinity requires a "
     "two-key retrieval path and should not be described as supported by the scalar function.")
heading("8.1 DuckDB warehouse", 2)
table(
    ["Warehouse table", "Rows"],
    [
        ["fact_interaction", "2,755,651"],
        ["feature_user", "1,407,580"],
        ["feature_item", "235,061"],
        ["feature_user_item", "2,145,179"],
        ["item_properties", "20,275,902"],
        ["category_tree", "1,669"],
        ["model_run", "1"]
    ]
)
para("The local DuckDB database provides a queryable analytical layer for interaction facts, feature "
     "tables, item properties, category information and model-run metadata. The warehouse database file "
     "is retained locally and is not committed to Git because of its size.")

# VERSIONING
heading("9. Data Versioning and Lineage")
para("DVC is used to version the source datasets and synchronize them with the OCI S3-compatible remote. "
     "The project also creates SHA-256 manifests and lineage metadata for processed outputs. This "
     "provides a way to identify source files, track data artifacts and support reproducible processing.")
para("The DVC remote was pushed successfully and a fresh-copy pull was tested. Credentials and access "
     "configuration are kept outside source control; secrets must not be included in the submitted ZIP "
     "or screenshots.")

# MODEL
heading("10. Recommendation Model and Evaluation")
para("The project trains a collaborative-filtering baseline using Truncated SVD with 32 components. "
     "Interaction strengths are derived from event weights: view = 1, add-to-cart = 3 and transaction = 5. "
     "These are modelling assumptions, not explicit user ratings.")
para("The evaluation uses a temporal holdout approach in which the latest eligible interaction per user "
     "is held out. The reported ranking metrics are Precision@10, Recall@10 and NDCG@10.")
table(
    ["Metric", "Observed value"],
    [
        ["Precision@10", "0.0007024"],
        ["Recall@10", "0.0070241"],
        ["NDCG@10", "0.0043398"],
        ["SVD components", "32"],
        ["Training interactions", "500,000"],
        ["Test candidates evaluated", "106,775"],
        ["MLflow run ID", "7106876d77f445c7b0580cb7f34d87a8"]
    ]
)
para("The ranking metrics are low. The model should therefore be presented as an experimental baseline "
     "that demonstrates the training and evaluation workflow, not as a production-ready recommender. "
     "The extreme sparsity, popularity imbalance, implicit-feedback assumptions and cold-start cases "
     "are important limitations.")

# ORCHESTRATION
heading("11. Workflow Orchestration and Monitoring")
para("Prefect orchestrates the project as a multi-stage flow named "
     "recomart-retailrocket-end-to-end. The successful local execution covered ingestion, validation, "
     "preparation, catalog processing, EDA, feature engineering, versioning, model training and warehouse "
     "integration.")
para("A recorded full run completed nine task stages in approximately 38 minutes and 26 seconds. "
     "Prefect logs and dashboard screenshots provide execution evidence. The Prefect server and flow "
     "were run locally; no cloud-hosted Prefect deployment or recurring production schedule is claimed.")

# RESULTS
heading("12. Results and Discussion")
for x in [
    "A repeatable batch pipeline was implemented across the main data-management stages.",
    "Raw data was validated and prepared into an analytical Parquet dataset.",
    "EDA quantified event imbalance, long-tail user/item activity and extreme matrix sparsity.",
    "User, item and user-item features were created and integrated into DuckDB.",
    "A versioned feature registry and retrieval demonstration were implemented.",
    "DVC and OCI Object Storage were used for data versioning and private cloud storage.",
    "A Truncated SVD baseline was trained and evaluated, with metrics tracked through MLflow.",
    "Prefect execution evidence was captured for the end-to-end workflow."
]:
    bullet(x)

heading("13. Limitations and Future Improvements")
for x in [
    "Improve recommendation quality through implicit-feedback algorithms such as ALS, BPR or item-item nearest neighbours.",
    "Compare popularity, content-based and collaborative-filtering baselines.",
    "Improve cold-start handling for new users and items.",
    "Tune hyperparameters and evaluate with additional ranking metrics and multiple temporal splits.",
    "Add a two-key retrieval interface for visitor-item affinity.",
    "Add automated scheduled execution and alerting if recurring operation is required.",
    "Add an online inference API and monitoring before any production deployment.",
    "Reconcile raw-to-prepared row counts with a detailed audit of filtering and deduplication."
]:
    bullet(x)

heading("14. Conclusion")
para("The RecoMart project demonstrates an end-to-end data-management workflow for a recommendation "
     "system using the Retailrocket dataset. It combines data ingestion, validation, preparation, EDA, "
     "feature engineering, feature metadata and retrieval, data versioning, cloud object storage, model "
     "training, experiment tracking, warehouse integration and workflow orchestration.")
para("The project provides a reproducible foundation and identifies the practical challenges of "
     "recommendation modelling on sparse implicit-feedback data. Further model improvements and "
     "production-serving capabilities remain future work.")

# EVIDENCE APPENDIX
heading("Appendix A. Implementation Evidence")
para("The following screenshots should be included if present in reports/screenshots/. They document "
     "cloud storage, orchestration and feature retrieval.")
screenshots = [
    ("bucket-details.png", "OCI bucket configuration and details."),
    ("buckets.png", "OCI bucket listing."),
    ("object-list.png", "Objects stored in the OCI bucket."),
    ("raw-object.png", "Raw dataset objects in cloud storage."),
    ("processed-object.png", "Processed dataset object in cloud storage."),
    ("reports-object.png", "Project reports stored in cloud storage."),
    ("prefect_dashboard.png", "Prefect dashboard."),
    ("flows(1).png", "Prefect flow definition."),
    ("flow-runs.png", "Prefect flow execution history."),
    ("prefect_warehouse_dashboard.png", "Prefect and warehouse execution evidence."),
    ("_prefect_warehouse_execution.png", "Warehouse integration execution."),
    ("feature_retrieval_demo.png", "Feature retrieval and version-check demonstration.")
]
for filename, caption in screenshots:
    add_screenshot(REPORTS / "screenshots" / filename, caption)

heading("Appendix B. Submission Packaging Checklist")
for x in [
    "Export this DOCX to PDF and review page breaks, charts and screenshots.",
    "Include source code, SQL, documentation and configuration examples in the ZIP.",
    "Include model artifacts and data only where permitted and practical; avoid committing secrets.",
    "Include the DVC configuration needed to reproduce data retrieval, without credentials.",
    "Upload the demonstration video and source ZIP to Google Drive.",
    "Set Drive permissions so the evaluator can access the files using a BITS ID.",
    "Confirm all team contributions and student IDs before final submission."
]:
    bullet(x)

# Footer
for sec in doc.sections:
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("RecoMart | DMML End-to-End Data Management Pipeline | BITS Pilani")

REPORTS.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(f"Created: {OUTPUT}")
print(f"Size: {OUTPUT.stat().st_size:,} bytes")
