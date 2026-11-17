from gestures.gesture_detector import ActionEvent
from vision.frame_pipeline import _console_print, _log_gesture_action, _log_hand_sample


def test_gesture_action_logger_describes_clicks(capsys):
    _log_gesture_action(ActionEvent("LEFT_CLICK", {}))

    assert capsys.readouterr().out == "[Intentra] Action detected: Single left click\n"


def test_gesture_action_logger_describes_scroll_direction_and_amount(capsys):
    _log_gesture_action(ActionEvent("SCROLL", {"mode": "fast", "amount": -2.0, "duration_ms": 300}))

    assert capsys.readouterr().out == (
        "[Intentra] Action detected: Fast scroll down (amount=-2.00, duration=300 ms)\n"
    )


def test_hand_diagnostic_compares_measured_pinch_to_threshold(capsys):
    _log_hand_sample(0.13, 0.1)

    assert capsys.readouterr().out == (
        "[Intentra] Hand input: pinch distance=0.130, threshold=0.100 (no pinch)\n"
    )


def test_console_logger_does_not_raise_when_stdout_is_unavailable(monkeypatch):
    monkeypatch.setattr("vision.frame_pipeline.sys.stdout", None)

    _console_print("test")
