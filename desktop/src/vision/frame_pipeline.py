from __future__ import annotations

import sys
import threading
import time
from collections import deque

import pyautogui
from pyautogui import PyAutoGUIException

from actions.action_dispatcher import ActionDispatcher
from gestures.gesture_config import GestureConfig
from gestures.gesture_detector import ActionEvent, GestureDetector
from input_control.mouse_controller import MouseController
from user.user_settings import UserSettings
from vision.camera import CameraManager
from vision.face_tracker import FaceTracker
from vision.gaze_estimator import GazeEstimator
from vision.hand_tracker import HandTracker


def _console_print(message: str) -> None:
    if sys.stdout is not None:
        print(message, flush=True)


def _log_gesture_action(event: ActionEvent) -> None:
    if event.name == "SCROLL":
        amount = float(event.context["amount"])
        direction = "up" if amount > 0 else "down" if amount < 0 else "no movement"
        mode = event.context.get("mode", "precise")
        description = f"{mode.title()} scroll {direction} (amount={amount:+.2f}"
        if mode == "fast":
            description += f", duration={int(event.context['duration_ms'])} ms"
        description += ")"
    else:
        description = {
            "LEFT_CLICK": "Single left click",
            "DOUBLE_CLICK": "Double-click",
            "RIGHT_CLICK": "Right-click",
        }.get(event.name, event.name.replace("_", " ").title())

    _console_print(f"[Intentra] Action detected: {description}")


def _log_hand_sample(pinch_distance: float, pinch_threshold: float) -> None:
    pinch_state = "pinch detected" if pinch_distance <= pinch_threshold else "no pinch"
    _console_print(
        "[Intentra] Hand input: "
        f"pinch distance={pinch_distance:.3f}, "
        f"threshold={pinch_threshold:.3f} ({pinch_state})"
    )


