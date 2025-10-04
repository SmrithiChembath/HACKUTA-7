from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
from typing import Dict, Any, List, Union


def fill_pdf_acroform(template_bytes: bytes, mapping: Dict[str, Union[str, List[str]]], answers: Dict[str, Any]) -> bytes:
    reader = PdfReader(BytesIO(template_bytes))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Set AcroForm fields
    for key, field_names in mapping.items():
        if key not in answers or not field_names:
            continue
        value = str(answers[key])
        targets: List[str] = field_names if isinstance(field_names, list) else [field_names]
        for pdf_field in targets:
            try:
                writer.update_page_form_field_values(writer.pages, {pdf_field: value})
            except Exception:
                # ignore missing fields; fallback overlay will handle
                pass

    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def overlay_text(template_bytes: bytes, overlay_items: Dict[int, Dict[str, Any]]) -> bytes:
    # overlay_items: page_index -> { (x,y,text) }
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    for page_index, items in overlay_items.items():
        for it in items:
            c.setFont("Helvetica", 10)
            c.drawString(it.get("x", 72), it.get("y", 720), str(it.get("text", "")))
        c.showPage()
    c.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)

    base = PdfReader(BytesIO(template_bytes))
    writer = PdfWriter()
    for i, page in enumerate(base.pages):
        page.merge_page(overlay_pdf.pages[i] if i < len(overlay_pdf.pages) else overlay_pdf.pages[-1])
        writer.add_page(page)

    out = BytesIO()
    writer.write(out)
    return out.getvalue()
