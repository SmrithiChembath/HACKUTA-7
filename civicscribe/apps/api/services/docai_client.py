from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from apps.api.utils.settings import settings
import os
import re
from datetime import datetime
from io import BytesIO

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.GOOGLE_PROJECT_ID or "")

async def process_income_proof(file_bytes: bytes, hint: str | None = None) -> dict:
    client_options = ClientOptions(api_endpoint=f"{settings.GOOGLE_LOCATION}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    name = client.processor_path(settings.GOOGLE_PROJECT_ID, settings.GOOGLE_LOCATION, settings.DOCAI_PROCESSOR_ID)
    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(content=file_bytes, mime_type="application/pdf"),
    )
    try:
        result = client.process_document(request=request)
        doc = result.document
        text = doc.text or ""
    except Exception:
        # Fallback: naive regex
        text = ocr_fallback(file_bytes)

    amount = extract_currency(text)
    date = extract_date(text)
    return {"monthly_income": amount, "latest_date": date, "raw_text": text[:2000]}


def ocr_fallback(file_bytes: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(BytesIO(file_bytes))
    except Exception:
        return ""


def extract_currency(text: str) -> float | None:
    matches = re.findall(r"\$\s?([0-9,]+(?:\.[0-9]{2})?)", text)
    if not matches:
        return None
    # assume the largest as monthly gross
    nums = [float(m.replace(",", "")) for m in matches]
    return max(nums) if nums else None


def extract_date(text: str) -> str | None:
    # find most recent date
    patterns = [
        r"(\b\w+\s+\d{1,2},\s+\d{4}\b)",  # Month 1, 2024
        r"(\b\d{1,2}/\d{1,2}/\d{2,4}\b)",     # 01/15/2024
    ]
    found = []
    for p in patterns:
        found += re.findall(p, text)
    def to_dt(s: str):
        for fmt in ("%B %d, %Y", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        return None
    dated = [(s, to_dt(s)) for s in found]
    dated = [x for x in dated if x[1] is not None]
    dated.sort(key=lambda x: x[1], reverse=True)
    return dated[0][0] if dated else None
