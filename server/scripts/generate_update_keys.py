from __future__ import annotations

import argparse
import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Ed25519 key pair for signed Intentra updates")
    parser.add_argument("--private-key", required=True, type=Path)
    parser.add_argument("--password-env-var", required=True)
    args = parser.parse_args()

    import os

    password = os.getenv(args.password_env_var)
    if not password or len(password) < 16:
        raise ValueError(f"{args.password_env_var} must be set to a password of at least 16 characters")
    if args.private_key.exists():
        raise FileExistsError(f"Refusing to overwrite existing private key: {args.private_key}")
    repository_root = Path(__file__).resolve().parents[2]
    if args.private_key.resolve().is_relative_to(repository_root):
        raise ValueError("Store the private signing key outside the repository")

    private_key = Ed25519PrivateKey.generate()
    encrypted_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    args.private_key.parent.mkdir(parents=True, exist_ok=True)
    with args.private_key.open("xb") as output:
        output.write(encrypted_pem)

    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    print(f"Keep this private signing key offline and backed up: {args.private_key.resolve()}")
    print(f"INTENTRA_UPDATE_PUBLIC_KEY={base64.b64encode(public_key).decode('ascii')}")


if __name__ == "__main__":
    main()
