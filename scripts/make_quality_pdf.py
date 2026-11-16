from pathlib import Path
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
root=Path(__file__).resolve().parents[1]
src=root/"reports"/"data_quality_report.json"
if not src.exists(): raise SystemExit("Run pipeline validation first.")
d=json.loads(src.read_text()); out=root/"reports"/"Data_Quality_Report.pdf"
styles=getSampleStyleSheet(); story=[Paragraph("RecoMart — Data Quality Report",styles["Title"]),Spacer(1,12)]
story.append(Paragraph("Dataset: Retailrocket events.csv | Generated from the actual validation run.",styles["BodyText"]))
rows=[["Check","Observed result"],["Rows",str(d["rows"])],["Missing visitor IDs",str(d["missing_visitorid"])],["Missing item IDs",str(d["missing_itemid"])],["Duplicate rows",str(d["duplicate_rows"])],["Invalid timestamps",str(d["invalid_timestamp"])],["Unknown event types",str(d["unknown_event_types"])],["Status",d["quality_status"]]]
t=Table(rows,colWidths=[220,270]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1F4E79")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.5,colors.grey),("PADDING",(0,0),(-1,-1),7)]))
story.append(t); SimpleDocTemplate(str(out),pagesize=A4).build(story); print(out)
