from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.database.mongo import get_collection

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    settings = get_settings()
    settings.validate_runtime_configuration()
    if expires_delta is None:
        expires_delta = settings.access_token_expire_minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    token_id = str(uuid4())
    claims = {"sub": subject, "jti": token_id, "exp": expires_at}
    token = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    get_collection("sessions").insert_one(
        {"_id": token_id, "user_id": subject, "active": True, "expires_at": expires_at}
    )
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def revoke_access_token(token: str) -> bool:
    claims = decode_access_token(token)
    token_id = claims.get("jti")
    if not token_id:
        return False
    result = get_collection("sessions").update_one(
        {"_id": token_id, "active": True},
        {"$set": {"active": False, "revoked_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count == 1
