#!/usr/bin/env python3
"""Build the consolidated RecoMart DMML submission DOCX and PDF."""

from pathlib import Path
from datetime import datetime
import hashlib
import re
import subprocess
import zipfile

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
SCREENSHOTS = REPORTS / "screenshots"
FIGURES = REPORTS / "figures"
LOG_FILE = ROOT / "logs" / "pipeline.log"

OUTPUT_DOCX = REPORTS / "RecoMart_DMML_Final_Submission.docx"
OUTPUT_PDF = REPORTS / "RecoMart_DMML_Final_Submission.pdf"
MANIFEST = REPORTS / "submission_manifest.txt"

DRIVE_FOLDER = (
    "https://drive.google.com/drive/folders/"
    "1Qzdc_dQ33hGSYH1hNuxxnGdodX2xWIEc?usp=sharing"
)
ZIP_NAME = "group1.zip"
VIDEO_STATUS = "Pending recording/upload. Add the final video link to the report after upload."

TEAM = [
    ("Sandeep Kumar Jain", "2025NS04132",
     "Pipeline architecture, implementation and integration; Prefect orchestration; "
     "OCI Object Storage and DVC integration; technical coordination."),
    ("Deepa Mohan", "2025NS04095",
     "Suggested contribution: dataset review, ingestion and validation requirements, "
     "data-quality analysis and documentation."),
    ("Yash Gupta", "2025NS04096",
     "Suggested contribution: data preparation, exploratory data analysis and "
     "interaction-pattern analysis."),
    ("Kothapalli Bhargava Avinash", "2025NS04077",
     "Suggested contribution: feature engineering, feature definitions, warehouse "
     "schema and feature-registry documentation."),
    ("Mumtaz Hanif Shaikh", "2025NS04082",
     "Suggested contribution: recommendation-model methodology, evaluation metrics, "
     "limitations and report/demo support."),
]

EDA_FILES = [
    "event_distribution.png",
    "event_percentage.png",
    "user_activity.png",
    "user_activity_detailed.png",
    "item_activity_distribution.png",
    "item_popularity_top20.png",
    "hourly_activity.png",
    "weekday_activity.png",
]

SCREENSHOT_FILES = [
    "buckets.png",
    "bucket-details.png",
    "object-list.png",
    "raw-object.png",
    "processed-object.png",
    "reports-object.png",
    "prefect_dashboard.png",
    "flows.png",
    "flow-runs.png",
    "prefect_warehouse_dashboard.png",
    "_prefect_warehouse_execution.png",
    "feature_retrieval_demo.png",
]


def add_field(paragraph, field):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = field
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, text, end])


def setup_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    styles = doc.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(9.5)
    styles["Normal"].paragraph_format.space_after = Pt(5)

    for name, size in [("Title", 25), ("Heading 1", 17),
                       ("Heading 2", 13), ("Heading 3", 11)]:
        styles[name].font.name = "Calibri"
        styles[name].font.size = Pt(size)
        styles[name].font.color.rgb = RGBColor(31, 78, 121)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("RecoMart DMML Project  |  Page ")
    add_field(footer, "PAGE")


