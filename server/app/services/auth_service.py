from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from app.core.security import create_access_token, hash_password, verify_password
from app.database.mongo import get_collection
from app.repositories.mongo_repository import MongoRepository


class AuthService:
    def __init__(self):
        self.users = MongoRepository(get_collection("users"))

    def register(self, username: str, email: str, password: str) -> dict:
        normalized_email = email.strip().lower()
        if self.users.get_by_query({"username": username}):
            raise ValueError("Username already exists")
        if self.users.get_by_query({"email": normalized_email}):
            raise ValueError("Email already exists")

        now = datetime.now(timezone.utc)
        user = {
            "_id": str(uuid4()),
            "username": username,
            "email": normalized_email,
            "password_hash": hash_password(password),
            "created_at": now,
            "updated_at": now,
        }
        try:
            self.users.insert(user)
        except DuplicateKeyError as exc:
            raise ValueError("Username or email already exists") from exc
        return user

    def login(self, username: str, password: str) -> dict:
        user = self.users.get_by_query({"username": username})
        if user is None or not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        return {"user": user, "token": create_access_token(user["_id"])}

    def get_user(self, user_id: str) -> dict | None:
        return self.users.get_by_query({"_id": user_id})


def get_auth_service() -> AuthService:
    return AuthService()
