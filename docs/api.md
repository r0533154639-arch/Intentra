# API contract summary

- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/users/me
- GET /api/settings
- PUT /api/settings
- POST /api/devices/register
- GET /api/devices
- POST /api/devices/pairing-codes
- POST /api/devices/pair
- GET /api/devices/pairing-codes/{device_id}
- GET /api/updates/check
- GET /api/updates/latest

Device settings are available at
`GET /api/devices/{device_id}/settings` and can be retrieved only by the
paired device key or an authenticated account that owns the device.
Calibration updates use
`PUT /api/devices/{device_id}/settings/calibration`. Calibration is saved
on the associated device record, and this device-settings response overlays
that calibration onto the account's shared gaze and gesture preferences.
The account-level `GET` and `PUT /api/settings` endpoints do not store
calibration data.
