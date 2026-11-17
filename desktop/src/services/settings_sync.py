from __future__ import annotations

import json

import httpx

from services.api_client import ApiClient
from storage.settings_cache import SettingsCache
from user.device_identity import DeviceIdentity


class SettingsSyncService:
    def __init__(self, api_client: ApiClient, cache: SettingsCache):
        self.api_client = api_client
        self.cache = cache

    def load_cached_settings(self) -> dict | None:
        payload = self.cache.get("user_settings")
        return json.loads(payload) if payload else None

    def save_cached_settings(self, payload: dict) -> None:
        self.cache.set("user_settings", json.dumps(payload))

    def synchronize(self, identity: DeviceIdentity) -> dict:
        try:
            response = self.api_client.get(
                f"/api/devices/{identity.device_id}/settings",
                extra_headers={"X-Device-Key": identity.device_key},
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise
            return self.start_pairing(identity)
        except (httpx.NetworkError, httpx.TimeoutException) as exc:
            cached = self.load_cached_settings()
            if cached is None:
                raise ConnectionError("Server is unavailable and no cached settings exist") from exc
            return {"status": "offline_cached", "settings": cached}

        pending_calibration = self.cache.get("pending_calibration")
        if pending_calibration:
            response = self.api_client.put(
                f"/api/devices/{identity.device_id}/settings/calibration",
                {"calibration_data": json.loads(pending_calibration)},
                extra_headers={"X-Device-Key": identity.device_key},
            )
            self.cache.delete("pending_calibration")
        self.save_cached_settings(response)
        return {"status": "ready", "settings": response}

    def start_pairing(self, identity: DeviceIdentity) -> dict:
        try:
            pairing = self.api_client.post(
                "/api/devices/pairing-codes",
                {
                    "os_user_identifier": identity.os_user_identifier,
                    "installation_id": identity.installation_id,
                    "device_name": identity.device_name,
                    "desktop_version": "1.0.0",
                    "device_key": identity.device_key,
                },
            )
        except (httpx.NetworkError, httpx.TimeoutException) as exc:
            cached = self.load_cached_settings()
            if cached is not None:
                return {"status": "offline_cached", "settings": cached}
            raise ConnectionError("Could not contact the server to pair this desktop") from exc
        return {
            "status": "pairing_required",
            "device_id": pairing["device_id"],
            "pairing_code": pairing["pairing_code"],
            "expires_at": pairing["expires_at"],
        }

    def poll_pairing(self, identity: DeviceIdentity) -> dict:
        try:
            status = self.api_client.get(
                f"/api/devices/pairing-codes/{identity.device_id}",
                extra_headers={"X-Device-Key": identity.device_key},
            )
            if status["status"] != "paired":
                return {"status": status["status"]}
            return self.synchronize(identity)
        except (httpx.NetworkError, httpx.TimeoutException) as exc:
            cached = self.load_cached_settings()
            if cached is not None:
                return {"status": "offline_cached", "settings": cached}
            raise ConnectionError("Could not contact the server to check device pairing") from exc

    def save_calibration(self, identity: DeviceIdentity, calibration_data: dict) -> dict:
        self.cache.set("pending_calibration", json.dumps(calibration_data))
        settings = self.load_cached_settings() or {
            "gaze": {"smoothing": 0.9, "sensitivity": 0.6, "calibration_data": {}},
            "gestures": {},
            "scroll": {},
        }
        settings["gaze"]["calibration_data"] = calibration_data
        self.save_cached_settings(settings)
        try:
            settings = self.api_client.put(
                f"/api/devices/{identity.device_id}/settings/calibration",
                {"calibration_data": calibration_data},
                extra_headers={"X-Device-Key": identity.device_key},
            )
        except (httpx.NetworkError, httpx.TimeoutException):
            return settings
        self.cache.delete("pending_calibration")
        self.save_cached_settings(settings)
        return settings
