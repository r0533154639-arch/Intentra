from __future__ import annotations

import httpx
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.lifecycle import ApplicationLifecycle
from ui.calibration_window import CalibrationWindow
from ui.settings_window import SettingsWindow
from services.update_service import UpdateService
from user.user_settings import UserSettings
from vision.frame_pipeline import FramePipeline


class PipelineSignals(QObject):
    status_changed = Signal(dict)
    eye_features = Signal(object)
    error_occurred = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self, lifecycle: ApplicationLifecycle, update_service: UpdateService):
        super().__init__()
        self.lifecycle = lifecycle
        self.update_service = update_service
        self.pipeline: FramePipeline | None = None
        self.settings: UserSettings | None = None
        self._pending_release: dict | None = None
        self._verified_package = None
        self.signals = PipelineSignals()
        self.camera_status = QLabel("Camera: inactive")
        self.face_status = QLabel("Face detection: not started")
        self.hand_status = QLabel("Hand detection: not started")
        self.gaze_status = QLabel("Gaze calibration: required")
        self.gesture_status = QLabel("Gesture configuration: not configured")
        self.account_status = QLabel("Associated account: not paired")
        self.server_status = QLabel("Server: connecting")
        self.control_status = QLabel("Mouse control: paused")
        self.message = QLabel()
        self.pairing_code = QLabel()
        self.control_button = QPushButton("Enable mouse control")
        self.calibration_button = QPushButton("Calibrate gaze")
        self.settings_button = QPushButton("Local settings")
        self.update_status = QLabel("Updates: not checked")
        self.check_updates_button = QPushButton("Check for updates")
        self.download_update_button = QPushButton("Download and verify update")
        self.install_update_button = QPushButton("Install verified update")

        self.control_button.clicked.connect(self.toggle_control)
        self.calibration_button.clicked.connect(self.calibrate_gaze)
        self.settings_button.clicked.connect(self.open_local_settings)
        self.check_updates_button.clicked.connect(self.check_for_updates)
        self.download_update_button.clicked.connect(self.download_update)
        self.install_update_button.clicked.connect(self.install_update)
        self.signals.status_changed.connect(self.update_pipeline_status)
        self.signals.error_occurred.connect(self.show_error)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(self.camera_status)
        layout.addWidget(self.face_status)
        layout.addWidget(self.hand_status)
        layout.addWidget(self.gaze_status)
        layout.addWidget(self.gesture_status)
        layout.addWidget(self.account_status)
        layout.addWidget(self.server_status)
        layout.addWidget(self.control_status)
        layout.addWidget(self.pairing_code)
        layout.addWidget(self.calibration_button)
        layout.addWidget(self.control_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.update_status)
        layout.addWidget(self.check_updates_button)
        layout.addWidget(self.download_update_button)
        layout.addWidget(self.install_update_button)
        layout.addWidget(self.message)
        self.setCentralWidget(content)
        self.setWindowTitle("Intentra")
        self.resize(520, 460)
        self.download_update_button.setEnabled(False)
        self.install_update_button.setEnabled(False)
        self._refresh_controls()

    def show_pairing(self, code: str, expires_at: str) -> None:
        self.pairing_code.setText(
            f"Pair this desktop from the signed-in web app at /devices. "
            f"Enter code: {code} (expires {expires_at})"
        )
        self.account_status.setText("Associated account: awaiting web pairing")
        self.server_status.setText("Server: connected; waiting for account approval")

    def show_ready(self, settings: UserSettings, status: str) -> None:
        self.settings = settings
        self.account_status.setText("Associated account: " + (settings.user_id or "paired"))
        self.pairing_code.clear()
        self.server_status.setText(f"Server: {status.replace('_', ' ')}")
        self.gaze_status.setText(
            "Gaze calibration: complete" if settings.calibration_data else "Gaze calibration: required"
        )
        self._refresh_controls()

    def set_pipeline(self, pipeline: FramePipeline) -> None:
        self.pipeline = pipeline
        try:
            pipeline.start()
        except (OSError, RuntimeError) as exc:
            self.show_error(str(exc))
            return
        self._refresh_controls()

    def update_pipeline_status(self, status: dict) -> None:
        self.camera_status.setText(f"Camera: {status['camera']}")
        self.face_status.setText(f"Face detection: {status['face']}")
        self.hand_status.setText(f"Hand detection: {status['hand']}")
        self.gaze_status.setText(
            "Gaze calibration: complete" if status["gaze_calibrated"] else "Gaze calibration: required"
        )
        if status["gesture_enabled"]:
            self.gesture_status.setText("Gesture detection: configured and active")
        else:
            self.gesture_status.setText(
                f"Gesture detection: disabled ({status['gesture_message'] or 'not configured'})"
            )
        self.control_status.setText(
            "Mouse control: ACTIVE" if status["control_enabled"] else "Mouse control: paused"
        )
        self._refresh_controls()

    def show_error(self, message: str) -> None:
        self.message.setText(message)

    def toggle_control(self) -> None:
        if self.pipeline is None:
            self.show_error("The camera and detection pipeline are not available.")
            return
        enabled = not self.pipeline.control_enabled
        try:
            self.pipeline.set_control_enabled(enabled)
        except RuntimeError as exc:
            self.show_error(str(exc))

    def calibrate_gaze(self) -> None:
        if self.pipeline is None:
            self.show_error("The camera must be active before gaze calibration.")
            return
        self.pipeline.set_control_enabled(False)

        def save_calibration(data: dict):
            settings = self.lifecycle.save_calibration(data)
            self.pipeline.update_settings(settings)
            self.show_ready(settings, "synchronized")

        window = CalibrationWindow(
            self.pipeline.gaze_estimator,
            self.pipeline.recent_eye_features,
            save_calibration,
            self,
        )
        window.exec()
        self._refresh_controls()

    def open_local_settings(self) -> None:
        window = SettingsWindow(self.lifecycle.config, self.settings, self)
        window.exec()

    def update_settings(self, settings: UserSettings, status: str) -> None:
        self.settings = settings
        if self.pipeline:
            self.pipeline.update_settings(settings)
        self.show_ready(settings, status)

    def check_for_updates(self) -> None:
        self.message.clear()
        self.download_update_button.setEnabled(False)
        self.install_update_button.setEnabled(False)
        self._pending_release = None
        self._verified_package = None
        try:
            result = self.update_service.check_for_update()
            if result["update_available"]:
                self._pending_release = result["latest"]
                self.update_status.setText(f"Update available: {result['latest']['version']}")
                self.download_update_button.setEnabled(True)
            else:
                self.update_status.setText("Updates: up to date")
        except (httpx.HTTPError, KeyError, ValueError, RuntimeError) as exc:
            self.update_status.setText("Updates: check failed")
            self.show_error(str(exc))

    def download_update(self) -> None:
        if self._pending_release is None:
            self.show_error("Check for updates before downloading.")
            return
        try:
            self._verified_package = self.update_service.download_and_verify(self._pending_release)
            self.install_update_button.setEnabled(True)
            self.update_status.setText("Update package downloaded and signature verified")
        except (httpx.HTTPError, OSError, KeyError, ValueError, RuntimeError) as exc:
            self.update_status.setText("Updates: verification failed")
            self.show_error(str(exc))

    def install_update(self) -> None:
        if self._verified_package is None:
            self.show_error("Download and verify the update before installing it.")
            return
        try:
            self.update_service.install(self._verified_package)
            self.update_status.setText("Verified installer launched; approve the Windows prompt to continue")
        except (OSError, ValueError, RuntimeError) as exc:
            self.show_error(str(exc))

    def _refresh_controls(self) -> None:
        has_pipeline = self.pipeline is not None
        gaze_ready = self.pipeline.gaze_calibrated if self.pipeline else False
        self.calibration_button.setEnabled(has_pipeline)
        self.control_button.setEnabled(has_pipeline and gaze_ready)
        active = self.pipeline is not None and self.pipeline.control_enabled
        self.control_button.setText("Pause mouse control" if active else "Enable mouse control")

    def closeEvent(self, event):
        if self.pipeline:
            self.pipeline.stop()
        self.lifecycle.close()
        event.accept()
