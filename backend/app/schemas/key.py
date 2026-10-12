from datetime import datetime
from pydantic import BaseModel, Field

class KeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Friendly identifier for the API key")
    token_limit: int = Field(default=500000, ge=0, description="Quota in tokens (0 for unlimited)")
    rate_limit_rpm: int = Field(default=120, ge=1, le=10000, description="Rate limit (requests/min)")
    expires_in_days: int | None = Field(default=None, ge=1, description="Expiry duration in days (optional)")

class KeyUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    token_limit: int | None = Field(default=None, ge=0)
    rate_limit_rpm: int | None = Field(default=None, ge=1)

class KeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    is_active: bool
    token_limit: int
    tokens_used: int
    rate_limit_rpm: int
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    percent_used: float = 0.0

    class Config:
        from_attributes = True

class KeyCreatedResponse(KeyResponse):
    raw_key: str = Field(..., description="The unmasked full API key. Save this as it is only displayed once.")
