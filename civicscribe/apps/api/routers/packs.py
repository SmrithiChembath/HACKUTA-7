from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from apps.api.utils.packs import list_packs, load_pack

router = APIRouter()

@router.get("")
async def get_packs() -> List[Dict[str, Any]]:
    return list_packs()

@router.get("/{slug}/notes")
async def get_pack_notes(slug: str):
    pack = load_pack(slug)
    return pack.notes
