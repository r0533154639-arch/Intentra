import numpy as np
import pytest

from vision.calibration import CalibrationSession
from vision.gaze_estimator import GazeEstimator


def make_calibration_samples():
    samples = []
    for x in (0.1, 0.5, 0.9):
        for y in (0.1, 0.5, 0.9):
            features = np.array([x, y, x * 0.8 + 0.1, y * 0.8 + 0.1])
            samples.append((features, (x, y)))
    return samples


def test_gaze_estimator_fits_and_persists_calibration():
    samples = make_calibration_samples()

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


def test_gaze_estimator_reduces_isolated_prediction_spikes():
    samples = make_calibration_samples()
    estimator = GazeEstimator()
    estimator.calibrate(samples)
    center_features = samples[4][0]

    baseline = estimator.estimate(center_features, timestamp_ms=0)
    estimator.estimate(center_features + 2.0, timestamp_ms=33)
    after_spike = estimator.estimate(center_features, timestamp_ms=66)

    assert abs(after_spike.x - baseline.x) < 0.01
    assert abs(after_spike.y - baseline.y) < 0.01


def test_gaze_estimator_reduces_jitter_during_fixed_gaze():
    samples = make_calibration_samples()
    estimator = GazeEstimator()
    calibration = estimator.calibrate(samples)
    coefficients = np.asarray(calibration["coefficients"])
    center_features = samples[4][0]
    feature_noise = np.array([0.02, -0.02, 0.01, -0.01])
    raw_positions = []
    filtered_positions = []

    for frame in range(30):
        direction = 1 if frame % 2 else -1
        features = center_features + direction * feature_noise
        raw_positions.append(np.concatenate(([1.0], features)) @ coefficients)
        gaze = estimator.estimate(features, timestamp_ms=frame * 33)
        filtered_positions.append((gaze.x, gaze.y))

    raw_jitter = np.ptp(np.asarray(raw_positions[10:]), axis=0)
    filtered_jitter = np.ptp(np.asarray(filtered_positions[10:]), axis=0)
    assert np.all(filtered_jitter < raw_jitter * 0.5)


def test_gaze_estimator_tracks_a_new_target_without_long_filter_lag():
    samples = make_calibration_samples()
    estimator = GazeEstimator()
    estimator.calibrate(samples)
    estimator.estimate(samples[4][0], timestamp_ms=0)

    gaze = None
    for frame in range(1, 13):
        gaze = estimator.estimate(samples[-1][0], timestamp_ms=frame * 33)

    assert gaze is not None
    assert abs(gaze.x - 0.9) < 0.08
    assert abs(gaze.y - 0.9) < 0.08


def test_gaze_estimator_downweights_an_inconsistent_calibration_point():
    samples = make_calibration_samples()
    features, _ = samples[4]
    samples[4] = (features, (0.95, 0.05))

    estimator = GazeEstimator()
    estimator.calibrate(samples)
    gaze = estimator.estimate(samples[3][0], smoothing=0.0)

    assert abs(gaze.x - 0.5) < 0.08
    assert abs(gaze.y - 0.1) < 0.08


def test_calibration_session_requires_all_nine_targets():
    session = CalibrationSession()
    features = [np.full(4, 0.4) for _ in range(15)]
    for _ in range(9):
        session.capture(features)
    assert session.complete
    assert len(session.samples) == 9


def test_calibration_uses_median_to_ignore_an_isolated_bad_frame():
    session = CalibrationSession()
    features = [np.full(4, 0.4) for _ in range(15)]
    features[0] = np.full(4, 0.9)

    session.capture(features)

    assert np.allclose(session.samples[0][0], np.full(4, 0.4))


def test_calibration_rejects_an_unstable_gaze_window():
    session = CalibrationSession()
    features = [np.full(4, 0.2 if index % 2 else 0.8) for index in range(15)]

    with pytest.raises(ValueError, match="Gaze was unstable"):
        session.capture(features)

    assert session.current_index == 0
