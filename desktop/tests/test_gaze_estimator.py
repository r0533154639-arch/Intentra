import numpy as np

from vision.calibration import CalibrationSession
from vision.gaze_estimator import GazeEstimator


def test_gaze_estimator_fits_and_persists_calibration():
    samples = []
    for x in (0.1, 0.5, 0.9):
        for y in (0.1, 0.5, 0.9):
            features = np.array([x, y, x * 0.8 + 0.1, y * 0.8 + 0.1])
            samples.append((features, (x, y)))

    estimator = GazeEstimator()
    calibration = estimator.calibrate(samples)
    sample = estimator.estimate(samples[4][0], sensitivity=1.0, smoothing=0.0)
    assert abs(sample.x - 0.5) < 0.01
    assert abs(sample.y - 0.5) < 0.01

    restored = GazeEstimator()
    assert restored.load(calibration)
    restored_sample = restored.estimate(samples[0][0], sensitivity=1.0, smoothing=0.0)
    assert abs(restored_sample.x - 0.1) < 0.01
    assert abs(restored_sample.y - 0.1) < 0.01


def test_calibration_session_requires_all_nine_targets():
    session = CalibrationSession()
    features = [np.array([index / 15, index / 30, index / 45, index / 60]) for index in range(15)]
    for _ in range(9):
        session.capture(features)
    assert session.complete
    assert len(session.samples) == 9
