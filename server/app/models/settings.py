from pydantic import BaseModel, Field


class GazeSettings(BaseModel):
    smoothing: float = 0.5
    sensitivity: float = 1.0


class GestureSettings(BaseModel):
    pinch_threshold: float = 0.0
    short_pinch_max_duration_ms: int = 0
    double_click_interval_ms: int = 0
    right_click_hold_ms: int = 0
    movement_threshold: float = 0.0
    jitter_threshold: float = 0.0


class ScrollSettings(BaseModel):
    precise_sensitivity: float = 1.0
    movement_smoothing: float = 0.0
    max_scroll_speed: float = 0.0
    fast_scroll_threshold: float = 0.0
    fast_scroll_acceleration_threshold: float = 0.0
    fast_scroll_duration_ms: int = 0
    fast_scroll_intensity: float = 1.0


class UserSettings(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    gaze: GazeSettings = Field(default_factory=GazeSettings)
    gestures: GestureSettings = Field(default_factory=GestureSettings)
    scroll: ScrollSettings = Field(default_factory=ScrollSettings)
    updated_at: str
    version: int = 1

    class Config:
        populate_by_name = True
