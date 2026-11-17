from __future__ import annotations

from dataclasses import dataclass
from math import hypot, copysign

from gestures.gesture_config import GestureConfig
from gestures.gesture_state import GestureState


@dataclass(frozen=True)
class ActionEvent:
    name: str
    context: dict


class GestureDetector:
    def __init__(self, config: GestureConfig):
        config.validate()
        self.config = config
        self.state = GestureState.IDLE
        self._start_time_ms: int | None = None
        self._last_time_ms: int | None = None
        self._filtered_position: tuple[float, float] | None = None
        self._last_speed = 0.0
        self._peak_speed = 0.0
        self._movement_distance = 0.0
        self._precise_scroll_y = 0.0
        self._fast_movement_y = 0.0
        self._fast_scroll_candidate = False
        self._precise_scroll = False
        self._pending_click_deadline_ms: int | None = None
        self._open_frames = 0

    def reset(self) -> None:
        self.state = GestureState.IDLE
        self._start_time_ms = None
        self._last_time_ms = None
        self._filtered_position = None
        self._last_speed = 0.0
        self._peak_speed = 0.0
        self._movement_distance = 0.0
        self._precise_scroll_y = 0.0
        self._fast_movement_y = 0.0
        self._fast_scroll_candidate = False
        self._precise_scroll = False
        self._pending_click_deadline_ms = None
        self._open_frames = 0

    def update(
        self,
        pinch_distance: float | None,
        wrist_position: tuple[float, float] | None,
        timestamp_ms: int,
    ) -> list[ActionEvent]:
        if self._last_time_ms is not None and timestamp_ms < self._last_time_ms:
            raise ValueError("Gesture timestamps must be monotonic")

        events: list[ActionEvent] = []
        if (
            self._pending_click_deadline_ms is not None
            and timestamp_ms >= self._pending_click_deadline_ms
        ):
            events.append(ActionEvent("LEFT_CLICK", {}))
            self._pending_click_deadline_ms = None

        pinch_closed = (
            pinch_distance is not None
            and pinch_distance <= self.config.pinch_threshold
            and wrist_position is not None
        )

        if self.state == GestureState.COOLDOWN:
            if not pinch_closed:
                self._open_frames += 1
                if self._open_frames >= 1:
                    self.state = GestureState.IDLE
            else:
                self._open_frames = 0
            self._last_time_ms = timestamp_ms
            return events

        if self.state == GestureState.IDLE:
            if pinch_closed:
                self._begin(wrist_position, timestamp_ms)
            self._last_time_ms = timestamp_ms
            return events

        if not pinch_closed:
            events.extend(self._finish(timestamp_ms))
            self.state = GestureState.COOLDOWN
            self._open_frames = 1
            self._last_time_ms = timestamp_ms
            return events

        events.extend(self._advance(wrist_position, timestamp_ms))
        self._last_time_ms = timestamp_ms
        return events

    def _begin(self, position: tuple[float, float], timestamp_ms: int) -> None:
        self.state = GestureState.PINCH_DETECTED
        self._start_time_ms = timestamp_ms
        self._last_time_ms = timestamp_ms
        self._filtered_position = position
        self._last_speed = 0.0
        self._peak_speed = 0.0
        self._movement_distance = 0.0
        self._precise_scroll_y = 0.0
        self._fast_movement_y = 0.0
        self._fast_scroll_candidate = False
        self._precise_scroll = False

    def _advance(self, position: tuple[float, float], timestamp_ms: int) -> list[ActionEvent]:
        assert self._start_time_ms is not None
        assert self._last_time_ms is not None
        smoothing = self.config.movement_smoothing
        alpha = 1.0 - smoothing
        previous_filtered = self._filtered_position or position
        filtered = (
            alpha * position[0] + smoothing * previous_filtered[0],
            alpha * position[1] + smoothing * previous_filtered[1],
        )
        self._filtered_position = filtered

        elapsed_ms = max(timestamp_ms - self._last_time_ms, 1)
        delta_x = filtered[0] - previous_filtered[0]
        delta_y = filtered[1] - previous_filtered[1]
        delta = hypot(delta_x, delta_y)
        if delta < self.config.jitter_threshold:
            delta_x = 0.0
            delta_y = 0.0
            delta = 0.0

        speed = delta / (elapsed_ms / 1000.0)
        acceleration = abs(speed - self._last_speed) / (elapsed_ms / 1000.0)
        self._last_speed = speed
        self._peak_speed = max(self._peak_speed, speed)
        duration_ms = timestamp_ms - self._start_time_ms

        if not self._precise_scroll and not self._fast_scroll_candidate:
            if (
                speed >= self.config.fast_scroll_threshold
                and acceleration >= self.config.fast_scroll_acceleration_threshold
            ):
                self._fast_scroll_candidate = True
                self.state = GestureState.FAST_SCROLL_CANDIDATE

        if self._fast_scroll_candidate:
            self._fast_movement_y += delta_y
        else:
            self._movement_distance += delta
            max_delta_y = self.config.max_scroll_speed * (elapsed_ms / 1000.0)
            delta_y = copysign(min(abs(delta_y), max_delta_y), delta_y)
            self._precise_scroll_y += delta_y
            if self._movement_distance >= self.config.movement_threshold:
                self._precise_scroll = True
                self.state = GestureState.PRECISE_SCROLL
            elif duration_ms >= self.config.short_pinch_max_duration_ms:
                self.state = GestureState.HOLDING

        if self._precise_scroll and self._precise_scroll_y != 0:
            scroll_y = self._precise_scroll_y
            self._precise_scroll_y = 0.0
            return [
                ActionEvent(
                    "SCROLL",
                    {"mode": "precise", "amount": -scroll_y * self.config.precise_sensitivity},
                )
            ]
        return []

    def _finish(self, timestamp_ms: int) -> list[ActionEvent]:
        assert self._start_time_ms is not None
        duration_ms = timestamp_ms - self._start_time_ms
        self.state = GestureState.RELEASED

        if self._precise_scroll:
            return []
        if self._fast_scroll_candidate:
            if self._fast_movement_y == 0:
                return []
            speed_factor = min(self._peak_speed, self.config.max_scroll_speed) / self.config.fast_scroll_threshold
            amount = -copysign(self.config.fast_scroll_intensity * speed_factor, self._fast_movement_y)
            return [
                ActionEvent(
                    "SCROLL",
                    {
                        "mode": "fast",
                        "amount": amount,
                        "duration_ms": self.config.fast_scroll_duration_ms,
                    },
                )
            ]
        if duration_ms <= self.config.short_pinch_max_duration_ms:
            self.state = GestureState.SHORT_PINCH
            if (
                self._pending_click_deadline_ms is not None
                and timestamp_ms < self._pending_click_deadline_ms
            ):
                self._pending_click_deadline_ms = None
                return [ActionEvent("DOUBLE_CLICK", {})]
            self._pending_click_deadline_ms = timestamp_ms + self.config.double_click_interval_ms
            return []
        if (
            duration_ms >= self.config.right_click_hold_ms
            and self._movement_distance < self.config.movement_threshold
        ):
            return [ActionEvent("RIGHT_CLICK", {})]
        return []
