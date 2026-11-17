# Intentra

Intentra is a Windows desktop accessibility system that uses gaze tracking and hand gestures to operate a computer without a physical mouse for everyday interaction.

This repository follows the Intentra Project Specification and is organized as a monorepo with separate desktop, web, and backend applications.

## Components

- `desktop/` — Python desktop app for gaze and gesture detection plus OS-level mouse control.
- `web/` — React + TypeScript web application for user account, login, settings, and device management.
- `server/` — FastAPI backend for authentication, settings storage, device registration, and update endpoints.
- `shared/` — Shared contracts and documentation.
- `infrastructure/` — Docker infrastructure for local development.

## Approved gesture mapping

The Phase 1 gesture-to-action mapping is fixed by the specification:

- short pinch -> single click
- two quick pinches -> double click
- long pinch without movement -> right click
- gradual pinch movement -> precise scroll
- fast wrist movement followed by release -> fast scroll

The cursor is controlled by gaze position, not by hand movement.

## Local development

Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY` with a newly
generated value. Do not commit `.env`. MongoDB must be running before the
backend starts.

The local database and backend can instead be started with Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose -f infrastructure\docker-compose.yml up --build
```

### Server

```bash
cd server
copy ..\.env.example .env
# Set JWT_SECRET_KEY in .env to a random secret of at least 32 characters.
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

For integration tests, configure `MONGODB_URI` to a disposable MongoDB
instance, set a test-only `JWT_SECRET_KEY`, then run `pytest`.

### Web app

```bash
cd web
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

### Desktop app

```bash
cd desktop
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\download_models.py
python src/main.py
```

On first desktop launch, the app displays a one-time pairing code. Sign in
to the web app, open **Devices**, and enter that code. Once paired, the
desktop downloads the account's settings and can perform gaze calibration.
Gesture and scroll thresholds remain disabled until calibrated values are
saved in the web settings page. Gaze calibration is stored per paired
desktop, so multiple computers using one account retain independent
calibration results.

The desktop's **Local settings** screen displays the active account,
calibration state, camera index, backend address, and local control
settings. Account-level gesture settings are changed in the web app.

### Tests and build

Run the backend integration tests against a disposable MongoDB database:

```powershell
cd server
python -m pip install -r requirements.txt
pytest
```

Run the desktop unit tests:

```powershell
cd desktop
python -m pip install -r requirements.txt
pytest
```

Build the web application:

```powershell
cd web
npm install
npm run build
```

## Signed desktop releases

The backend exposes update metadata only for releases published to the
MongoDB `updates` collection. Generate an encrypted Ed25519 signing key
outside the repository and configure its public key for the desktop app:

```powershell
python server\scripts\generate_update_keys.py --private-key C:\secure\intentra-release.private.pem --password-env-var INTENTRA_UPDATE_SIGNING_PASSWORD
$env:INTENTRA_UPDATE_PUBLIC_KEY = "<public key printed by the command>"
```

Set `INTENTRA_UPDATE_SIGNING_PASSWORD` through a secure release environment.
Publish a Windows installer from that environment using
`server\scripts\publish_release.py`. The desktop verifies the package
SHA-256 and Ed25519 signature before offering Windows elevation to run it.
Never commit or distribute the private signing key.

## Notes

- Passwords are stored as hashes, not plaintext.
- Production communication should use HTTPS and secret management.
- The system supports offline cached settings and later synchronization.
- The MediaPipe task model files are downloaded separately and are not committed.
