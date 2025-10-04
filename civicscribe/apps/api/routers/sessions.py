from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from apps.api.utils.auth import get_current_user
from apps.api.services.supabase_client import get_supabase
from apps.api.utils.packs import load_pack
from apps.api.services.gemini_client import normalize_field
from apps.api.services.tts_elevenlabs import synthesize_tts
from apps.api.services.storage import upload_bytes_and_get_url
from apps.api.utils.settings import settings
import uuid
import json

router = APIRouter()


def session_progress(pack, answers: Dict[str, Any]):
    total_required = sum(1 for k in pack.flow_order if pack.fields.get(k, {}).get("required", False))
    filled_required = sum(1 for k in pack.flow_order if pack.fields.get(k, {}).get("required", False) and k in answers)
    pct = int((filled_required / max(total_required, 1)) * 100)
    next_key = None
    for k in pack.flow_order:
        if pack.fields.get(k, {}).get("required", False) and k not in answers:
            next_key = k
            break
    return next_key, pct


@router.post("")
async def create_session(payload: Dict[str, Any], user=Depends(get_current_user)):
    pack_slug = payload.get("pack_slug")
    if not pack_slug:
        raise HTTPException(400, "pack_slug required")
    pack = load_pack(pack_slug)
    sb = get_supabase()

    # fetch user id
    auth0_sub = user.get("sub")
    user_row = sb.table("users").select("id").eq("auth0_sub", auth0_sub).single().execute().data
    user_id = user_row.get("id")

    res = sb.table("sessions").insert({"user_id": user_id, "pack_slug": pack_slug}).execute()
    session = res.data[0]

    first_key = pack.flow_order[0] if pack.flow_order else None
    first_label = pack.fields.get(first_key, {}).get("label", "") if first_key else ""
    welcome = pack.welcome
    first_message = f"{welcome} {first_label}".strip()

    # TTS
    try:
        audio_bytes = await synthesize_tts(first_message)
        audio_url = upload_bytes_and_get_url(audio_bytes, "audio/mpeg", prefix=f"tts/{session['id']}/")
    except Exception:
        audio_url = None

    # Save assistant message
    sb.table("messages").insert({"session_id": session["id"], "role": "assistant", "text": first_message, "audio_url": audio_url}).execute()

    return {"session_id": session["id"], "first_message": first_message, "first_audio_url": audio_url}


@router.get("/{id}")
async def get_session_status(id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    s = sb.table("sessions").select("*", count="exact").eq("id", id).single().execute().data
    if not s:
        raise HTTPException(404, "Not found")
    pack = load_pack(s["pack_slug"])
    ans_rows = sb.table("answers").select("key,value").eq("session_id", id).execute().data or []
    answers = {r["key"]: r["value"] for r in ans_rows}
    next_key, pct = session_progress(pack, answers)
    return {"filled_keys": list(answers.keys()), "pending_key": next_key, "progress": pct}


@router.post("/{id}/answer")
async def post_answer(id: str, payload: Dict[str, Any], user=Depends(get_current_user)):
    key = payload.get("key")
    raw_text = payload.get("raw_text", "")
    if not key:
        raise HTTPException(400, "key required")

    sb = get_supabase()
    s = sb.table("sessions").select("*").eq("id", id).single().execute().data
    if not s:
        raise HTTPException(404, "Session not found")
    pack = load_pack(s["pack_slug"])

    f = pack.fields.get(key)
    if not f:
        raise HTTPException(400, "Unknown field")

    # Normalize via Gemini
    note_text = None
    try:
        norm = await normalize_field(pack.title, key, f.get("label", key), f.get("type", "text"), raw_text, note_text)
    except Exception:
        norm = {"normalized": raw_text.strip(), "explain": "Recorded your answer.", "needs_clarification": False}

    # Save answer
    sb.table("answers").upsert({"session_id": id, "key": key, "value": norm["normalized"]}).execute()

    # Determine next field
    ans_rows = sb.table("answers").select("key,value").eq("session_id", id).execute().data or []
    answers = {r["key"]: r["value"] for r in ans_rows}

    if norm.get("needs_clarification"):
        assistant_text = f"{norm.get('explain', '')} Could you clarify: {f.get('label', key)}"
        next_key = key
    else:
        next_key, pct = session_progress(pack, answers)
        if next_key:
            next_label = pack.fields.get(next_key, {}).get("label", next_key)
            # If next question is income and doc requirement exists, suggest upload
            if next_key == 'monthly_income':
                assistant_text = "Thank you. Please upload your most recent Social Security benefit statement, or tell me your monthly income."
            else:
                assistant_text = f"Thank you. {next_label}"
        else:
            assistant_text = pack.completion.get("summary_text", "All set.")

    # TTS
    try:
        audio_bytes = await synthesize_tts(assistant_text)
        audio_url = upload_bytes_and_get_url(audio_bytes, "audio/mpeg", prefix=f"tts/{id}/")
    except Exception:
        audio_url = None

    # Save messages
    sb.table("messages").insert([
        {"session_id": id, "role": "user", "text": raw_text},
        {"session_id": id, "role": "assistant", "text": assistant_text, "audio_url": audio_url, "meta": {"explain": norm.get("explain")}},
    ]).execute()

    progress = session_progress(pack, answers)[1]
    return {"assistant_text": assistant_text, "audio_url": audio_url, "next_key": next_key, "progress": progress}


@router.get("/{id}/messages")
async def get_messages(id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    rows = sb.table("messages").select("*").eq("session_id", id).order("created_at", desc=True).limit(50).execute().data or []
    return list(reversed(rows))
