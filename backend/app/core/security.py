# backend/app/auth.py
import hashlib
import secrets
import time
from typing import Optional

# In-memory хранилище токенов: token -> (admin_id, expires_at)
_admin_tokens: dict[str, tuple[int, float]] = {}
_TOKEN_TTL_SEC = 24 * 3600  # 24 часа


def _hash_password(password: str, salt: str = "ai_traffic_admin") -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def verify_admin_password(password_hash: Optional[str], password: str) -> bool:
    if not password_hash:
        return False
    return secrets.compare_digest(password_hash, _hash_password(password))


def create_admin_token(admin_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _admin_tokens[token] = (admin_id, time.time() + _TOKEN_TTL_SEC)
    return token


def verify_admin_token(token: Optional[str]) -> Optional[int]:
    if not token:
        return None
    now = time.time()
    if token not in _admin_tokens:
        return None
    admin_id, expires = _admin_tokens[token]
    if now > expires:
        del _admin_tokens[token]
        return None
    return admin_id


def hash_for_storage(password: str) -> str:
    return _hash_password(password)
