from secrets import token_hex

from fastapi.testclient import TestClient

from app.main import app
from app.database.mongo import get_collection


def register_and_login(client: TestClient) -> tuple[str, str]:
    unique = token_hex(8)
    registration = client.post(
        "/api/auth/register",
        json={
            "username": f"test-{unique}",
            "email": f"test-{unique}@example.com",
            "password": "intentra-test-password",
        },
    )
    assert registration.status_code == 200
    login = client.post(
        "/api/auth/login",
        json={
            "username": registration.json()["username"],
            "password": "intentra-test-password",
        },
    )
    assert login.status_code == 200
    return registration.json()["id"], login.json()["access_token"]


def test_health_and_authenticated_user():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        _, token = register_and_login(client)
        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


def test_settings_are_saved_per_account():
    with TestClient(app) as client:
        user_id, token = register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "gaze": {"smoothing": 0.4, "sensitivity": 1.2, "calibration_data": {}},
            "gestures": {
                "pinch_threshold": 0.0,
                "short_pinch_max_duration_ms": 0,
                "double_click_interval_ms": 0,
                "right_click_hold_ms": 0,
                "movement_threshold": 0.0,
            },
            "scroll": {
                "precise_sensitivity": 1.0,
                "fast_scroll_threshold": 0.0,
                "fast_scroll_intensity": 1.0,
            },
        }
        saved = client.put("/api/settings", headers=headers, json=payload)
        assert saved.status_code == 200
        assert saved.json()["version"] == 1
        loaded = client.get("/api/settings", headers=headers)
        assert loaded.json()["gaze"]["smoothing"] == 0.4
        assert loaded.json()["gestures"]["jitter_threshold"] == 0.0
        assert loaded.json()["scroll"]["max_scroll_speed"] == 0.0

        get_collection("settings").update_one(
            {"user_id": user_id},
            {"$set": {"gestures": {"pinch_threshold": 0.1}}},
        )
        migrated = client.get("/api/settings", headers=headers).json()
        assert migrated["gestures"]["pinch_threshold"] == 0.1
        assert migrated["gestures"]["jitter_threshold"] == 0.0
        assert migrated["scroll"]["max_scroll_speed"] == 0.0

        _, other_token = register_and_login(client)
        other_settings = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer " + other_token},
        ).json()
        assert other_settings["gaze"]["smoothing"] == 0.9
        assert other_settings["gaze"]["sensitivity"] == 0.6
        assert other_settings["gestures"] == {
            "pinch_threshold": 0.2,
            "short_pinch_max_duration_ms": 300,
            "double_click_interval_ms": 400,
            "right_click_hold_ms": 650,
            "movement_threshold": 0.1,
            "jitter_threshold": 0.002,
        }
        assert other_settings["scroll"] == {
            "precise_sensitivity": 100.0,
            "movement_smoothing": 0.4,
            "max_scroll_speed": 10.0,
            "fast_scroll_threshold": 1.5,
            "fast_scroll_acceleration_threshold": 10.0,
            "fast_scroll_duration_ms": 300,
            "fast_scroll_intensity": 2.0,
        }