class FramePipeline:
    def __init__(
        self,
        camera: CameraManager,
        face_tracker: FaceTracker,
        hand_tracker: HandTracker,
        gaze_estimator: GazeEstimator,
        mouse_controller: MouseController,
        settings: UserSettings,
        on_status,
        on_eye_features,
        on_error,
    ):
        self.camera = camera
        self.face_tracker = face_tracker
        self.hand_tracker = hand_tracker
        self.gaze_estimator = gaze_estimator
        self.mouse_controller = mouse_controller
        self.dispatcher = ActionDispatcher(mouse_controller)
        self.on_status = on_status
        self.on_eye_features = on_eye_features
        self.on_error = on_error
        self._stop_event = threading.Event()
        self._cancel_actions = threading.Event()
        self._control_enabled = threading.Event()
        self._settings_lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._eye_features: deque = deque(maxlen=30)
        self._features_lock = threading.Lock()
        self._settings = settings
        self._gesture_detector: GestureDetector | None = None
        self._gesture_error: str | None = None
        self._install_settings(settings)

    @property
    def gaze_calibrated(self) -> bool:
        return self.gaze_estimator.is_calibrated

    @property
    def control_enabled(self) -> bool:
        return self._control_enabled.is_set()

    @property
    def gesture_error(self) -> str | None:
        return self._gesture_error

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self.camera.start()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="intentra-frame-pipeline", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.pause()
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
            if self._thread.is_alive():
                raise TimeoutError("Camera processing thread did not stop in time")
        self.camera.stop()
        self.face_tracker.close()
        self.hand_tracker.close()

    def pause(self) -> None:
        self._control_enabled.clear()
        self._cancel_actions.set()
        self._reset_gesture_state()
        self._publish_status()

    def set_control_enabled(self, enabled: bool) -> None:
        if enabled and not self.gaze_estimator.is_calibrated:
            raise RuntimeError("Calibrate gaze tracking before enabling mouse control")
        if enabled and self._gesture_detector is None:
            raise RuntimeError(
                self._gesture_error or "Complete gesture calibration before enabling mouse control"
            )
        if enabled:
            self._cancel_actions.clear()
            self._control_enabled.set()
        else:
            self._control_enabled.clear()
            self._cancel_actions.set()
            with self._settings_lock:
                if self._gesture_detector:
                    self._gesture_detector.reset()
        self._publish_status()

    def update_settings(self, settings: UserSettings) -> None:
        with self._settings_lock:
            self._settings = settings
            self.gaze_estimator.load(settings.calibration_data)
            self._install_settings(settings)
        if self.gaze_estimator.is_calibrated is False:
            self.set_control_enabled(False)
        self._publish_status()

    def set_calibration(self, calibration_data: dict) -> None:
        with self._settings_lock:
            self.gaze_estimator.load(calibration_data)
            self._settings.calibration_data = calibration_data
        self._publish_status()

    def _reset_gesture_state(self) -> None:
        with self._settings_lock:
            if self._gesture_detector:
                self._gesture_detector.reset()

    def recent_eye_features(self) -> list:
        with self._features_lock:
            return list(self._eye_features)

    def _install_settings(self, settings: UserSettings) -> None:
        payload = settings.as_server_payload()
        try:
            config = GestureConfig.from_settings(payload)
        except (KeyError, TypeError, ValueError) as exc:
            self._gesture_detector = None
            self._gesture_error = str(exc)
            return
        self._gesture_detector = GestureDetector(config)
        self._gesture_error = None

    def _publish_status(self, face: str = "starting", hand: str = "starting") -> None:
        self.on_status(
            {
                "camera": "active" if self._thread and self._thread.is_alive() else "inactive",
                "face": face,
                "hand": hand,
                "gaze_calibrated": self.gaze_estimator.is_calibrated,
                "gesture_enabled": self._gesture_detector is not None,
                "gesture_message": self._gesture_error,
                "control_enabled": self._control_enabled.is_set(),
            }
        )

    def _run(self) -> None:
        last_status_time = 0.0
        last_gesture_diagnostic_time = 0.0
        try:
            while not self._stop_event.is_set():
                frame = self.camera.read_frame()
                timestamp_ms = time.monotonic_ns() // 1_000_000
                eye_features = self.face_tracker.process(frame, timestamp_ms)
                hand = self.hand_tracker.process(frame, timestamp_ms)
                if eye_features is not None:
                    with self._features_lock:
                        self._eye_features.append(eye_features)
                    self.on_eye_features(eye_features)

                if self._control_enabled.is_set():
                    with self._settings_lock:
                        if eye_features is not None and self.gaze_estimator.is_calibrated:
                            settings = self._settings
                            gaze = self.gaze_estimator.estimate(
                                eye_features,
                                sensitivity=settings.sensitivity,
                                smoothing=settings.smoothing,
                                timestamp_ms=timestamp_ms,
                            )
                            screen_width, screen_height = pyautogui.size()
                            self.dispatcher.dispatch(
                                "MOVE_CURSOR",
                                {"x": gaze.x * (screen_width - 1), "y": gaze.y * (screen_height - 1)},
                            )
                        if self._gesture_detector:
                            observation = hand
                            if (
                                observation is not None
                                and time.monotonic() - last_gesture_diagnostic_time >= 1.0
                            ):
                                _log_hand_sample(
                                    observation.pinch_distance,
                                    self._gesture_detector.config.pinch_threshold,
                                )
                                last_gesture_diagnostic_time = time.monotonic()
                            events = self._gesture_detector.update(
                                observation.pinch_distance if observation else None,
                                observation.wrist_position if observation else None,
                                timestamp_ms,
                            )
                            for event in events:
                                _log_gesture_action(event)
                                self.dispatcher.dispatch(
                                    event.name,
                                    {**event.context, "cancel_event": self._cancel_actions},
                                )

                now = time.monotonic()
                if now - last_status_time >= 0.5:
                    self._publish_status(
                        face="detected" if eye_features is not None else "not detected",
                        hand="detected" if hand is not None else "not detected",
                    )
                    last_status_time = now
        except (OSError, RuntimeError, ValueError, PyAutoGUIException) as exc:
            self.on_error(str(exc))
        finally:
            self._control_enabled.clear()
            self._cancel_actions.set()
            self._reset_gesture_state()
            self.camera.stop()
            self._publish_status(face="stopped", hand="stopped")
