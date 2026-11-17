from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import pi
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class GazeSample:
    x: float
    y: float


class GazeEstimator:
    def __init__(self):
        self._coefficients: np.ndarray | None = None
        self._prediction_history: deque[np.ndarray] = deque(maxlen=3)
        self._previous_raw: np.ndarray | None = None
        self._filtered_position: np.ndarray | None = None
        self._filtered_velocity: np.ndarray | None = None
        self._last_timestamp_ms: int | None = None
        self.sample_count = 0
        self._quality: dict = {}

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

        feature_mean = features.mean(axis=0)
        feature_scale = features.std(axis=0)
        feature_scale[feature_scale < 1e-6] = 1.0
        normalized_features = (features - feature_mean) / feature_scale
        design = np.column_stack((np.ones(len(features)), normalized_features))
        rank = np.linalg.matrix_rank(design)
        if rank < 3:
            raise ValueError("Gaze calibration points do not provide enough independent variation")

        penalty = np.eye(design.shape[1], dtype=np.float64) * 1e-4
        penalty[0, 0] = 0.0
        weights = np.ones(len(features), dtype=np.float64)
        normalized_coefficients = np.zeros((design.shape[1], 2), dtype=np.float64)
        for _ in range(6):
            root_weights = np.sqrt(weights)
            weighted_design = design * root_weights[:, None]
            weighted_targets = targets * root_weights[:, None]
            normal_matrix = weighted_design.T @ weighted_design + penalty
            normalized_coefficients = np.linalg.solve(
                normal_matrix,
                weighted_design.T @ weighted_targets,
            )
            residuals = np.linalg.norm(targets - design @ normalized_coefficients, axis=1)
            residual_median = np.median(residuals)
            residual_mad = np.median(np.abs(residuals - residual_median))
            cutoff = max(residual_median + 2.5 * 1.4826 * residual_mad, 0.02)
            updated_weights = np.minimum(1.0, cutoff / np.maximum(residuals, 1e-9))
            if np.max(np.abs(updated_weights - weights)) < 1e-3:
                break
            weights = updated_weights

        feature_coefficients = normalized_coefficients[1:] / feature_scale[:, None]
        intercept = normalized_coefficients[0] - feature_mean @ feature_coefficients
        self._coefficients = np.vstack((intercept, feature_coefficients))
        self._reset_filter()
        self.sample_count = len(observations)
        residuals = np.linalg.norm(targets - np.column_stack((np.ones(len(features)), features)) @ np.vstack((intercept, feature_coefficients)), axis=1)
        self._quality = {
            "mean_error": float(np.mean(residuals)),
            "max_error": float(np.max(residuals)),
        }
        return self.to_dict()

    def _reset_filter(self) -> None:
        self._prediction_history.clear()
        self._previous_raw = None
        self._filtered_position = None
        self._filtered_velocity = None
        self._last_timestamp_ms = None

    def load(self, calibration_data: dict | None) -> bool:
        if not calibration_data:
            self._coefficients = None
            self._reset_filter()
            self.sample_count = 0
            return False
        coefficients = calibration_data.get("coefficients")
        if not isinstance(coefficients, list):
            self._coefficients = None
            self._reset_filter()
            self.sample_count = 0
            raise ValueError("Stored gaze calibration is missing its coefficients")
        array = np.asarray(coefficients, dtype=np.float64)
        if array.shape != (5, 2) or not np.isfinite(array).all():
            raise ValueError("Stored gaze calibration coefficients are invalid")
        self._coefficients = array
        self.sample_count = int(calibration_data.get("sample_count", 0))
        quality = calibration_data.get("quality")
        self._quality = quality if isinstance(quality, dict) else {}
        self._reset_filter()
        return True

    def to_dict(self) -> dict:
        if self._coefficients is None:
            return {}
        return {
            "coefficients": self._coefficients.tolist(),
            "sample_count": self.sample_count,
            "quality": dict(self._quality),
        }

    def estimate(
        self,
        eye_features: Sequence[float],
        sensitivity: float = 1.0,
        smoothing: float = 0.5,
        timestamp_ms: int | None = None,
    ) -> GazeSample:
        if self._coefficients is None:
            raise RuntimeError("Gaze must be calibrated before estimating screen coordinates")
        if not 0 <= smoothing < 1:
            raise ValueError("Smoothing must be at least 0 and less than 1")
        if not np.isfinite(sensitivity) or sensitivity <= 0:
            raise ValueError("Sensitivity must be a finite number greater than zero")
        values = np.asarray(eye_features, dtype=np.float64)
        if values.shape != (4,) or not np.isfinite(values).all():
            raise ValueError("Eye feature vector is invalid")
        design = np.concatenate(([1.0], values))
        predicted = design @ self._coefficients
        predicted = 0.5 + (predicted - 0.5) * sensitivity
        predicted = np.clip(predicted, 0.0, 1.0)

        if timestamp_ms is None:
            elapsed_seconds = 1.0 / 30.0
        else:
            if self._last_timestamp_ms is None:
                elapsed_seconds = 1.0 / 30.0
            else:
                elapsed_ms = timestamp_ms - self._last_timestamp_ms
                if elapsed_ms < 0:
                    raise ValueError("Gaze timestamps must be monotonic")
                if elapsed_ms > 250:
                    self._reset_filter()
                    elapsed_seconds = 1.0 / 30.0
                else:
                    elapsed_seconds = max(elapsed_ms / 1000.0, 1.0 / 120.0)
            self._last_timestamp_ms = timestamp_ms

        self._prediction_history.append(predicted)
        if len(self._prediction_history) < 3:
            robust_prediction = self._prediction_history[0]
        else:
            robust_prediction = np.median(np.stack(self._prediction_history), axis=0)
        if self._filtered_position is None:
            self._previous_raw = robust_prediction.copy()
            self._filtered_position = robust_prediction.copy()
            self._filtered_velocity = np.zeros(2, dtype=np.float64)
        else:
            assert self._previous_raw is not None
            assert self._filtered_velocity is not None
            raw_velocity = (robust_prediction - self._previous_raw) / elapsed_seconds
            derivative_alpha = self._filter_alpha(1.0, elapsed_seconds)
            self._filtered_velocity = (
                derivative_alpha * raw_velocity
                + (1.0 - derivative_alpha) * self._filtered_velocity
            )
            minimum_cutoff = 0.5 + 0.6 * (1.0 - smoothing)
            cutoff = minimum_cutoff + 0.02 * np.abs(self._filtered_velocity)
            alpha = self._filter_alpha(cutoff, elapsed_seconds)
            filtered = (
                alpha * robust_prediction
                + (1.0 - alpha) * self._filtered_position
            )
            movement = filtered - self._filtered_position
            self._filtered_position = np.where(
                np.abs(movement) < 0.001,
                self._filtered_position,
                filtered,
            )
            self._previous_raw = robust_prediction.copy()

        return GazeSample(
            float(self._filtered_position[0]),
            float(self._filtered_position[1]),
        )

    @staticmethod
    def _filter_alpha(cutoff: float | np.ndarray, elapsed_seconds: float) -> float | np.ndarray:
        tau = 1.0 / (2.0 * pi * cutoff)
        return 1.0 / (1.0 + tau / elapsed_seconds)
