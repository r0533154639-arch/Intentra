from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QPushButton, QVBoxLayout

from app.configuration import DesktopConfig
from user.user_settings import UserSettings


class SettingsWindow(QDialog):
    def __init__(
        self,
        config: DesktopConfig,
        settings: UserSettings | None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Intentra local settings")
        self.setMinimumWidth(420)

        form = QFormLayout()
        self._add_value(form, "Camera device", str(config.camera_index))
        self._add_value(form, "Backend", config.server_base_url)
        self._add_value(form, "Associated account", settings.user_id if settings and settings.user_id else "Not paired")
        self._add_value(
            form,
            "Gaze calibration",
            "Complete" if settings and settings.calibration_data else "Required",
        )
        self._add_value(form, "Cursor smoothing", self._number(settings.smoothing) if settings else "Unavailable")
        self._add_value(form, "Cursor sensitivity", self._number(settings.sensitivity) if settings else "Unavailable")
        self._add_value(
            form,
            "Gesture configuration",
            "Configured" if settings and settings.pinch_threshold > 0 else "Not configured",
        )
        self._add_value(
            form,
            "Settings version",
            str(settings.version) if settings else "Unavailable",
        )

        explanation = QLabel(
            "Account and gesture settings are managed in the Intentra web app. "
            "Pause control or start gaze calibration from the main window."
        )
        explanation.setWordWrap(True)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(explanation)
        layout.addWidget(close_button)

    @staticmethod
    def _add_value(form: QFormLayout, name: str, value: str) -> None:
        label = QLabel(value)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow(name, label)

    @staticmethod
    def _number(value: float) -> str:
        return f"{value:g}"
