from fastapi import APIRouter, Depends, HTTPException, Response
from apps.api.utils.auth import get_current_user
from apps.api.services.supabase_client import get_supabase
from apps.api.utils.packs import load_pack
from apps.api.services.pdf_fill import fill_pdf_acroform, overlay_text
import os

router = APIRouter()

@router.post("/{id}/render")
async def render_pdf(id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    s = sb.table("sessions").select("*").eq("id", id).single().execute().data
    if not s:
        raise HTTPException(404, "Session not found")
    pack = load_pack(s["pack_slug"])

    ans_rows = sb.table("answers").select("key,value").eq("session_id", id).execute().data or []
    answers = {r["key"]: r["value"] for r in ans_rows}

    # Read template
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../packs/{pack.slug}/form.pdf"))
    if not os.path.exists(template_path):
        raise HTTPException(500, "Template missing")
    with open(template_path, "rb") as f:
        template_bytes = f.read()

    mapping = pack.mapping()

    try:
        pdf_bytes = fill_pdf_acroform(template_bytes, mapping, answers)
    except Exception:
        # overlay fallback: place some key fields in default spots on first page
        default_overlay = {0: [
            {"x": 100, "y": 700, "text": answers.get("full_name", "")},
            {"x": 100, "y": 680, "text": answers.get("date_of_birth", "")},
            {"x": 100, "y": 660, "text": str(answers.get("household_size", ""))},
            {"x": 100, "y": 640, "text": answers.get("home_address", "")},
            {"x": 100, "y": 620, "text": answers.get("phone", "")},
            {"x": 100, "y": 600, "text": answers.get("email", "")},
            {"x": 100, "y": 580, "text": str(answers.get("monthly_income", ""))},
            {"x": 100, "y": 560, "text": answers.get("ssn_last4_optional", "")},
        ]}
        pdf_bytes = overlay_text(template_bytes, default_overlay)

    headers = {"Content-Type": "application/pdf", "Content-Disposition": "attachment; filename=completed.pdf"}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
