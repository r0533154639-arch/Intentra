from __future__ import annotations

from app.configuration import DesktopConfig
from services.api_client import ApiClient
from services.settings_sync import SettingsSyncService
from storage.settings_cache import SettingsCache
from user.device_identity import DeviceIdentity, DeviceIdentityStore
from user.user_settings import UserSettings


class ApplicationLifecycle:
    def __init__(self, config: DesktopConfig | None = None):
        self.config = config or DesktopConfig.load()
        self.cache = SettingsCache(self.config.cache_path)
        self.api_client = ApiClient(self.config.server_base_url)
        self.settings_sync = SettingsSyncService(self.api_client, self.cache)
        self.identity: DeviceIdentity | None = None

    def start(self) -> dict:
        self.identity = DeviceIdentityStore(self.cache).load_or_create()
        result = self.settings_sync.synchronize(self.identity)
        if result["status"] == "pairing_required":
            return result
        if "settings" not in result:
            return result

        user_settings = UserSettings.from_server_payload(result["settings"])
        return {
            "status": result["status"],
            "settings": user_settings,
            "gaze_calibrated": bool(user_settings.calibration_data),
        }

    def poll_pairing(self) -> dict:
        if self.identity is None:
            raise RuntimeError("Application lifecycle has not started")
        result = self.settings_sync.poll_pairing(self.identity)
        if "settings" not in result:
            return result
        user_settings = UserSettings.from_server_payload(result["settings"])
        return {
            "status": result["status"],
            "settings": user_settings,
            "gaze_calibrated": bool(user_settings.calibration_data),
        }

    def begin_pairing(self) -> dict:
        if self.identity is None:
            raise RuntimeError("Application lifecycle has not started")
        return self.settings_sync.start_pairing(self.identity)

    def refresh_settings(self) -> dict:
        if self.identity is None:
            raise RuntimeError("Application lifecycle has not started")
        result = self.settings_sync.synchronize(self.identity)
        if "settings" not in result:
            return result
        user_settings = UserSettings.from_server_payload(result["settings"])
        return {
            "status": result["status"],
            "settings": user_settings,
            "gaze_calibrated": bool(user_settings.calibration_data),
        }

    def save_calibration(self, calibration_data: dict) -> UserSettings:
        if self.identity is None:
            raise RuntimeError("Application lifecycle has not started")
        payload = self.settings_sync.save_calibration(self.identity, calibration_data)
        return UserSettings.from_server_payload(payload)

    def close(self) -> None:
        self.api_client.close()
        self.cache.close()
