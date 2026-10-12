from typing import Optional
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.db.models import APIKey
from app.services.key_service import KeyService

security_bearer = HTTPBearer(auto_error=False)

async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
) -> dict:
    """
    Validates JWT Admin session token.
    Raises 401 if missing, invalid or expired.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要管理员登录凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭据已过期或无效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username or username != settings.ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户身份验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"username": username, "role": "admin"}

async def get_current_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """
    Validates API Key from Authorization Bearer header or X-API-Key header.
    Throws 401 if missing/invalid, 403 if inactive/expired/quota exceeded.
    """
    raw_key = None
    if "x-api-key" in request.headers:
        raw_key = request.headers.get("x-api-key")
    elif credentials and credentials.credentials:
        if credentials.credentials.startswith(settings.API_KEY_PREFIX):
            raw_key = credentials.credentials

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing. Please provide via 'X-API-Key' or 'Authorization: Bearer <key>' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = await KeyService.get_by_raw_key(db, raw_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key.",
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is inactive or revoked.",
        )

    if api_key.is_expired():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key has expired.",
        )

    if not api_key.has_quota(required_tokens=1):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"API Key token quota exceeded. Allocated: {api_key.token_limit}, Used: {api_key.tokens_used}.",
        )

    return api_key

async def get_optional_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[APIKey]:
    """
    Optional API Key verification. Allows playground to run if no key provided,
    using system default quota.
    """
    raw_key = None
    if "x-api-key" in request.headers:
        raw_key = request.headers.get("x-api-key")
    elif credentials and credentials.credentials:
        if credentials.credentials.startswith(settings.API_KEY_PREFIX):
            raw_key = credentials.credentials

    if not raw_key:
        return None

    return await KeyService.get_by_raw_key(db, raw_key)
