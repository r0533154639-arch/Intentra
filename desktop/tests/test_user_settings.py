from gestures.gesture_config import GestureConfig
from user.user_settings import UserSettings


def test_older_settings_payload_uses_safe_disabled_gesture_defaults():
    settings = UserSettings.from_server_payload(
        {
            "user_id": "user-1",
            "version": 2,
            "gaze": {"smoothing": 0.5, "sensitivity": 1.0, "calibration_data": {}},
            "gestures": {"pinch_threshold": 0.1},
            "scroll": {"precise_sensitivity": 1.0},
        }
    )

    assert settings.user_id == "user-1"
    assert settings.pinch_threshold == 0.1
    try:
        GestureConfig.from_settings(settings.as_server_payload())
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete legacy gesture settings must remain disabled")
