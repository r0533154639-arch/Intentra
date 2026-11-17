from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class UserSettings:
    user_id: str | None = None
    version: int = 0
    smoothing: float = 0.9
    sensitivity: float = 0.6
    calibration_data: dict = field(default_factory=dict)
    pinch_threshold: float = 0.0
    short_pinch_max_duration_ms: int = 0
    double_click_interval_ms: int = 0
    right_click_hold_ms: int = 0
    movement_threshold: float = 0.0
    jitter_threshold: float = 0.0
    precise_sensitivity: float = 1.0
    movement_smoothing: float = 0.0
    max_scroll_speed: float = 0.0
    fast_scroll_threshold: float = 0.0
    fast_scroll_acceleration_threshold: float = 0.0
    fast_scroll_duration_ms: int = 0
    fast_scroll_intensity: float = 1.0

    @classmethod
    def from_server_payload(cls, payload: dict) -> "UserSettings":
        gaze = payload.get("gaze", {})
        gestures = payload.get("gestures", {})
        scroll = payload.get("scroll", {})
        return cls(
            user_id=payload.get("user_id"),
            version=int(payload.get("version", 0)),
            smoothing=gaze.get("smoothing", 0.5),
            sensitivity=gaze.get("sensitivity", 1.0),
            calibration_data=gaze.get("calibration_data", {}),
            pinch_threshold=gestures.get("pinch_threshold", 0.0),
            short_pinch_max_duration_ms=gestures.get("short_pinch_max_duration_ms", 0),
            double_click_interval_ms=gestures.get("double_click_interval_ms", 0),
            right_click_hold_ms=gestures.get("right_click_hold_ms", 0),
            movement_threshold=gestures.get("movement_threshold", 0.0),
            jitter_threshold=gestures.get("jitter_threshold", 0.0),
            precise_sensitivity=scroll.get("precise_sensitivity", 1.0),
            movement_smoothing=scroll.get("movement_smoothing", 0.0),
            max_scroll_speed=scroll.get("max_scroll_speed", 0.0),
            fast_scroll_threshold=scroll.get("fast_scroll_threshold", 0.0),
            fast_scroll_acceleration_threshold=scroll.get("fast_scroll_acceleration_threshold", 0.0),
            fast_scroll_duration_ms=scroll.get("fast_scroll_duration_ms", 0),
            fast_scroll_intensity=scroll.get("fast_scroll_intensity", 1.0),
        )

    def as_server_payload(self) -> dict:
        values = asdict(self)
        return {
            "gaze": {
                "smoothing": values["smoothing"],
                "sensitivity": values["sensitivity"],
                "calibration_data": values["calibration_data"],
            },
            "gestures": {
                "pinch_threshold": values["pinch_threshold"],
                "short_pinch_max_duration_ms": values["short_pinch_max_duration_ms"],
                "double_click_interval_ms": values["double_click_interval_ms"],
                "right_click_hold_ms": values["right_click_hold_ms"],
                "movement_threshold": values["movement_threshold"],
                "jitter_threshold": values["jitter_threshold"],
            },
            "scroll": {
                "precise_sensitivity": values["precise_sensitivity"],
                "movement_smoothing": values["movement_smoothing"],
                "max_scroll_speed": values["max_scroll_speed"],
                "fast_scroll_threshold": values["fast_scroll_threshold"],
                "fast_scroll_acceleration_threshold": values["fast_scroll_acceleration_threshold"],
                "fast_scroll_duration_ms": values["fast_scroll_duration_ms"],
                "fast_scroll_intensity": values["fast_scroll_intensity"],
            },
        }
