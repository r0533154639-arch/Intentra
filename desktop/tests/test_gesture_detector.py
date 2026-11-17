from gestures.gesture_config import GestureConfig
from gestures.gesture_detector import GestureDetector


def create_detector() -> GestureDetector:
    return GestureDetector(
        GestureConfig(
            pinch_threshold=0.1,
            short_pinch_max_duration_ms=200,
            double_click_interval_ms=400,
            right_click_hold_ms=600,
            movement_threshold=0.1,
            jitter_threshold=0.001,
            fast_scroll_threshold=1.5,
            fast_scroll_acceleration_threshold=10.0,
            fast_scroll_duration_ms=300,
            max_scroll_speed=10.0,
            precise_sensitivity=100.0,
            fast_scroll_intensity=2.0,
            movement_smoothing=0.0,
        )
    )


def test_short_pinch_is_held_until_double_click_window_expires():
    detector = create_detector()
    assert detector.update(0.05, (0.5, 0.5), 0) == []
    assert detector.update(0.2, (0.5, 0.5), 100) == []
    events = detector.update(0.2, (0.5, 0.5), 501)
    assert [event.name for event in events] == ["LEFT_CLICK"]


def test_two_short_pinches_produce_one_double_click():
    detector = create_detector()
    detector.update(0.05, (0.5, 0.5), 0)
    detector.update(0.2, (0.5, 0.5), 100)
    detector.update(0.2, (0.5, 0.5), 120)
    detector.update(0.05, (0.5, 0.5), 150)
    detector.update(0.05, (0.5, 0.5), 250)
    detector.update(0.2, (0.5, 0.5), 300)
    events = detector.update(0.2, (0.5, 0.5), 350)
    events += detector.update(0.2, (0.5, 0.5), 400)
    assert [event.name for event in events] == ["DOUBLE_CLICK"]
    assert detector.update(0.2, (0.5, 0.5), 800) == []


def test_long_stationary_pinch_produces_one_right_click():
    detector = create_detector()
    detector.update(0.05, (0.5, 0.5), 0)
    assert detector.update(0.05, (0.5, 0.5), 650) == []
    events = detector.update(0.2, (0.5, 0.5), 700)
    assert [event.name for event in events] == ["RIGHT_CLICK"]


def test_gradual_movement_scrolls_and_does_not_click_on_release():
    detector = create_detector()
    detector.update(0.05, (0.5, 0.5), 0)
    events = detector.update(0.05, (0.5, 0.7), 1000)
    assert [event.name for event in events] == ["SCROLL"]
    assert events[0].context["mode"] == "precise"
    assert detector.update(0.2, (0.5, 0.7), 1050) == []
    assert detector.update(0.2, (0.5, 0.7), 1500) == []


def test_fast_wrist_movement_scrolls_only_after_release():
    detector = create_detector()
    detector.update(0.05, (0.5, 0.5), 0)
    assert detector.update(0.05, (0.5, 0.7), 100) == []
    events = detector.update(0.2, (0.5, 0.7), 120)
    assert [event.name for event in events] == ["SCROLL"]
    assert events[0].context["mode"] == "fast"
    assert events[0].context["duration_ms"] == 300


def test_detector_rejects_unconfigured_thresholds():
    try:
        GestureConfig.from_settings(
            {
                "gestures": {
                    "pinch_threshold": 0,
                    "short_pinch_max_duration_ms": 0,
                    "double_click_interval_ms": 0,
                    "right_click_hold_ms": 0,
                    "movement_threshold": 0,
                    "jitter_threshold": 0,
                },
                "scroll": {
                    "fast_scroll_threshold": 0,
                    "fast_scroll_acceleration_threshold": 0,
                    "fast_scroll_duration_ms": 0,
                    "max_scroll_speed": 0,
                    "precise_sensitivity": 0,
                    "fast_scroll_intensity": 0,
                    "movement_smoothing": 0,
                },
            }
        )
    except ValueError as exc:
        assert "Pinch threshold" in str(exc)
    else:
        raise AssertionError("Zero placeholder values must not enable gesture control")
