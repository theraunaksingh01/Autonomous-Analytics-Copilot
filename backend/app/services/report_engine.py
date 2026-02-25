from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import ListFlowable, ListItem
import os


def generate_pdf_report(file_name, insights, logs):
    os.makedirs("reports", exist_ok=True)

    file_path = f"reports/{file_name}_report.pdf"
    doc = SimpleDocTemplate(file_path)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>AI Dataset Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Overview
    elements.append(Paragraph("<b>Dataset Overview</b>", styles["Heading2"]))
    elements.append(Paragraph(
        f"{insights['overview']['rows']} rows · {insights['overview']['columns']} columns",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # Key Findings
    elements.append(Paragraph("<b>Key Findings</b>", styles["Heading2"]))
    findings = [ListItem(Paragraph(f, styles["Normal"])) for f in insights.get("key_findings", [])]
    elements.append(ListFlowable(findings, bulletType='bullet'))
    elements.append(Spacer(1, 0.3 * inch))

    # Recent Queries
    elements.append(Paragraph("<b>Recent Analysis Queries</b>", styles["Heading2"]))

    for log in logs:
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"<b>Q:</b> {log.question}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Answer:</b> {log.answer}", styles["Normal"]))
        elements.append(Paragraph(
            f"Confidence: {round(log.confidence*100,2)}% · Latency: {log.latency}s",
            styles["Normal"]
        ))

    doc.build(elements)

    return file_path