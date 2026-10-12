from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    key_prefix = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Token Quota & Tracking
    token_limit = Column(Integer, default=500000, nullable=False)  # Quota
    tokens_used = Column(Integer, default=0, nullable=False)        # Accumulated tokens
    rate_limit_rpm = Column(Integer, default=120, nullable=False)   # Requests per minute
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    usage_logs = relationship("TokenUsageLog", back_populates="api_key", cascade="all, delete-orphan")

    def has_quota(self, required_tokens: int = 1) -> bool:
        if self.token_limit <= 0:  # Unlimited
            return True
        return (self.tokens_used + required_tokens) <= self.token_limit

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class TokenUsageLog(Base):
    __tablename__ = "token_usage_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(64), index=True, nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=True)
    
    endpoint = Column(String(100), default="/api/v1/decision/predict", nullable=False)
    decision_types = Column(String(100), default="choice", nullable=False) # e.g. "choice,noul,score"
    
    input_length = Column(Integer, default=0, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    decision_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    latency_ms = Column(Float, default=0.0, nullable=False)
    status_code = Column(Integer, default=200, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Relationships
    api_key = relationship("APIKey", back_populates="usage_logs")

# Index for fast analytics queries
Index("idx_usage_key_created", TokenUsageLog.api_key_id, TokenUsageLog.created_at)
