from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database.mongo import get_collection
from app.repositories.mongo_repository import MongoRepository
from app.schemas.settings import SettingsPayload, recommended_settings_payload


class SettingsService:
    def __init__(self):
        self.settings = MongoRepository(get_collection("settings"))

    def upsert_for_user(self, user_id: str, payload: dict) -> dict:
        normalized = SettingsPayload.model_validate(payload).model_dump()
        current = self.get_for_user(user_id)
        document = {
            "user_id": user_id,
            "gaze": normalized["gaze"],
            "gestures": normalized["gestures"],
            "scroll": normalized["scroll"],
            "updated_at": datetime.now(timezone.utc),
            "version": (current["version"] if current else 0) + 1,
        }
        if current:
            return self.settings.upsert({"user_id": user_id}, document)
        return self.settings.upsert(
            {"user_id": user_id},
            {**document, "_id": f"settings-{user_id}"},
        )

    def get_for_user(self, user_id: str) -> dict | None:
        document = self.settings.get_by_query({"user_id": user_id})
        if document is None:
            return None
        gaze = dict(document.get("gaze", {}))
        gaze["calibration_data"] = {}
        normalized = SettingsPayload.model_validate(
            {
                "gaze": gaze,
                "gestures": document.get("gestures", {}),
                "scroll": document.get("scroll", {}),
            }
        ).model_dump()
        return {**document, **normalized}

    def get_for_device(self, user_id: str, calibration_data: dict[str, Any]) -> dict:
        settings = self.get_for_user(user_id)
        if settings is None:
            settings = {
                "user_id": user_id,
                **recommended_settings_payload(),
                "updated_at": None,
                "version": 0,
            }
        return {
            **settings,
            "gaze": {**settings["gaze"], "calibration_data": calibration_data},
        }


def get_settings_service() -> SettingsService:
    return SettingsService()