def add_title(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_para(doc, text="", bold_prefix=None):
    p = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def add_bullet(doc, text):
    doc.add_paragraph(text, style="List Bullet")


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"

    for cell, value in zip(table.rows[0].cells, headers):
        cell.text = str(value)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True

    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc.add_paragraph()


def add_image_if_exists(doc, path, caption, width=6.3):
    if not path.exists():
        add_para(doc, f"[Evidence image not found: {path.relative_to(ROOT)}]")
        return
    doc.add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph(caption)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.italic = True
        run.font.size = Pt(8)


def redact_log(text):
    """Basic redaction for common credentials before embedding logs."""
    patterns = [
        (r"(?i)(aws_secret_access_key|customer_secret_key|password|passwd)"
         r"(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]"),
        (r"(?i)(token|authorization|api_key|secret)"
         r"(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]"),
        (r"(?i)(ocid1\.[a-z0-9._-]+)", "[OCI-ID-REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def add_markdown_appendix(doc, path):
    doc.add_page_break()
    add_title(doc, f"Appendix — {path.name}", 1)

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_code = False

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not line.strip():
            continue

        if in_code:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.name = "Consolas"
            run.font.size = Pt(8)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.lstrip().startswith(("- ", "* ")):
            add_bullet(doc, line.lstrip()[2:])
        elif re.match(r"^\d+[\.\)]\s+", line):
            doc.add_paragraph(re.sub(r"^\d+[\.\)]\s+", "", line),
                              style="List Number")
        else:
            add_para(doc, line)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_report():
    doc = Document()
    setup_document(doc)

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("\n\nBITS PILANI\n").bold = True
    p.add_run("Data Mining and Machine Learning\n").bold = True
    p.add_run("\n")
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("End-to-End Data Management Pipeline\n"
                        "for a Recommendation System")
    run.bold = True
    run.font.size = Pt(23)
    run.font.color.rgb = RGBColor(31, 78, 121)

    p = doc.add_paragraph("\nRecoMart — RetailRocket Dataset")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Final Project Submission")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n")
    add_table(doc, ["Team member", "BITS ID"], [
        (name, student_id) for name, student_id, _ in TEAM
    ])
    p = doc.add_paragraph(
        "\nSubmission date: 22 November 2026\n"
        "Project implementation environment: Linux"
    )
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # Main report
    add_title(doc, "1. Executive Summary")
    add_para(doc,
        "This project implements an end-to-end data management pipeline for "
        "RecoMart, a recommendation-system scenario using the RetailRocket "
        "e-commerce interaction dataset. The implemented workflow covers local "
        "data ingestion, validation, preparation, exploratory analysis, feature "
        "engineering, data versioning and lineage, recommendation-model training, "
        "and analytical warehouse integration. Oracle Cloud Infrastructure (OCI) "
        "Object Storage is used for cloud data storage, while Prefect orchestrates "
        "the pipeline locally."
    )
    add_para(doc,
        "The project demonstrates a reproducible batch-processing workflow over "
        "historical clickstream data. It is not presented as a live streaming "
        "system or as a production-hosted recommendation service."
    )

    add_title(doc, "2. Problem Formulation and Objectives")
    add_para(doc,
        "RecoMart needs a data pipeline that turns raw e-commerce interaction "
        "records and item metadata into validated datasets, reusable features, "
        "and a recommendation-model baseline. The data includes user-item "
        "interactions and product/catalog information."
    )
    add_para(doc, "The project objectives are to:")
    for item in [
        "Ingest and organize source data in a structured raw-data layout.",
        "Validate schema, missing identifiers, duplicate records, event labels "
        "and timestamps.",
        "Prepare clean datasets and examine interaction distributions, item "
        "popularity and matrix sparsity.",
        "Engineer user, item and user-item features and register feature metadata.",
        "Track data lineage and versions using manifests, hashes and DVC.",
        "Train and evaluate a collaborative-filtering recommendation baseline.",
        "Orchestrate the end-to-end batch workflow and store supporting data in OCI."
    ]:
        add_bullet(doc, item)

    add_title(doc, "3. Dataset and Ingestion")
    add_para(doc,
        "The project uses the RetailRocket dataset, including events, item "
        "properties and category-tree data. The events data contains visitor, "
        "item, event-type and timestamp information. Item-property files and "
        "the category tree provide catalog metadata."
    )
    add_para(doc,
        "The ingestion process copies source data into a date-partitioned raw "
        "lake layout and writes a manifest with file metadata and SHA-256 "
        "checksums. OCI Object Storage is used to store raw, processed, feature "
        "and report artifacts. The cloud bucket is private."
    )

    add_title(doc, "4. Data Validation and Preparation")
    add_table(doc, ["Raw event validation check", "Observed result"], [
        ("Rows inspected", "2,756,101"),
        ("Missing visitor IDs", "0"),
        ("Missing item IDs", "0"),
        ("Duplicate rows detected", "460"),
        ("Unknown event labels", "0"),
        ("Invalid timestamps", "0"),
        ("Validation status", "PASS"),
    ])
    add_para(doc,
        "The prepared event dataset contains 2,755,651 rows. The difference "
        "between the raw and prepared row counts is reported as observed; this "
        "report does not attribute the entire difference to duplicate removal "
        "without a verified reconciliation."
    )
    add_para(doc,
        "Preparation includes cleaning and transforming the event data into "
        "analysis-ready files. The validation PDF and JSON report are included "
        "as supporting evidence in the submission package."
    )

    add_title(doc, "5. Exploratory Data Analysis")
    add_table(doc, ["EDA measure", "Observed result"], [
        ("Prepared events", "2,755,651"),
        ("Unique visitors", "1,407,580"),
        ("Unique items", "235,061"),
        ("Unique visitor-item pairs", "2,145,179"),
        ("Interaction matrix sparsity", "Approximately 99.99935%"),
        ("View events", "2,664,219 (96.682%)"),
        ("Add-to-cart events", "68,975 (2.503%)"),
        ("Transaction events", "22,457 (0.815%)"),
    ])
    add_para(doc,
        "The event distribution is dominated by views. User and item activity "
        "show long-tail behaviour, and the interaction matrix is extremely "
        "sparse. These characteristics are important when interpreting "
        "recommendation quality and cold-start limitations."
    )

    for filename in EDA_FILES:
        add_image_if_exists(
            doc, FIGURES / filename,
            f"Exploratory analysis chart: {filename.replace('_', ' ').replace('.png', '')}"
        )

    add_title(doc, "6. Feature Engineering and Feature Registry")
    add_para(doc,
        "The feature workflow generates user-level and item-level activity "
        "features, together with user-item interaction features. The registry "
        "metadata identifies the feature set and its version. Scalar user and "
        "item feature retrieval is implemented with a version check."
    )
    add_para(doc,
        "The demonstrated registry version is 1.0.0. A request for an "
        "unavailable version is rejected. The current scalar retrieval helper "
        "supports visitor-level and item-level feature lookup; it does not "
        "provide scalar retrieval for the two-key visitor-item affinity feature."
    )
    add_image_if_exists(
        doc, SCREENSHOTS / "feature_retrieval_demo.png",
        "Feature retrieval and version-check demonstration"
    )

    add_title(doc, "7. Data Versioning, Lineage and Warehouse")
    add_para(doc,
        "Data versioning and lineage are supported by DVC and project manifests. "
        "The manifests record file metadata and checksums to support traceability. "
        "The project uses a local DuckDB analytical warehouse to integrate "
        "prepared interactions, user features, item features, user-item features, "
        "item properties, category information and model-run metadata."
    )
    add_para(doc,
        "The DuckDB database is a local project artifact and is not included "
        "in the source-code ZIP by default because of its large size. The "
        "underlying data can be restored through the documented DVC workflow "
        "where access to the configured remote is available."
    )

    add_title(doc, "8. Recommendation Model and Evaluation")
    add_para(doc,
        "The implemented recommendation baseline uses TruncatedSVD with "
        "32 components. Interaction weights are used as implicit feedback "
        "(view = 1, add-to-cart = 3, transaction = 5). These are modelling "
        "assumptions, not explicit user ratings. MLflow records the model run."
    )
    add_table(doc, ["Evaluation measure", "Observed value"], [
        ("Precision@10", "0.0007024116"),
        ("Recall@10", "0.0070241161"),
        ("NDCG@10", "0.0043398282"),
        ("Training interactions", "500,000"),
        ("Test candidates evaluated", "106,775"),
        ("Users in evaluation", "420,127"),
        ("Items in evaluation", "131,170"),
        ("SVD components", "32"),
        ("MLflow run ID", "7106876d77f445c7b0580cb7f34d87a8"),
    ])
    add_para(doc,
        "The measured ranking metrics are low and should be interpreted as "
        "baseline results rather than production-ready recommendation quality. "
        "The evaluation uses a temporal holdout strategy and excludes cold-start "
        "users or items outside the training vocabulary."
    )

    add_title(doc, "9. Pipeline Orchestration and Execution Evidence")
    add_para(doc,
        "The Prefect flow is named "
        "'recomart-retailrocket-end-to-end'. A successful local execution "
        "completed nine pipeline tasks in approximately 38 minutes and "
        "26 seconds. The tasks cover ingestion, validation, preparation, "
        "catalog processing, EDA, feature engineering, lineage/versioning, "
        "model training and warehouse integration."
    )
    add_para(doc,
        "Prefect is running locally at http://127.0.0.1:4200. The screenshots "
        "below document the local dashboard, flow and run evidence. The project "
        "does not claim a cloud-hosted Prefect deployment or an active recurring "
        "schedule."
    )

    for filename in [
        "prefect_dashboard.png", "flows.png", "flow-runs.png",
        "prefect_warehouse_dashboard.png", "_prefect_warehouse_execution.png"
    ]:
        add_image_if_exists(
            doc, SCREENSHOTS / filename,
            f"Prefect execution evidence: {filename}"
        )

    add_title(doc, "10. OCI Object Storage Evidence")
    add_para(doc,
        "OCI Object Storage in the ap-mumbai-1 region is used as the cloud "
        "storage component. The project bucket is private. Evidence screenshots "
        "document the bucket, raw objects, processed objects and report objects. "
        "This is an Object Storage integration; no OCI Compute deployment is "
        "claimed."
    )
    for filename in [
        "buckets.png", "bucket-details.png", "object-list.png",
        "raw-object.png", "processed-object.png", "reports-object.png"
    ]:
        add_image_if_exists(
            doc, SCREENSHOTS / filename,
            f"OCI Object Storage evidence: {filename}"
        )

    add_title(doc, "11. Team Contributions")
    add_para(doc,
        "The following allocation is a proposed summary based on the work "
        "distribution discussed by the team. Team members should verify and "
        "approve the individual contribution descriptions before submission."
    )
    add_table(doc, ["Team member", "BITS ID", "Proposed contribution"], TEAM)

    add_title(doc, "12. Limitations and Future Scope")
    for item in [
        "The current workflow processes historical data in batches; live "
        "streaming ingestion is not implemented.",
        "Prefect orchestration and DuckDB execution are local rather than "
        "hosted on OCI Compute.",
        "The recommendation model is a baseline with low ranking metrics and "
        "requires further tuning and comparative evaluation.",
        "Cold-start users and items require additional strategies.",
        "The feature retrieval helper currently demonstrates scalar user and "
        "item lookup, not a complete online feature-serving API.",
        "Future work can add streaming ingestion, scheduled cloud orchestration, "
        "model comparison, richer ranking evaluation, online inference and "
        "production monitoring."
    ]:
        add_bullet(doc, item)

    add_title(doc, "13. Conclusion")
    add_para(doc,
        "The project delivers a modular, reproducible batch data pipeline "
        "covering ingestion through model training and warehouse integration. "
        "It combines data validation, EDA, feature engineering, versioning, "
        "MLflow tracking, Prefect orchestration and OCI Object Storage. The "
        "results provide a working foundation for further recommendation-system "
        "development while making the current implementation boundaries clear."
    )

    add_title(doc, "14. Submission Links and Package")
    add_para(doc, f"Google Drive submission folder: {DRIVE_FOLDER}")
    add_para(doc, f"Source-code ZIP filename: {ZIP_NAME} (to be created/uploaded).")
    add_para(doc, f"Video: {VIDEO_STATUS}")
    add_para(doc,
        "Before final submission, upload group1.zip and the project demo video "
        "to the shared Drive folder, set access as required by the course, and "
        "replace the pending video status with the actual shareable video URL."
    )

    # Append project documentation in full
    for filename in [
        "architecture.md",
        "DATASET_AND_CLOUD_SOURCES.md",
        "EDA_METHODOLOGY.md",
        "DATA_VERSIONING.md",
        "SCHEDULING.md",
        "FINAL_CHECKLIST.md",
        "DEMO_SCRIPT.md",
    ]:
        path = DOCS / filename
        if path.exists():
            add_markdown_appendix(doc, path)

    # Include the EDA report and evidence status notes
    for filename in [
        "EDA_REPORT.md", "EVIDENCE_STATUS.md", "OCI_DEPLOYMENT_EVIDENCE.md"
    ]:
        path = REPORTS / filename
        if path.exists():
            add_markdown_appendix(doc, path)

    # Include the actual pipeline log, with basic credential redaction
    if LOG_FILE.exists():
        doc.add_page_break()
        add_title(doc, "Appendix — Pipeline Execution Log", 1)
        log_text = redact_log(
            LOG_FILE.read_text(encoding="utf-8", errors="replace")
        )
        lines = log_text.splitlines()[-350:]
        p = doc.add_paragraph()
        for line in lines:
            run = p.add_run(line + "\n")
            run.font.name = "Consolas"
            run.font.size = Pt(7)

    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT_DOCX)


def make_manifest():
    candidates = [
        OUTPUT_DOCX, OUTPUT_PDF,
        REPORTS / "Data_Quality_Report.pdf",
        REPORTS / "EDA_Charts.zip",
        REPORTS / "data_quality_report.json",
        REPORTS / "eda_summary.json",
        REPORTS / "extended_eda_summary.json",
        REPORTS / "ingestion_manifest.json",
        REPORTS / "lineage_manifest.json",
        REPORTS / "model_metrics.json",
        LOG_FILE,
    ]
    candidates += [FIGURES / f for f in EDA_FILES]
    candidates += [SCREENSHOTS / f for f in SCREENSHOT_FILES]
    candidates += [DOCS / f for f in [
        "architecture.md", "DATASET_AND_CLOUD_SOURCES.md",
        "EDA_METHODOLOGY.md", "DATA_VERSIONING.md", "SCHEDULING.md",
        "FINAL_CHECKLIST.md", "DEMO_SCRIPT.md"
    ]]

    lines = [
        "RecoMart DMML final submission manifest",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Project root: {ROOT}",
        f"Google Drive folder: {DRIVE_FOLDER}",
        f"Planned source ZIP: {ZIP_NAME}",
        f"Video: {VIDEO_STATUS}",
        "",
        "Files found and SHA-256:",
    ]

    for path in candidates:
        if path.exists() and path.is_file():
            lines.append(f"{sha256(path)}  {path.relative_to(ROOT)}")
        else:
            lines.append(f"MISSING  {path.relative_to(ROOT)}")

    lines += [
        "",
        "Notes:",
        "- The source ZIP has not yet been created.",
        "- The demo video has not yet been uploaded; add its actual URL.",
        "- Verify team contribution descriptions with all members.",
        "- Review the final PDF and ensure no secrets are present.",
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_and_merge_pdf():
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(REPORTS), str(OUTPUT_DOCX)
    ], check=True)

    converted = REPORTS / (OUTPUT_DOCX.stem + ".pdf")
    if not converted.exists():
        raise FileNotFoundError("LibreOffice did not create the report PDF.")

    quality_pdf = REPORTS / "Data_Quality_Report.pdf"
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("pypdf not installed; final PDF will not append the quality PDF.")
        converted.replace(OUTPUT_PDF)
        return

    writer = PdfWriter()
    for page in PdfReader(str(converted)).pages:
        writer.add_page(page)

    if quality_pdf.exists():
        for page in PdfReader(str(quality_pdf)).pages:
            writer.add_page(page)

    with OUTPUT_PDF.open("wb") as f:
        writer.write(f)

    converted.unlink(missing_ok=True)


def main():
    if not (ROOT / "src").exists() or not (ROOT / "reports").exists():
        raise SystemExit("Run this script from inside the RecoMart project.")

    build_report()
    export_and_merge_pdf()
    make_manifest()

    print("\nFINAL SUBMISSION FILES CREATED")
    print(f"DOCX: {OUTPUT_DOCX}")
    print(f"PDF:  {OUTPUT_PDF}")
    print(f"MANIFEST: {MANIFEST}")
    print("\nPlease open and review the PDF before uploading it.")


if __name__ == "__main__":
    main()
