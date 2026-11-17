import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GazeSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    smoothing: float = Field(default=0.5, ge=0, lt=1)
    sensitivity: float = Field(default=1.0, gt=0, le=10)
    calibration_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("calibration_data")
    @classmethod
    def calibration_is_device_scoped(cls, value: dict[str, Any]) -> dict[str, Any]:
        if value:
            raise ValueError("Gaze calibration is stored per device, not in account settings")
        return value


class GestureSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    pinch_threshold: float = Field(default=0.0, ge=0, le=10)
    short_pinch_max_duration_ms: int = Field(default=0, ge=0, le=60000)
    double_click_interval_ms: int = Field(default=0, ge=0, le=60000)
    right_click_hold_ms: int = Field(default=0, ge=0, le=60000)
    movement_threshold: float = Field(default=0.0, ge=0, le=10)
    jitter_threshold: float = Field(default=0.0, ge=0, le=10)


class ScrollSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    precise_sensitivity: float = Field(default=1.0, ge=0, le=10000)
    movement_smoothing: float = Field(default=0.0, ge=0, lt=1)
    max_scroll_speed: float = Field(default=0.0, ge=0, le=1000)
    fast_scroll_threshold: float = Field(default=0.0, ge=0, le=1000)
    fast_scroll_acceleration_threshold: float = Field(default=0.0, ge=0, le=100000)
    fast_scroll_duration_ms: int = Field(default=0, ge=0, le=10000)
    fast_scroll_intensity: float = Field(default=1.0, ge=0, le=10000)


class SettingsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gaze: GazeSettings = Field(default_factory=GazeSettings)
    gestures: GestureSettings = Field(default_factory=GestureSettings)
    scroll: ScrollSettings = Field(default_factory=ScrollSettings)


def recommended_settings_payload() -> dict[str, Any]:
    return {
        "gaze": {
            "smoothing": 0.9,
            "sensitivity": 0.6,
            "calibration_data": {},
        },
        "gestures": {
            "pinch_threshold": 0.2,
            "short_pinch_max_duration_ms": 300,
            "double_click_interval_ms": 400,
            "right_click_hold_ms": 650,
            "movement_threshold": 0.1,
            "jitter_threshold": 0.002,
        },
        "scroll": {
            "precise_sensitivity": 100.0,
            "movement_smoothing": 0.4,
            "max_scroll_speed": 10.0,
            "fast_scroll_threshold": 1.5,
            "fast_scroll_acceleration_threshold": 10.0,
            "fast_scroll_duration_ms": 300,
            "fast_scroll_intensity": 2.0,
        },
    }


class DeviceRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    os_user_identifier: str = Field(min_length=1)
    installation_id: str = Field(min_length=1)
    device_name: str = Field(min_length=1)
    desktop_version: str


class DevicePairingStart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    os_user_identifier: str = Field(min_length=1)
    installation_id: str = Field(min_length=1)
    device_name: str = Field(min_length=1)
    desktop_version: str
    device_key: str = Field(pattern=r"^[a-f0-9]{64}$")


class DevicePairingApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pairing_code: str = Field(pattern=r"^[a-zA-Z0-9 -]{10,16}$")


class CalibrationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calibration_data: dict[str, Any]

    @field_validator("calibration_data")
    @classmethod
    def validate_calibration(cls, value: dict[str, Any]) -> dict[str, Any]:
        coefficients = value.get("coefficients")
        sample_count = value.get("sample_count")
        if (
            not isinstance(coefficients, list)
            or len(coefficients) != 5
            or any(not isinstance(row, list) or len(row) != 2 for row in coefficients)
            or not isinstance(sample_count, int)
            or sample_count < 5
        ):
            raise ValueError("Calibration must contain five coefficient rows and at least five samples")
        if any(
            not isinstance(number, (int, float)) or not math.isfinite(number)
            for row in coefficients
            for number in row
        ):
            raise ValueError("Calibration coefficients must be finite numbers")
        return value
