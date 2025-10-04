import json
import time
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from typing import Any, Dict
from apps.api.utils.settings import settings
from apps.api.services.supabase_client import get_supabase

http_bearer = HTTPBearer(auto_error=False)

class AuthUser(Dict[str, Any]):
    pass

async def get_jwks() -> Dict[str, Any]:
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.get(jwks_url)
        r.raise_for_status()
        return r.json()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(http_bearer)) -> AuthUser:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = creds.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = await get_jwks()
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break
        if public_key is None:
            raise HTTPException(status_code=401, detail="Invalid header")

        issuer = settings.AUTH0_ISSUER or f"https://{settings.AUTH0_DOMAIN}/"
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=issuer,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # Upsert user in Supabase
    sb = get_supabase()
    auth0_sub = payload.get("sub")
    email = payload.get("email")
    if auth0_sub:
        sb.table("users").upsert({"auth0_sub": auth0_sub, "email": email}).execute()

    return payload


async def decode_token(token: str) -> Dict[str, Any]:
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = await get_jwks()
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break
        if public_key is None:
            raise HTTPException(status_code=401, detail="Invalid header")
        issuer = settings.AUTH0_ISSUER or f"https://{settings.AUTH0_DOMAIN}/"
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=issuer,
        )
        # Upsert user
        sb = get_supabase()
        auth0_sub = payload.get("sub")
        email = payload.get("email")
        if auth0_sub:
            sb.table("users").upsert({"auth0_sub": auth0_sub, "email": email}).execute()
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
