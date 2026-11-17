from dataclasses import dataclass


@dataclass(frozen=True)
class GestureConfig:
    pinch_threshold: float
    short_pinch_max_duration_ms: int
    double_click_interval_ms: int
    right_click_hold_ms: int
    movement_threshold: float
    jitter_threshold: float
    fast_scroll_threshold: float
    fast_scroll_acceleration_threshold: float
    fast_scroll_duration_ms: int
    max_scroll_speed: float
    precise_sensitivity: float
    fast_scroll_intensity: float
    movement_smoothing: float

    @classmethod
    def from_settings(cls, settings: dict) -> "GestureConfig":
        gesture = settings["gestures"]
        scroll = settings["scroll"]
        config = cls(
            pinch_threshold=float(gesture["pinch_threshold"]),
            short_pinch_max_duration_ms=int(gesture["short_pinch_max_duration_ms"]),
            double_click_interval_ms=int(gesture["double_click_interval_ms"]),
            right_click_hold_ms=int(gesture["right_click_hold_ms"]),
            movement_threshold=float(gesture["movement_threshold"]),
            jitter_threshold=float(gesture["jitter_threshold"]),
            fast_scroll_threshold=float(scroll["fast_scroll_threshold"]),
            fast_scroll_acceleration_threshold=float(scroll["fast_scroll_acceleration_threshold"]),
            fast_scroll_duration_ms=int(scroll["fast_scroll_duration_ms"]),
            max_scroll_speed=float(scroll["max_scroll_speed"]),
            precise_sensitivity=float(scroll["precise_sensitivity"]),
            fast_scroll_intensity=float(scroll["fast_scroll_intensity"]),
            movement_smoothing=float(scroll["movement_smoothing"]),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.pinch_threshold <= 0:
            raise ValueError("Pinch threshold must be calibrated before control is enabled")
        if self.short_pinch_max_duration_ms <= 0 or self.double_click_interval_ms <= 0:
            raise ValueError("Pinch and double-click timing must be configured")
        if self.right_click_hold_ms <= self.short_pinch_max_duration_ms:
            raise ValueError("Right-click hold must exceed the short-pinch duration")
        if self.movement_threshold <= 0 or self.fast_scroll_threshold <= 0:
            raise ValueError("Movement and fast-scroll thresholds must be calibrated")
        if self.jitter_threshold < 0 or self.jitter_threshold >= self.movement_threshold:
            raise ValueError("Jitter threshold must be non-negative and below movement threshold")
        if self.fast_scroll_acceleration_threshold <= 0 or self.max_scroll_speed <= 0:
            raise ValueError("Fast-scroll acceleration and maximum speed must be configured")
        if self.fast_scroll_duration_ms <= 0:
            raise ValueError("Fast-scroll duration must be configured")
        if self.precise_sensitivity <= 0 or self.fast_scroll_intensity <= 0:
            raise ValueError("Scroll sensitivities must be greater than zero")
        if not 0 <= self.movement_smoothing < 1:
            raise ValueError("Movement smoothing must be at least 0 and less than 1")
