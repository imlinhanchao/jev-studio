from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.db.base import Base
from app.db.models import APIKey
from app.core.security import hash_api_key

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes tables and seeds a starter developer API key if needed."""
    from sqlalchemy import select
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(APIKey).limit(1))
        existing_key = result.scalar_one_or_none()
        
        if not existing_key:
            # Seed a default demo developer key
            demo_raw_key = f"{settings.API_KEY_PREFIX}demo-master-key-2026"
            key_hash = hash_api_key(demo_raw_key)
            masked_prefix = f"{demo_raw_key[:12]}...{demo_raw_key[-4:]}"
            
            default_key = APIKey(
                name="Default Developer Key",
                key_hash=key_hash,
                key_prefix=masked_prefix,
                token_limit=1000000,  # 1M tokens
                tokens_used=0,
                rate_limit_rpm=300,
                is_active=True,
            )
            session.add(default_key)
            await session.commit()
            print(f"[Init DB] Seeded default master key: {demo_raw_key}")
