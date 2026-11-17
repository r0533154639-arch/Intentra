from __future__ import annotations

import base64
import hashlib
import json
import secrets
import uuid
from dataclasses import dataclass

from storage.settings_cache import SettingsCache


@dataclass(frozen=True)
class DeviceIdentity:
    os_user_identifier: str
    installation_id: str
    device_id: str
    device_key: str
    device_name: str


class DeviceIdentityStore:
    def __init__(self, cache: SettingsCache):
        self.cache = cache

    @staticmethod
    def _windows_user_sid() -> str:
        import win32api
        import win32security

        process_token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32security.TOKEN_QUERY,
        )
        try:
            sid = win32security.GetTokenInformation(process_token, win32security.TokenUser)[0]
            return win32security.ConvertSidToStringSid(sid)
        finally:
            win32api.CloseHandle(process_token)

    @staticmethod
    def _protect_device_key(device_key: str) -> str:
        import win32crypt

        protected = win32crypt.CryptProtectData(
            device_key.encode("ascii"),
            "Intentra desktop device key",
            None,
            None,
            None,
            0,
        )
        return base64.b64encode(protected).decode("ascii")

    @staticmethod
    def _unprotect_device_key(protected_key: str) -> str:
        import win32crypt

        protected = base64.b64decode(protected_key, validate=True)
        _, plaintext = win32crypt.CryptUnprotectData(
            protected,
            None,
            None,
            None,
            0,
        )
        return plaintext.decode("ascii")
    def load_or_create(self) -> DeviceIdentity:
        os_user_identifier = self._windows_user_sid()
        stored = self.cache.get("device_identity")
        if stored:
            data = json.loads(stored)
            if data["os_user_identifier"] == os_user_identifier:
                device_key = self._unprotect_device_key(data["protected_device_key"])
                installation_id = data["installation_id"]
                return DeviceIdentity(
                    os_user_identifier=os_user_identifier,
                    installation_id=installation_id,
                    device_id=self._device_id(installation_id, os_user_identifier),
                    device_key=device_key,
                    device_name=data["device_name"],
                )

        installation_id = str(uuid.uuid4())
        device_key = secrets.token_hex(32)
        import platform

        device_name = platform.node() or "Windows desktop"
        data = {
            "os_user_identifier": os_user_identifier,
            "installation_id": installation_id,
            "protected_device_key": self._protect_device_key(device_key),
            "device_name": device_name,
        }
        self.cache.set("device_identity", json.dumps(data))
        return DeviceIdentity(
            os_user_identifier=os_user_identifier,
            installation_id=installation_id,
            device_id=self._device_id(installation_id, os_user_identifier),
            device_key=device_key,
            device_name=device_name,
        )

    @staticmethod
    def _device_id(installation_id: str, os_user_identifier: str) -> str:
        identity = f"{installation_id}\0{os_user_identifier}".encode("utf-8")
        return hashlib.sha256(identity).hexdigest()
