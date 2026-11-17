from __future__ import annotations

import argparse
import base64
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dotenv import load_dotenv
from pymongo import MongoClient


def load_private_key(path: Path, password: bytes) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(path.read_bytes(), password=password)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Signing key must be an Ed25519 private key")
    return key


def create_release_document(
    package_path: Path,
    version: str,
    platform: str,
    download_url: str,
    release_notes: str,
    minimum_supported_version: str,
    signing_key: Ed25519PrivateKey,
) -> dict:
    parsed_url = urlparse(download_url)
    if parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.username or parsed_url.password:
        raise ValueError("Release packages must be hosted at an HTTPS URL")
    hasher = hashlib.sha256()
    with package_path.open("rb") as package:
        for chunk in iter(lambda: package.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.digest()
    return {
        "version": version,
        "platform": platform,
        "download_url": download_url,
        "release_notes": release_notes,
        "published_at": datetime.now(timezone.utc),
        "minimum_supported_version": minimum_supported_version,
        "sha256": digest.hex(),
        "signature": base64.b64encode(signing_key.sign(digest)).decode("ascii"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish signed Intentra release metadata to MongoDB")
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--platform", default="windows")
    parser.add_argument("--download-url", required=True)
    parser.add_argument("--release-notes", required=True)
    parser.add_argument("--minimum-supported-version", required=True)
    parser.add_argument("--private-key", required=True, type=Path)
    args = parser.parse_args()

    if not args.package.is_file():
        raise FileNotFoundError(f"Package file does not exist: {args.package}")
    repository_root = Path(__file__).resolve().parents[2]
    if args.private_key.resolve().is_relative_to(repository_root):
        raise ValueError("Store the private signing key outside the repository")
    for version in (args.version, args.minimum_supported_version):
        if not version or not all(part.isdigit() for part in version.split(".")):
            raise ValueError("Versions must contain dot-separated integers")
    release_version = tuple(int(part) for part in args.version.split("."))
    minimum_version = tuple(int(part) for part in args.minimum_supported_version.split("."))
    width = max(len(release_version), len(minimum_version))
    release_version += (0,) * (width - len(release_version))
    minimum_version += (0,) * (width - len(minimum_version))
    if minimum_version > release_version:
        raise ValueError("Minimum supported version cannot exceed the release version")

    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DB_NAME", "intentra")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI must be configured")

    password = os.getenv("INTENTRA_UPDATE_SIGNING_PASSWORD")
    if not password:
        raise RuntimeError("INTENTRA_UPDATE_SIGNING_PASSWORD must be set in the release environment")
    signing_key = load_private_key(args.private_key, password.encode("utf-8"))
    release = create_release_document(
        args.package,
        args.version,
        args.platform,
        args.download_url,
        args.release_notes,
        args.minimum_supported_version,
        signing_key,
    )
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        client[database_name]["updates"].replace_one(
            {"platform": args.platform, "version": args.version},
            release,
            upsert=True,
        )
    finally:
        client.close()
    print(f"Published signed {args.platform} release {args.version} with SHA-256 {release['sha256']}")


if __name__ == "__main__":
    main()
