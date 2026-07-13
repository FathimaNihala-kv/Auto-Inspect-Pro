from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.utils import ImageReader
import io
try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None

from config import REPORTS_DIR, UPLOADS_DIR


def create_report_pdf(inspection_id, vehicle, inspection, items, photos):
    report_path = REPORTS_DIR / f"inspection_{inspection_id}_report.pdf"
    doc = SimpleDocTemplate(str(report_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    ACCENT_COLOR = colors.HexColor("#2E7D7D")
    LIGHT_HEADER = colors.HexColor("#e6f6f6")
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, leading=24, textColor=ACCENT_COLOR, spaceAfter=12)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#374151"), spaceAfter=8)
    story = []

    story.append(Paragraph("AutoInspect Pro Report", title_style))
    story.append(Paragraph(f"Inspection ID: {inspection_id}", subtitle_style))
    story.append(Paragraph(f"Vehicle: {vehicle.get('make')} {vehicle.get('model')} ({vehicle.get('year')})", normal))
    story.append(Paragraph(f"Customer: {vehicle.get('customer_name')}", normal))
    story.append(Paragraph(f"Inspector: {inspection.get('inspector_name')}", normal))
    story.append(Spacer(1, 12))

    data = [
        ["Field", "Value"],
        ["VIN", vehicle.get("vin", "")],
        ["Registration", vehicle.get("registration_number", "")],
        ["Odometer", vehicle.get("odometer", "")],
        ["Fuel Type", vehicle.get("fuel_type", "")],
        ["Transmission", vehicle.get("transmission", "")],
        ["Inspection Date", vehicle.get("inspection_date", "")],
        ["Overall Score", str(inspection.get("overall_score", 0))],
        ["Status", inspection.get("overall_status", "Pending")],
    ]
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Inspection Findings", subtitle_style))
    if items:
        rows = [["Category", "Part", "Condition", "Severity", "Remarks"]]
        for item in items:
            rows.append([item.get("category", ""), item.get("part_name", ""), item.get("condition", ""), item.get("severity", ""), item.get("remarks", "")])
        findings_table = Table(rows, repeatRows=1)
        findings_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_HEADER),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(findings_table)
    else:
        story.append(Paragraph("No findings recorded.", normal))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Inspector Notes", subtitle_style))
    story.append(Paragraph(inspection.get("remarks", "No summary notes were provided."), normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Inspection Photos", title_style))
    story.append(Spacer(1, 6))
    if photos:
        for idx, photo in enumerate(photos, start=1):
            raw_path = photo.get("file_path", "")
            file_path = Path(raw_path)
            if not file_path.exists() and raw_path:
                file_path = UPLOADS_DIR / Path(raw_path).name
            filename = Path(raw_path).name if raw_path else ""
            caption = photo.get("caption", "") or filename or f"Photo {idx}"

            # Try to gather item remarks by matching part name, category or filename
            remarks_list = [item.get("remarks", "") for item in items if (
                item.get("part_name") and (item.get("part_name") == caption or item.get("part_name") == filename)
                ) or (
                item.get("category") and (item.get("category") == caption or item.get("category") == photo.get("category") or item.get("category") == filename)
                )]
            remarks_text = "; ".join([r for r in remarks_list if r]) if remarks_list else "No item remarks available."

            # Display filename and caption so users can identify images even if captions are missing
            story.append(Paragraph(f"Photo {idx}: {caption}", styles["Heading4"]))
            story.append(Paragraph(f"Filename: {filename}", normal))

            # Resolve alternate upload locations
            if not file_path.exists() and UPLOADS_DIR:
                alt = UPLOADS_DIR / filename
                if alt.exists():
                    file_path = alt

            if file_path.exists():
                # Try direct insertion first
                try:
                    story.append(RLImage(str(file_path), width=300, height=200))
                except Exception:
                    # Fallback: try loading with PIL and create an ImageReader
                    if PILImage:
                        try:
                            with PILImage.open(file_path) as im:
                                im_conv = im.convert("RGB")
                                # preserve aspect ratio within box 300x200
                                max_w, max_h = 300, 200
                                w, h = im_conv.size
                                ratio = min(max_w / w, max_h / h)
                                new_w = int(w * ratio)
                                new_h = int(h * ratio)
                                im_resized = im_conv.resize((new_w, new_h))
                                buf = io.BytesIO()
                                im_resized.save(buf, format="JPEG")
                                buf.seek(0)
                                img_reader = ImageReader(buf)
                                story.append(RLImage(img_reader, width=new_w, height=new_h))
                        except Exception:
                            story.append(Paragraph(f"Photo could not be rendered: {file_path.name}", normal))
                    else:
                        story.append(Paragraph(f"Photo could not be rendered: {file_path.name}", normal))
            else:
                story.append(Paragraph(f"Missing photo file: {file_path}", normal))
            story.append(Paragraph(f"Item Remarks: {remarks_text}", normal))
            story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No photos uploaded for this inspection.", normal))
    story.append(Spacer(1, 12))
    story.append(Paragraph("End of Report", subtitle_style))
    story.append(Paragraph("Thank you for using AutoInspect Pro.", normal))

    doc.build(story)
    return report_path
