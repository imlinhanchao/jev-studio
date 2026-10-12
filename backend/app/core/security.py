import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt

from app.core.config import settings

def generate_api_key() -> tuple[str, str, str]:
    """
    Generates a new API key.
    Returns:
        (raw_key, key_hash, masked_prefix)
    Example:
        raw_key: jev-live-9f2b84719c2e4f0a9d18...
        key_hash: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
        masked_prefix: jev-live-9f2b...4f0a
    """
    random_part = secrets.token_hex(20)
    raw_key = f"{settings.API_KEY_PREFIX}{random_part}"
    key_hash = hash_api_key(raw_key)
    masked_prefix = f"{raw_key[:12]}...{raw_key[-4:]}"
    return raw_key, key_hash, masked_prefix

def hash_api_key(raw_key: str) -> str:
    """Computes SHA-256 hash of the API key for secure storage."""
    return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()

def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verifies a raw API key against a stored hash."""
    return hash_api_key(raw_key) == stored_hash

def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Verifies admin credentials configured in .env.
    Uses secrets.compare_digest to protect against timing attacks.
    """
    is_user_valid = secrets.compare_digest(username.strip(), settings.ADMIN_USERNAME.strip())
    is_pass_valid = secrets.compare_digest(password.strip(), settings.ADMIN_PASSWORD.strip())
    return is_user_valid and is_pass_valid

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token for admin sessions."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
