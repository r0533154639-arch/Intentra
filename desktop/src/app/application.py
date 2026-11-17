from __future__ import annotations

import httpx
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.configuration import DesktopConfig
from app.lifecycle import ApplicationLifecycle
from input_control.mouse_controller import MouseController
from services.update_service import UpdateService
from ui.main_window import MainWindow
from user.user_settings import UserSettings
from vision.camera import CameraManager
from vision.face_tracker import FaceTracker
from vision.frame_pipeline import FramePipeline
from vision.gaze_estimator import GazeEstimator
from vision.hand_tracker import HandTracker


class IntentraApp:
    def __init__(self):
        self.config = DesktopConfig.load()
        self.lifecycle = ApplicationLifecycle(self.config)
        self.window: MainWindow | None = None
        self.pipeline: FramePipeline | None = None
        self._pairing_timer: QTimer | None = None
        self._retry_timer: QTimer | None = None
        self._settings_timer: QTimer | None = None

    def run(self) -> int:
        application = QApplication.instance() or QApplication([])
        update_service = UpdateService(self.lifecycle.api_client, self.config.update_public_key)
        self.window = MainWindow(self.lifecycle, update_service)
        self.window.show()
        try:
            result = self.lifecycle.start()
            self._apply_lifecycle_result(result)
        except (ConnectionError, httpx.HTTPError, OSError, RuntimeError) as exc:
            self.window.show_error(str(exc))
            self._start_connection_retry()
        return application.exec()

    def _apply_lifecycle_result(self, result: dict) -> None:
        if result["status"] == "pairing_required":
            self.window.show_pairing(result["pairing_code"], result["expires_at"])
            self._start_pairing_poll()
        elif "settings" in result:
            self.window.show_ready(result["settings"], result["status"])
            self._start_pipeline(result["settings"])
            self._start_settings_poll()
        else:
            raise RuntimeError(f"Unexpected desktop lifecycle state: {result['status']}")

    def _start_pipeline(self, settings: UserSettings) -> None:
        if self.pipeline is not None:
            self.pipeline.stop()
        try:
            gaze_estimator = GazeEstimator()
            gaze_estimator.load(settings.calibration_data)
            pipeline = FramePipeline(
                camera=CameraManager(self.config.camera_index),
                face_tracker=FaceTracker(),
                hand_tracker=HandTracker(),
                gaze_estimator=gaze_estimator,
                mouse_controller=MouseController(),
                settings=settings,
                on_status=self.window.signals.status_changed.emit,
                on_eye_features=self.window.signals.eye_features.emit,
                on_error=self.window.signals.error_occurred.emit,
            )
        except (FileNotFoundError, OSError, RuntimeError) as exc:
            self.window.show_error(str(exc))
            return
        self.pipeline = pipeline
        self.window.set_pipeline(pipeline)

    def _start_pairing_poll(self) -> None:
        if self._pairing_timer is None:
            self._pairing_timer = QTimer(self.window)
            self._pairing_timer.timeout.connect(self._poll_pairing)
        self._pairing_timer.start(2500)

    def _poll_pairing(self) -> None:
        try:
            result = self.lifecycle.poll_pairing()
            if result["status"] == "paired" and "settings" not in result:
                return
            if result["status"] == "expired":
                pairing = self.lifecycle.begin_pairing()
                self.window.show_pairing(pairing["pairing_code"], pairing["expires_at"])
                return
            if "settings" in result:
                if self.pipeline is None:
                    self._pairing_timer.stop()
                    self.window.show_ready(result["settings"], result["status"])
                    self._start_pipeline(result["settings"])
                    self._start_settings_poll()
                elif (
                    self.window.settings is not None
                    and result["settings"].version != self.window.settings.version
                ):
                    self.window.update_settings(result["settings"], result["status"])
        except (ConnectionError, httpx.HTTPError, OSError, RuntimeError) as exc:
            self.window.show_error(str(exc))

    def _start_connection_retry(self) -> None:
        if self._retry_timer is None:
            self._retry_timer = QTimer(self.window)
            self._retry_timer.timeout.connect(self._retry_startup)
        self._retry_timer.start(10000)

    def _retry_startup(self) -> None:
        try:
            result = self.lifecycle.start()
            self._retry_timer.stop()
            self._apply_lifecycle_result(result)
        except (ConnectionError, httpx.HTTPError, OSError, RuntimeError) as exc:
            self.window.show_error(str(exc))

    def _start_settings_poll(self) -> None:
        if self._settings_timer is None:
            self._settings_timer = QTimer(self.window)
            self._settings_timer.timeout.connect(self._refresh_settings)
        self._settings_timer.start(30000)

    def _refresh_settings(self) -> None:
        try:
            was_paired = self.pipeline is not None
            result = self.lifecycle.refresh_settings()
            if result.get("status") == "pairing_required":
                if self.pipeline:
                    self.pipeline.stop()
                    self.pipeline = None
                self.window.show_pairing(result["pairing_code"], result["expires_at"])
                self._start_pairing_poll()
                return
            updated = result.get("settings")
            if not was_paired and updated is not None:
                self.window.show_ready(updated, result["status"])
                self._start_pipeline(updated)
                self._start_settings_poll()
            elif (
                updated is not None
                and self.window.settings is not None
                and updated.version != self.window.settings.version
            ):
                self.window.update_settings(updated, result["status"])
        except (ConnectionError, httpx.HTTPError, OSError, RuntimeError) as exc:
            self.window.show_error(str(exc))
