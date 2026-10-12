from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, hash_api_key
from app.db.models import APIKey
from app.schemas.key import KeyCreate, KeyUpdate

class KeyService:
    @staticmethod
    async def create_key(db: AsyncSession, data: KeyCreate) -> tuple[APIKey, str]:
        raw_key, key_hash, masked_prefix = generate_api_key()
        
        expires_at = None
        if data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)
            
        db_key = APIKey(
            name=data.name,
            key_hash=key_hash,
            key_prefix=masked_prefix,
            token_limit=data.token_limit,
            tokens_used=0,
            rate_limit_rpm=data.rate_limit_rpm,
            is_active=True,
            expires_at=expires_at,
        )
        db.add(db_key)
        await db.flush()
        await db.refresh(db_key)
        return db_key, raw_key

    @staticmethod
    async def list_keys(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[APIKey]:
        result = await db.execute(
            select(APIKey).order_by(desc(APIKey.created_at)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, key_id: int) -> Optional[APIKey]:
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_raw_key(db: AsyncSession, raw_key: str) -> Optional[APIKey]:
        hashed = hash_api_key(raw_key)
        result = await db.execute(select(APIKey).where(APIKey.key_hash == hashed))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_key(db: AsyncSession, key_id: int, data: KeyUpdate) -> Optional[APIKey]:
        db_key = await KeyService.get_by_id(db, key_id)
        if not db_key:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_key, field, value)

        await db.flush()
        await db.refresh(db_key)
        return db_key

    @staticmethod
    async def delete_key(db: AsyncSession, key_id: int) -> bool:
        db_key = await KeyService.get_by_id(db, key_id)
        if not db_key:
            return False
        await db.delete(db_key)
        return True

    @staticmethod
    async def increment_usage(db: AsyncSession, key_id: int, tokens: int):
        stmt = (
            update(APIKey)
            .where(APIKey.id == key_id)
            .values(
                tokens_used=APIKey.tokens_used + tokens,
                last_used_at=datetime.utcnow(),
            )
        )
        await db.execute(stmt)
