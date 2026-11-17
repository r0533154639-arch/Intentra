from __future__ import annotations

import cv2


class CameraManager:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self._capture: cv2.VideoCapture | None = None

    def start(self) -> None:
        if self._capture is not None:
            return
        capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Could not open camera device {self.camera_index}")
        self._capture = capture

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def read_frame(self):
        if self._capture is None:
            raise RuntimeError("Camera has not been started")
        success, frame = self._capture.read()
        if not success or frame is None:
            raise RuntimeError("Camera frame capture failed")
        return frame
