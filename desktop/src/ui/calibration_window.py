from __future__ import annotations

import httpx
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from vision.calibration import CalibrationSession
from vision.gaze_estimator import GazeEstimator


class CalibrationWindow(QDialog):
    def __init__(
        self,
        gaze_estimator: GazeEstimator,
        sample_provider,
        save_callback,
        parent=None,
    ):
        super().__init__(parent)
        self.gaze_estimator = gaze_estimator
        self.sample_provider = sample_provider
        self.save_callback = save_callback
        self.session = CalibrationSession()
        self.instruction = QLabel()
        self.message = QLabel()
        self.marker = QLabel(" ", self)
        self.marker.setFixedSize(24, 24)
        self.marker.setStyleSheet("background: #e11d48; border-radius: 12px;")
        self.capture_button = QPushButton("Capture target (Space)")
        self.capture_button.clicked.connect(self.capture_target)

        layout = QVBoxLayout(self)
        layout.addWidget(self.instruction, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(self.message, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.capture_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setWindowTitle("Intentra gaze calibration")
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setWindowState(self.windowState() | Qt.WindowState.WindowFullScreen)
        self.setStyleSheet("background: #111827; color: white; font-size: 16px;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_target()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_target()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.capture_target()
            return
        super().keyPressEvent(event)

    def _position_target(self):
        if self.width() <= 0 or self.height() <= 0:
            return
        target = self.session.current_target
        x = int(target.x * self.width() - self.marker.width() / 2)
        y = int(target.y * self.height() - self.marker.height() / 2)
        self.marker.move(x, y)
        self.marker.raise_()
        self.instruction.setText(
            f"Look at target {self.session.current_index + 1} of {len(self.session.targets)}, then press Space"
        )

    def capture_target(self):
        try:
            self.session.capture(self.sample_provider())
            if self.session.complete:
                self.gaze_estimator.calibrate(self.session.samples)
                self.save_callback(self.gaze_estimator.to_dict())
                self.accept()
                return
            self.message.setText("")
            self._position_target()
        except (ValueError, ConnectionError, httpx.HTTPError, OSError) as exc:
            self.message.setText(str(exc))