def test_device_pairing_requires_approval_and_authenticates_device_key():
    with TestClient(app) as client:
        _, token = register_and_login(client)
        device_key = token_hex(32)
        pairing = client.post(
            "/api/devices/pairing-codes",
            json={
                "os_user_identifier": "S-1-5-21-test",
                "installation_id": token_hex(16),
                "device_name": "Test desktop",
                "desktop_version": "1.0.0",
                "device_key": device_key,
            },
        )
        assert pairing.status_code == 200
        device_id = pairing.json()["device_id"]
        headers = {"X-Device-Key": device_key}
        assert client.get(f"/api/devices/pairing-codes/{device_id}", headers=headers).json()["status"] == "pending"

        approved = client.post(
            "/api/devices/pair",
            headers={"Authorization": f"Bearer {token}"},
            json={"pairing_code": pairing.json()["pairing_code"]},
        )
        assert approved.status_code == 200
        assert "device_key_hash" not in approved.json()
        assert client.get(f"/api/devices/pairing-codes/{device_id}", headers=headers).json()["status"] == "paired"
        initial_settings = client.get(f"/api/devices/{device_id}/settings", headers=headers)
        assert initial_settings.status_code == 200
        assert initial_settings.json()["gaze"]["calibration_data"] == {}

        calibration = {
            "coefficients": [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.2, 0.3],
                [0.4, 0.5],
                [0.6, 0.7],
            ],
            "sample_count": 9,
        }
        saved_calibration = client.put(
            f"/api/devices/{device_id}/settings/calibration",
            headers=headers,
            json={"calibration_data": calibration},
        )
        assert saved_calibration.status_code == 200
        assert saved_calibration.json()["gaze"]["calibration_data"] == calibration
        owner_settings = client.get(
            f"/api/devices/{device_id}/settings",
            headers={"Authorization": "Bearer " + token},
        ).json()
        assert owner_settings["gaze"]["calibration_data"] == calibration
        account_settings = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer " + token},
        ).json()
        assert account_settings["gaze"]["calibration_data"] == {}
        assert "calibration_data" not in client.get(
            "/api/devices",
            headers={"Authorization": "Bearer " + token},
        ).json()[0]

        second_device_key = token_hex(32)
        second_installation = client.post(
            "/api/devices/pairing-codes",
            json={
                "os_user_identifier": "S-1-5-21-test",
                "installation_id": token_hex(16),
                "device_name": "Second desktop",
                "desktop_version": "1.0.0",
                "device_key": second_device_key,
            },
        )
        second_device_id = second_installation.json()["device_id"]
        second_approval = client.post(
            "/api/devices/pair",
            headers={"Authorization": "Bearer " + token},
            json={"pairing_code": second_installation.json()["pairing_code"]},
        )
        assert second_approval.status_code == 200
        second_pairing_status = client.get(
            f"/api/devices/pairing-codes/{second_device_id}",
            headers={"X-Device-Key": second_device_key},
        )
        assert second_pairing_status.json()["status"] == "paired"
        second_settings = client.get(
            f"/api/devices/{second_device_id}/settings",
            headers={"X-Device-Key": second_device_key},
        )
        assert second_settings.status_code == 200
        assert second_settings.json()["gaze"]["calibration_data"] == {}
        assert client.get(f"/api/devices/{device_id}/settings").status_code == 401


def test_pairing_cannot_take_over_an_existing_device():
    with TestClient(app) as client:
        owner_id, owner_token = register_and_login(client)
        installation_id = token_hex(16)
        os_user_identifier = "S-1-5-21-pairing-owner"
        original_key = token_hex(32)
        pairing = client.post(
            "/api/devices/pairing-codes",
            json={
                "os_user_identifier": os_user_identifier,
                "installation_id": installation_id,
                "device_name": "Owner desktop",
                "desktop_version": "1.0.0",
                "device_key": original_key,
            },
        )
        assert pairing.status_code == 200
        approval = client.post(
            "/api/devices/pair",
            headers={"Authorization": "Bearer " + owner_token},
            json={"pairing_code": pairing.json()["pairing_code"]},
        )
        assert approval.status_code == 200

        replacement = client.post(
            "/api/devices/pairing-codes",
            json={
                "os_user_identifier": os_user_identifier,
                "installation_id": installation_id,
                "device_name": "Replacement desktop",
                "desktop_version": "1.0.0",
                "device_key": token_hex(32),
            },
        )
        assert replacement.status_code == 409

        devices = client.get(
            "/api/devices",
            headers={"Authorization": "Bearer " + owner_token},
        ).json()
        assert len(devices) == 1
        assert devices[0]["user_id"] == owner_id


def test_logout_revokes_token():
    with TestClient(app) as client:
        _, token = register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        assert client.post("/api/auth/logout", headers=headers).status_code == 200
        assert client.get("/api/users/me", headers=headers).status_code == 401
