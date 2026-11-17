from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from app.database.mongo import get_collection
from app.repositories.mongo_repository import MongoRepository

PAIRING_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
PAIRING_CODE_LIFETIME = timedelta(minutes=10)


class DeviceService:
    def __init__(self):
        self.devices = MongoRepository(get_collection("devices"))
        self.pairing_codes = MongoRepository(get_collection("pairing_codes"))

    @staticmethod
    def _device_id(installation_id: str, os_user_identifier: str) -> str:
        identity = f"{installation_id}\0{os_user_identifier}".encode("utf-8")
        return hashlib.sha256(identity).hexdigest()

    @staticmethod
    def _key_hash(device_key: str) -> str:
        return hashlib.sha256(device_key.encode("utf-8")).hexdigest()

    @staticmethod
    def _public_device(device: dict) -> dict:
        return {
            key: value
            for key, value in device.items()
            if key not in {"device_key_hash", "calibration_data"}
        }

    def start_pairing(self, payload: dict) -> dict:
        device_id = self._device_id(payload["installation_id"], payload["os_user_identifier"])
        existing = self.devices.get_by_query({"_id": device_id})
        if existing:
            if secrets.compare_digest(
                existing.get("device_key_hash", ""),
                self._key_hash(payload["device_key"]),
            ):
                raise ValueError("This desktop is already paired")
            raise PermissionError("This installation is already associated with an account")

        now = datetime.now(timezone.utc)
        code = "".join(secrets.choice(PAIRING_CODE_ALPHABET) for _ in range(12))
        pairing = {
            "_id": device_id,
            "device_id": device_id,
            "pairing_code_hash": hashlib.sha256(code.encode("ascii")).hexdigest(),
            "device_key_hash": self._key_hash(payload["device_key"]),
            "os_user_identifier": payload["os_user_identifier"],
            "installation_id": payload["installation_id"],
            "device_name": payload["device_name"],
            "desktop_version": payload["desktop_version"],
            "user_id": None,
            "created_at": now,
            "expires_at": now + PAIRING_CODE_LIFETIME,
        }
        self.pairing_codes.upsert({"_id": device_id}, pairing)
        return {
            "device_id": device_id,
            "pairing_code": code,
            "expires_at": pairing["expires_at"],
        }

    def approve_pairing(self, user_id: str, pairing_code: str) -> dict:
        normalized_code = pairing_code.replace(" ", "").upper()
        code_hash = hashlib.sha256(normalized_code.encode("ascii")).hexdigest()
        now = datetime.now(timezone.utc)
        pairing = self.pairing_codes.collection.find_one_and_update(
            {
                "pairing_code_hash": code_hash,
                "user_id": None,
                "expires_at": {"$gt": now},
            },
            {"$set": {"user_id": user_id, "pairing_state": "approving"}},
            return_document=ReturnDocument.AFTER,
        )
        if pairing is None:
            raise ValueError("Pairing code is invalid, expired, or already used")

        previous = self.devices.get_by_query({"_id": pairing["device_id"]})
        document = {
            "_id": pairing["device_id"],
            "user_id": user_id,
            "os_user_identifier": pairing["os_user_identifier"],
            "installation_id": pairing["installation_id"],
            "device_name": pairing["device_name"],
            "desktop_version": pairing["desktop_version"],
            "device_key_hash": pairing["device_key_hash"],
            "last_seen": now,
            "created_at": previous["created_at"] if previous else now,
        }
        try:
            saved = self.devices.upsert({"_id": pairing["device_id"]}, document)
        except PyMongoError:
            self.pairing_codes.collection.update_one(
                {"_id": pairing["_id"], "user_id": user_id, "pairing_state": "approving"},
                {"$set": {"user_id": None}, "$unset": {"pairing_state": ""}},
            )
            raise
        self.pairing_codes.collection.update_one(
            {"_id": pairing["_id"], "user_id": user_id, "pairing_state": "approving"},
            {"$set": {"pairing_state": "paired", "paired_at": now}},
        )
        return self._public_device(saved)

    def poll_pairing(self, device_id: str, device_key: str) -> dict:
        key_hash = self._key_hash(device_key)
        pairing = self.pairing_codes.get_by_query({"_id": device_id})
        if pairing is None:
            device = self.devices.get_by_query({"_id": device_id})
            if device and secrets.compare_digest(device.get("device_key_hash", ""), key_hash):
                return {"status": "paired"}
            return {"status": "expired"}
        if not secrets.compare_digest(pairing["device_key_hash"], key_hash):
            raise PermissionError("Invalid device credentials")
        if pairing["expires_at"] <= datetime.now(timezone.utc) and pairing["user_id"] is None:
            return {"status": "expired"}
        if pairing.get("pairing_state") != "paired":
            return {"status": "pending"}

        self.devices.collection.update_one(
            {"_id": device_id, "device_key_hash": key_hash},
            {"$set": {"last_seen": datetime.now(timezone.utc)}},
        )
        return {"status": "paired"}

    def register_device(self, user_id: str, payload: dict) -> dict:
        device_id = self._device_id(payload["installation_id"], payload["os_user_identifier"])
        existing = self.devices.get_by_query({"_id": device_id})
        if existing and existing["user_id"] != user_id:
            raise PermissionError("This installation is already associated with another account")

        now = datetime.now(timezone.utc)
        document = {
            "_id": device_id,
            "user_id": user_id,
            "os_user_identifier": payload["os_user_identifier"],
            "installation_id": payload["installation_id"],
            "device_name": payload["device_name"],
            "desktop_version": payload["desktop_version"],
            "last_seen": now,
            "created_at": existing["created_at"] if existing else now,
        }
        return self._public_device(self.devices.upsert({"_id": device_id}, document))

    def list_for_user(self, user_id: str) -> list[dict]:
        return [self._public_device(device) for device in self.devices.list_by_query({"user_id": user_id})]

    def get_for_user(self, device_id: str, user_id: str) -> dict | None:
        return self.devices.get_by_query({"_id": device_id, "user_id": user_id})

    def get_for_device_key(self, device_id: str, device_key: str) -> dict | None:
        key_hash = self._key_hash(device_key)
        device = self.devices.get_by_query({"_id": device_id})
        if device is None or not secrets.compare_digest(device.get("device_key_hash", ""), key_hash):
            return None
        self.devices.collection.update_one(
            {"_id": device_id}, {"$set": {"last_seen": datetime.now(timezone.utc)}}
        )
        return device

    def update_calibration(self, device_id: str, user_id: str, calibration_data: dict[str, Any]) -> None:
        updated = self.devices.update(
            {"_id": device_id, "user_id": user_id},
            {
                "calibration_data": calibration_data,
                "calibration_updated_at": datetime.now(timezone.utc),
            },
        )
        if not updated:
            raise RuntimeError("Device calibration could not be saved")


def get_device_service() -> DeviceService:
    return DeviceService()
