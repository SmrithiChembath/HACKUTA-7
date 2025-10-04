from apps.api.services.supabase_client import get_supabase
from apps.api.utils.settings import settings
import uuid

def upload_bytes_and_get_url(content: bytes, content_type: str, prefix: str = "audio/") -> str | None:
    try:
        sb = get_supabase()
        bucket = settings.SUPABASE_BUCKET
        filename = f"{prefix}{uuid.uuid4()}.bin"
        sb.storage().from_(bucket).upload(filename, content, file_options={"content-type": content_type})
        pub = sb.storage().from_(bucket).get_public_url(filename)
        return pub
    except Exception:
        return None
