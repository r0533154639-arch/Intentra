from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CalibrationTarget:
    x: float
    y: float


class CalibrationSession:
    def __init__(self):
        self.targets = [
            CalibrationTarget(x, y)
            for y in (0.1, 0.5, 0.9)
            for x in (0.1, 0.5, 0.9)
        ]
        self.samples: list[tuple[np.ndarray, tuple[float, float]]] = []
        self.current_index = 0

    @property
    def complete(self) -> bool:
        return self.current_index >= len(self.targets)

    @property
    def current_target(self) -> CalibrationTarget:
        if self.complete:
            raise RuntimeError("Calibration session is complete")
        return self.targets[self.current_index]

    def capture(self, recent_features: list[np.ndarray]) -> None:
        if self.complete:
            raise RuntimeError("Calibration session is complete")
        if len(recent_features) < 15:
            raise ValueError("Keep your face visible and wait for more camera samples")
        target = self.current_target
        features = np.asarray(recent_features[-15:], dtype=np.float64)
        if features.shape != (15, 4) or not np.isfinite(features).all():
            raise ValueError("Camera did not provide valid eye-tracking samples")
        center = np.median(features, axis=0)
        variability = np.median(np.abs(features - center), axis=0)
        central_range = np.quantile(features, 0.9, axis=0) - np.quantile(features, 0.1, axis=0)
        if np.max(variability) > 0.05 or np.max(central_range) > 0.1:
            raise ValueError("Gaze was unstable. Keep looking at the target and capture it again.")
        self.samples.append((center, (target.x, target.y)))
        self.current_index += 1
