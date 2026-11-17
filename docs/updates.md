# Signed desktop updates

The backend serves only release records present in MongoDB's `updates`
collection. Records must include a version, Windows platform, HTTPS package
URL, release notes, minimum supported version, SHA-256 digest, signature,
and publication timestamp.

Release operators generate an encrypted Ed25519 key outside the repository
with `server/scripts/generate_update_keys.py`, keep its password in the
release environment, and configure the corresponding base64 raw public key
as `INTENTRA_UPDATE_PUBLIC_KEY` in the desktop environment. The
`server/scripts/publish_release.py` command hashes an installer, signs that
digest, and upserts the release metadata into MongoDB.

The desktop downloads packages without following redirects, enforces an
HTTPS URL and a maximum package size, checks SHA-256, verifies the Ed25519
signature, and rechecks the digest immediately before launching the Windows
installer with elevation. It does not install an unverified package.
