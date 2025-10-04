import google.generativeai as genai
import json
from apps.api.utils.settings import settings

SYSTEM_PROMPT = (
    "You assist people in filling forms. Use respectful, plain language. "
    "You do NOT provide legal advice. Always return VALID JSON ONLY with keys: "
    "normalized, explain, needs_clarification."
)

genai.configure(api_key=settings.GEMINI_API_KEY)

def mask_pii(raw_text: str) -> str:
    import re
    text = raw_text
    # Email
    text = re.sub(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+)", r"\1***\2", text)
    # Phone (simple)
    text = re.sub(r"(\d{3})[- .]?(\d{3})[- .]?(\d{4})", r"***-***-\3", text)
    # SSN last4
    text = re.sub(r"\b\d{3}-?\d{2}-?(\d{4})\b", r"***-**-\1", text)
    # Address: mask leading number block (e.g., 742 -> 700–900)
    def mask_address(match):
        try:
            num = int(match.group(1))
            base = (num // 100) * 100
            return f"{base}\u2013{base+200} "
        except:
            return match.group(0)
    text = re.sub(r"\b(\d{3,5})\s+(?=[A-Za-z])", mask_address, text)
    return text

async def normalize_field(pack_title: str, key: str, label: str, ftype: str, raw_text: str, notes: str | None) -> dict:
    model = genai.GenerativeModel(settings.GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)
    masked = mask_pii(raw_text)
    user_prompt = (
        f"FORM: {pack_title}\n"
        f"FIELD:\n  key: {key}\n  label: {label}\n  type: {ftype}\n"
        f"USER_INPUT (PII masked): {masked}\n"
        + (f"NOTES (optional): {notes}\n" if notes else "") +
        "\nReturn JSON ONLY:\n{\n  \"normalized\": \"<short machine-friendly value>\",\n  \"explain\": \"<=2 short sentences in plain language\",\n  \"needs_clarification\": false\n}\n"
    )
    for attempt in range(2):
        try:
            resp = await model.generate_content_async(user_prompt, generation_config={"response_mime_type": "application/json"})
            text = resp.text
            data = json.loads(text)
            if not all(k in data for k in ("normalized", "explain", "needs_clarification")):
                raise ValueError("Missing keys")
            return data
        except Exception:
            if attempt == 0:
                user_prompt += "\nONLY JSON. NO PROSE."
            else:
                return {"normalized": raw_text.strip(), "explain": "Recorded your answer.", "needs_clarification": False}

