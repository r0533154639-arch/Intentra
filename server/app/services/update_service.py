from __future__ import annotations

from typing import Any

from app.database.mongo import get_collection


class UpdateService:
    def __init__(self):
        self.releases = get_collection("updates")

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, ...]:
        try:
            parts = tuple(int(part) for part in version.split("."))
        except ValueError as exc:
            raise ValueError("Versions must be dot-separated integers") from exc
        if not parts or any(part < 0 for part in parts):
            raise ValueError("Versions must be dot-separated non-negative integers")
        return parts

    def latest(self, platform: str = "windows") -> dict[str, Any]:
        release = self.releases.find_one({"platform": platform}, sort=[("published_at", -1)])
        if release is None:
            raise LookupError(f"No published update exists for platform '{platform}'")
        required_fields = {
            "version",
            "platform",
            "download_url",
            "release_notes",
            "published_at",
            "minimum_supported_version",
            "sha256",
            "signature",
        }
        missing_fields = required_fields.difference(release)
        if missing_fields:
            raise RuntimeError(f"Update release metadata is incomplete: {', '.join(sorted(missing_fields))}")
        release["_id"] = str(release["_id"])
        return release

    def check(self, current_version: str | None = None, platform: str = "windows") -> dict[str, Any]:
        latest = self.latest(platform)
        latest_version = self._version_tuple(latest["version"])
        current = self._version_tuple(current_version) if current_version else ()
        version_width = max(len(latest_version), len(current))
        latest_version = latest_version + (0,) * (version_width - len(latest_version))
        current = current + (0,) * (version_width - len(current))
        return {"update_available": not current_version or latest_version > current, "latest": latest}


def get_update_service() -> UpdateService:
    return UpdateService()
