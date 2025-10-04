from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from apps.api.utils.auth import get_current_user
from apps.api.services.supabase_client import get_supabase
from apps.api.utils.packs import load_pack
from apps.api.services.docai_client import process_income_proof
from apps.api.services.tts_elevenlabs import synthesize_tts
from apps.api.services.storage import upload_bytes_and_get_url
import os

router = APIRouter()

@router.post("/{id}/upload")
async def upload_document(id: str, kind: str = Form(...), file: UploadFile = File(...), user=Depends(get_current_user)):
    sb = get_supabase()
    s = sb.table("sessions").select("*").eq("id", id).single().execute().data
    if not s:
        raise HTTPException(404, "Session not found")
    pack = load_pack(s["pack_slug"])

    file_bytes = await file.read()

    # Store to Supabase Storage
    # Simplify: store path by session id and filename
    storage = sb.storage()
    bucket = os.getenv("SUPABASE_BUCKET", "civicscribe")
    path = f"uploads/{id}/{file.filename}"
    try:
        storage.from_(bucket).upload(path, file_bytes, file_options={"content-type": file.content_type})
    except Exception:
        pass

    # Process with Doc AI
    hint = None
    for req in pack.doc_requirements:
        if req.get("kind") == kind:
            hint = req.get("docai_hint")
            break

    parsed = await process_income_proof(file_bytes, hint=hint) if kind == "income_proof" else {}

    # Update answers if recognized
    updated_keys = []
    summary = "Uploaded."
    if kind == "income_proof" and parsed.get("monthly_income"):
        sb.table("answers").upsert({"session_id": id, "key": "monthly_income", "value": parsed["monthly_income"]}).execute()
        updated_keys.append("monthly_income")
        if parsed.get("latest_date"):
            summary = f"I see your monthly income is ${parsed['monthly_income']:.0f} from {parsed['latest_date']}."
        else:
            summary = f"I see your monthly income is ${parsed['monthly_income']:.0f}."

    # Record upload row
    sb.table("uploads").insert({"session_id": id, "kind": kind, "file_path": path, "doc_json": parsed}).execute()

    # TTS
    try:
        audio_bytes = await synthesize_tts(summary)
        audio_url = upload_bytes_and_get_url(audio_bytes, "audio/mpeg", prefix=f"tts/{id}/")
    except Exception:
        audio_url = None

    sb.table("messages").insert({"session_id": id, "role": "assistant", "text": summary, "audio_url": audio_url}).execute()

    return {"summary": summary, "updated_keys": updated_keys}
