export interface RegisterForm {
  username: string;
  email: string;
  password: string;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface UserSettings {
  gaze: {
    smoothing: number;
    sensitivity: number;
    calibration_data: Record<string, unknown>;
  };
  gestures: {
    pinch_threshold: number;
    short_pinch_max_duration_ms: number;
    double_click_interval_ms: number;
    right_click_hold_ms: number;
    movement_threshold: number;
    jitter_threshold: number;
  };
  scroll: {
    precise_sensitivity: number;
    movement_smoothing: number;
    max_scroll_speed: number;
    fast_scroll_threshold: number;
    fast_scroll_acceleration_threshold: number;
    fast_scroll_duration_ms: number;
    fast_scroll_intensity: number;
  };
  version?: number;
  updated_at?: string | null;
  user_id?: string;
}

export interface Device {
  _id: string;
  user_id: string;
  os_user_identifier: string;
  installation_id: string;
  device_name: string;
  desktop_version: string;
  last_seen: string;
  created_at: string;
}
