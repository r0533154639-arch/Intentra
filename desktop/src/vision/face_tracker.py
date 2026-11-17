from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from vision.models import FACE_LANDMARKER_MODEL, require_model

LEFT_IRIS = range(468, 473)
RIGHT_IRIS = range(473, 478)


class FaceTracker:
    def __init__(self):
        options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(
            model_asset_buffer=require_model(FACE_LANDMARKER_MODEL).read_bytes()
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1

    @staticmethod
    def _eye_feature(
        landmarks,
        iris_indexes: range,
        corner_indexes: tuple[int, int],
        lid_indexes: tuple[int, int],
    ) -> tuple[float, float]:
        iris_x = float(np.mean([landmarks[index].x for index in iris_indexes]))
        iris_y = float(np.mean([landmarks[index].y for index in iris_indexes]))
        corners = [landmarks[index].x for index in corner_indexes]
        lids = [landmarks[index].y for index in lid_indexes]
        width = max(abs(corners[1] - corners[0]), 1e-6)
        height = max(abs(lids[1] - lids[0]), 1e-6)
        horizontal = (iris_x - min(corners)) / width
        vertical = (iris_y - min(lids)) / height
        return horizontal, vertical

    @classmethod
    def extract_eye_features(cls, landmarks) -> np.ndarray:
        if len(landmarks) < 478:
            raise RuntimeError(
                "The Face Landmarker did not return iris landmarks required for gaze estimation"
            )
        left = cls._eye_feature(landmarks, LEFT_IRIS, (33, 133), (159, 145))
        right = cls._eye_feature(landmarks, RIGHT_IRIS, (362, 263), (386, 374))
        return np.asarray((*left, *right), dtype=np.float64)

    def process(self, frame, timestamp_ms: int) -> np.ndarray | None:
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.face_landmarks:
            return None
        return self.extract_eye_features(result.face_landmarks[0])

    def close(self) -> None:
        self._landmarker.close()
