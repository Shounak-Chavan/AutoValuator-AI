from fastapi import Header,HTTPException
from app.core.security import verify_token
from app.core.config import settings

from typing import Optional
from fastapi import Header, HTTPException

def get_api_key(api_key: Optional[str] = Header(None)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key required")

    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")


def get_current_user(token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid JWT Token")

    return payload