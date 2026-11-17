from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class GazeSample:
    x: float
    y: float


class GazeEstimator:
    def __init__(self):
        self._coefficients: np.ndarray | None = None
        self._previous: np.ndarray | None = None
        self.sample_count = 0

    @property
    def is_calibrated(self) -> bool:
        return self._coefficients is not None

    def calibrate(
        self,
        samples: Iterable[tuple[Sequence[float], tuple[float, float]]],
    ) -> dict:
        observations = list(samples)
        if len(observations) < 5:
            raise ValueError("Gaze calibration requires at least five screen-point samples")

        features = np.asarray([sample[0] for sample in observations], dtype=np.float64)
        targets = np.asarray([sample[1] for sample in observations], dtype=np.float64)
        if features.ndim != 2 or features.shape[1] != 4 or targets.shape != (len(observations), 2):
            raise ValueError("Gaze calibration samples have invalid dimensions")
        if not np.isfinite(features).all() or not np.isfinite(targets).all():
            raise ValueError("Gaze calibration samples must contain finite values")

        design = np.column_stack((np.ones(len(features)), features))
        coefficients, _, rank, _ = np.linalg.lstsq(design, targets, rcond=None)
        if rank < 3:
            raise ValueError("Gaze calibration points do not provide enough independent variation")

        self._coefficients = coefficients
        self._previous = None
        self.sample_count = len(observations)
        return self.to_dict()

    def load(self, calibration_data: dict | None) -> bool:
        if not calibration_data:
            self._coefficients = None
            self._previous = None
            self.sample_count = 0
            return False
        coefficients = calibration_data.get("coefficients")
        if not isinstance(coefficients, list):
            self._coefficients = None
            self._previous = None
            self.sample_count = 0
            raise ValueError("Stored gaze calibration is missing its coefficients")
        array = np.asarray(coefficients, dtype=np.float64)
        if array.shape != (5, 2) or not np.isfinite(array).all():
            raise ValueError("Stored gaze calibration coefficients are invalid")
        self._coefficients = array
        self.sample_count = int(calibration_data.get("sample_count", 0))
        self._previous = None
        return True

    def to_dict(self) -> dict:
        if self._coefficients is None:
            return {}
        return {
            "coefficients": self._coefficients.tolist(),
            "sample_count": self.sample_count,
        }

    def estimate(
        self,
        eye_features: Sequence[float],
        sensitivity: float = 1.0,
        smoothing: float = 0.5,
    ) -> GazeSample:
        if self._coefficients is None:
            raise RuntimeError("Gaze must be calibrated before estimating screen coordinates")
        if not 0 <= smoothing < 1:
            raise ValueError("Smoothing must be at least 0 and less than 1")
        values = np.asarray(eye_features, dtype=np.float64)
        if values.shape != (4,) or not np.isfinite(values).all():
            raise ValueError("Eye feature vector is invalid")
        design = np.concatenate(([1.0], values))
        predicted = design @ self._coefficients
        predicted = 0.5 + (predicted - 0.5) * sensitivity
        predicted = np.clip(predicted, 0.0, 1.0)
        if self._previous is None:
            self._previous = predicted
        else:
            alpha = 1.0 - smoothing
            self._previous = alpha * predicted + (1.0 - alpha) * self._previous
        return GazeSample(float(self._previous[0]), float(self._previous[1]))
