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
        iris_x = float(np.median([landmarks[index].x for index in iris_indexes]))
        iris_y = float(np.median([landmarks[index].y for index in iris_indexes]))
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
        left_eye_center = np.array([
            (landmarks[33].x + landmarks[133].x) / 2,
            (landmarks[33].y + landmarks[133].y) / 2,
        ])
        right_eye_center = np.array([
            (landmarks[362].x + landmarks[263].x) / 2,
            (landmarks[362].y + landmarks[263].y) / 2,
        ])
        roll = float(np.arctan2(
            right_eye_center[1] - left_eye_center[1],
            right_eye_center[0] - left_eye_center[0],
        ))
        cosine = float(np.cos(-roll))
        sine = float(np.sin(-roll))

        def unroll(point, origin):
            translated = point - origin
            return np.array([
                cosine * translated[0] - sine * translated[1],
                sine * translated[0] + cosine * translated[1],
            ]) + origin

        def compensated_eye_feature(iris_indexes, corner_indexes, lid_indexes, origin):
            iris = unroll(np.array([
                np.median([landmarks[index].x for index in iris_indexes]),
                np.median([landmarks[index].y for index in iris_indexes]),
            ]), origin)
            corners = np.array([
                unroll(np.array([landmarks[index].x, landmarks[index].y]), origin)
                for index in corner_indexes
            ])
            lids = np.array([
                unroll(np.array([landmarks[index].x, landmarks[index].y]), origin)
                for index in lid_indexes
            ])
            width = max(abs(corners[1, 0] - corners[0, 0]), 1e-6)
            height = max(abs(lids[1, 1] - lids[0, 1]), 1e-6)
            horizontal = (iris[0] - corners[:, 0].min()) / width
            vertical = (iris[1] - lids[:, 1].min()) / height
            return float(horizontal), float(vertical), float(height / width)

        left = compensated_eye_feature(LEFT_IRIS, (33, 133), (159, 145), left_eye_center)
        right = compensated_eye_feature(RIGHT_IRIS, (362, 263), (386, 374), right_eye_center)
        eye_openness = min(left[2], right[2])
        if eye_openness < 0.08:
            raise RuntimeError("Eyes are closed or only partially visible")
        return np.asarray((left[0], left[1], right[0], right[1]), dtype=np.float64)

    def process(self, frame, timestamp_ms: int) -> np.ndarray | None:
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.face_landmarks:
            return None
        try:
            return self.extract_eye_features(result.face_landmarks[0])
        except RuntimeError:
            return None

    def close(self) -> None:
        self._landmarker.close()
