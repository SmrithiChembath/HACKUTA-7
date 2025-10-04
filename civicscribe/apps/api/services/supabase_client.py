from supabase import create_client, Client
from apps.api.utils.settings import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    return create_client(url, key)
