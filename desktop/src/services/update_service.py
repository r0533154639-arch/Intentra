from __future__ import annotations

import base64
import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from services.api_client import ApiClient

APP_VERSION = "1.0.0"
MAX_UPDATE_SIZE = 2 * 1024 * 1024 * 1024


class UpdateService:
    def __init__(self, api_client: ApiClient, public_key: str):
        self.api_client = api_client
        self.public_key = public_key
        self._verified_packages: dict[Path, tuple[str, str]] = {}

    def check_for_update(self) -> dict:
        return self.api_client.get(
            f"/api/updates/check?current_version={APP_VERSION}&platform=windows"
        )

    def download_and_verify(self, release: dict) -> Path:
        if not self.public_key:
            raise RuntimeError("INTENTRA_UPDATE_PUBLIC_KEY must be configured before installing updates")
        if re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", release.get("version", "")) is None:
            raise ValueError("Update version is invalid")
        minimum_version = release.get("minimum_supported_version", "")
        if re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", minimum_version) is None:
            raise ValueError("Update metadata does not contain a valid minimum supported version")
        if self._version_tuple(APP_VERSION) < self._version_tuple(minimum_version):
            raise RuntimeError(
                f"Version {APP_VERSION} is below the supported upgrade floor {minimum_version}"
            )
        url = release.get("download_url", "")
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.username or parsed_url.password:
            raise ValueError("Update packages must be downloaded from an HTTPS URL")
        expected_hash = release.get("sha256", "").lower()
        if re.fullmatch(r"[a-f0-9]{64}", expected_hash) is None:
            raise ValueError("Update metadata does not contain a valid SHA-256 digest")

        destination_directory = self._update_directory()
        destination_directory.mkdir(parents=True, exist_ok=True)
        destination = destination_directory / f"intentra-{release['version']}-setup.exe"
        temporary = destination.with_suffix(".exe.download")
        digest = hashlib.sha256()
        total_size = 0
        try:
            with httpx.Client(timeout=60, follow_redirects=False) as client:
                with client.stream("GET", url) as response:
                    response.raise_for_status()
                    with temporary.open("wb") as package:
                        for chunk in response.iter_bytes():
                            total_size += len(chunk)
                            if total_size > MAX_UPDATE_SIZE:
                                raise ValueError("Update package exceeds the maximum permitted size")
                            digest.update(chunk)
                            package.write(chunk)
            actual_hash = digest.hexdigest()
            if actual_hash != expected_hash:
                raise ValueError("Update package SHA-256 digest does not match the release metadata")
            self._verify_signature(actual_hash, release["signature"])
            temporary.replace(destination)
            self._verified_packages[destination.resolve()] = (actual_hash, release["signature"])
            return destination
        finally:
            if temporary.exists():
                temporary.unlink()

    def install(self, package_path: Path) -> None:
        if not package_path.is_file():
            raise FileNotFoundError(f"Verified update package does not exist: {package_path}")
        verified = self._verified_packages.get(package_path.resolve())
        if verified is None:
            raise ValueError("Only a package verified during this application session can be installed")
        digest = hashlib.sha256()
        with package_path.open("rb") as package:
            for chunk in iter(lambda: package.read(1024 * 1024), b""):
                digest.update(chunk)
        actual_hash = digest.hexdigest()
        if actual_hash != verified[0]:
            raise ValueError("Update package changed after verification")
        self._verify_signature(actual_hash, verified[1])
        import win32api
        import win32con

        result = win32api.ShellExecute(
            None,
            "runas",
            str(package_path),
            None,
            str(package_path.parent),
            win32con.SW_SHOWNORMAL,
        )
        if result <= 32:
            raise OSError(f"Windows could not launch the verified installer (ShellExecute={result})")

    def _verify_signature(self, digest_hex: str, signature_b64: str) -> None:
        try:
            public_key_bytes = base64.b64decode(self.public_key, validate=True)
            signature = base64.b64decode(signature_b64, validate=True)
        except (ValueError, TypeError) as exc:
            raise ValueError("Update signature or public key is not valid base64") from exc
        if len(public_key_bytes) != 32:
            raise ValueError("INTENTRA_UPDATE_PUBLIC_KEY must encode a 32-byte Ed25519 key")
        try:
            Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature, bytes.fromhex(digest_hex))
        except InvalidSignature as exc:
            raise ValueError("Update package signature verification failed") from exc

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, ...]:
        values = tuple(int(part) for part in version.split("."))
        width = max(len(values), 4)
        return values + (0,) * (width - len(values))

    @staticmethod
    def _update_directory() -> Path:
        local_app_data = os.getenv("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA is not available on this Windows installation")
        return Path(local_app_data) / "Intentra" / "updates"
