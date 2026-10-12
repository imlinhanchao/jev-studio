from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_admin
from app.schemas.key import KeyCreate, KeyCreatedResponse, KeyResponse, KeyUpdate
from app.services.key_service import KeyService

router = APIRouter(prefix="/keys", tags=["API Keys"], dependencies=[Depends(get_current_admin)])

@router.get("", response_model=list[KeyResponse])
async def list_keys(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Lists all API keys with their token usage and quotas."""
    keys = await KeyService.list_keys(db, skip=skip, limit=limit)
    response_list = []
    for k in keys:
        pct = 0.0
        if k.token_limit > 0:
            pct = round(min(100.0, (k.tokens_used / k.token_limit) * 100), 2)
        response_list.append(
            KeyResponse(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                is_active=k.is_active,
                token_limit=k.token_limit,
                tokens_used=k.tokens_used,
                rate_limit_rpm=k.rate_limit_rpm,
                created_at=k.created_at,
                expires_at=k.expires_at,
                last_used_at=k.last_used_at,
                percent_used=pct,
            )
        )
    return response_list

@router.post("", response_model=KeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    payload: KeyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Creates a new API key. The unmasked raw key is returned ONLY once."""
    db_key, raw_key = await KeyService.create_key(db, payload)
    
    pct = 0.0
    if db_key.token_limit > 0:
        pct = round(min(100.0, (db_key.tokens_used / db_key.token_limit) * 100), 2)

    return KeyCreatedResponse(
        id=db_key.id,
        name=db_key.name,
        key_prefix=db_key.key_prefix,
        is_active=db_key.is_active,
        token_limit=db_key.token_limit,
        tokens_used=db_key.tokens_used,
        rate_limit_rpm=db_key.rate_limit_rpm,
        created_at=db_key.created_at,
        expires_at=db_key.expires_at,
        last_used_at=db_key.last_used_at,
        percent_used=pct,
        raw_key=raw_key,
    )

@router.get("/{key_id}", response_model=KeyResponse)
async def get_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Gets details for a specific API key."""
    db_key = await KeyService.get_by_id(db, key_id)
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    pct = 0.0
    if db_key.token_limit > 0:
        pct = round(min(100.0, (db_key.tokens_used / db_key.token_limit) * 100), 2)

    return KeyResponse(
        id=db_key.id,
        name=db_key.name,
        key_prefix=db_key.key_prefix,
        is_active=db_key.is_active,
        token_limit=db_key.token_limit,
        tokens_used=db_key.tokens_used,
        rate_limit_rpm=db_key.rate_limit_rpm,
        created_at=db_key.created_at,
        expires_at=db_key.expires_at,
        last_used_at=db_key.last_used_at,
        percent_used=pct,
    )

@router.patch("/{key_id}", response_model=KeyResponse)
async def update_key(
    key_id: int,
    payload: KeyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Updates API key status, name, or quota limits."""
    updated = await KeyService.update_key(db, key_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="API Key not found")

    pct = 0.0
    if updated.token_limit > 0:
        pct = round(min(100.0, (updated.tokens_used / updated.token_limit) * 100), 2)

    return KeyResponse(
        id=updated.id,
        name=updated.name,
        key_prefix=updated.key_prefix,
        is_active=updated.is_active,
        token_limit=updated.token_limit,
        tokens_used=updated.tokens_used,
        rate_limit_rpm=updated.rate_limit_rpm,
        created_at=updated.created_at,
        expires_at=updated.expires_at,
        last_used_at=updated.last_used_at,
        percent_used=pct,
    )

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Deletes/revokes an API key."""
    deleted = await KeyService.delete_key(db, key_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="API Key not found")
    return None
