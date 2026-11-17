from __future__ import annotations

from dataclasses import dataclass
from math import hypot

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from vision.models import HAND_LANDMARKER_MODEL, require_model

THUMB_TIP = 4
INDEX_TIP = 8
INDEX_MCP = 5
WRIST = 0


@dataclass(frozen=True)
class HandObservation:
    pinch_distance: float
    wrist_position: tuple[float, float]


class HandTracker:
    def __init__(self):
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(
            model_asset_buffer=require_model(HAND_LANDMARKER_MODEL).read_bytes()
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1

    def process(self, frame, timestamp_ms: int) -> HandObservation | None:
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.hand_landmarks:
            return None

        landmarks = result.hand_landmarks[0]
        thumb = landmarks[THUMB_TIP]
        index = landmarks[INDEX_TIP]
        wrist = landmarks[WRIST]
        palm = landmarks[INDEX_MCP]
        palm_scale = max(hypot(palm.x - wrist.x, palm.y - wrist.y), 1e-6)
        pinch_distance = hypot(thumb.x - index.x, thumb.y - index.y) / palm_scale
        return HandObservation(
            pinch_distance=pinch_distance,
            wrist_position=(float(wrist.x), float(wrist.y)),
        )

    def close(self) -> None:
        self._landmarker.close()
