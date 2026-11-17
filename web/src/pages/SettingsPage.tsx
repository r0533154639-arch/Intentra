import { FormEvent, useEffect, useState } from 'react';

import { fetchSettings, saveSettings } from '../api/settings';
import { useAuth } from '../features/account/AuthContext';
import type { UserSettings } from '../types';

const initialSettings: UserSettings = {
  gaze: { smoothing: 0.5, sensitivity: 1, calibration_data: {} },
  gestures: {
    pinch_threshold: 0,
    short_pinch_max_duration_ms: 0,
    double_click_interval_ms: 0,
    right_click_hold_ms: 0,
    movement_threshold: 0,
    jitter_threshold: 0,
  },
  scroll: {
    precise_sensitivity: 1,
    movement_smoothing: 0,
    max_scroll_speed: 0,
    fast_scroll_threshold: 0,
    fast_scroll_acceleration_threshold: 0,
    fast_scroll_duration_ms: 0,
    fast_scroll_intensity: 1,
  },
};

export default function SettingsPage() {
  const { token } = useAuth();
  const [settings, setSettings] = useState<UserSettings>(initialSettings);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    if (!token) {
      setSettings(initialSettings);
      return () => {
        active = false;
      };
    }

    setLoading(true);
    fetchSettings(token)
      .then((value) => {
        if (active) {
          setSettings(value);
          setMessage('');
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setMessage(error instanceof Error ? error.message : 'Settings could not be loaded');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setMessage('Log in to save settings.');
      return;
    }
    setLoading(true);
    setMessage('');
    saveSettings(token, {
      gaze: settings.gaze,
      gestures: settings.gestures,
      scroll: settings.scroll,
    })
      .then((saved) => {
        setSettings(saved);
        setMessage('Settings saved.');
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : 'Settings could not be saved');
      })
      .finally(() => setLoading(false));
  }

  return (
    <form className="settings-form" onSubmit={onSubmit}>
      <div className="page-heading">
        <span className="eyebrow">Personalize your experience</span>
        <h1>Settings</h1>
        <p>Fine-tune gaze tracking, gestures, and scrolling to suit your setup.</p>
      </div>
      {!token && <p className="notice notice-info">Log in to load and save your settings.</p>}
      {loading && <p className="notice notice-info" role="status">Loading or saving settings...</p>}
      <fieldset className="settings-section">
        <legend>Gaze tracking</legend>
        <label>
          <span>Cursor smoothing</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.gaze.smoothing}
            onChange={(event) => setSettings({ ...settings, gaze: { ...settings.gaze, smoothing: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Cursor sensitivity</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.gaze.sensitivity}
            onChange={(event) => setSettings({ ...settings, gaze: { ...settings.gaze, sensitivity: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <fieldset className="settings-section">
        <legend>Gestures</legend>
        <label>
          <span>Pinch threshold</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.gestures.pinch_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, pinch_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Short-pinch maximum (ms)</span>
          <input
            className="settings-input"
            type="number"
            value={settings.gestures.short_pinch_max_duration_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, short_pinch_max_duration_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Double-click interval (ms)</span>
          <input
            className="settings-input"
            type="number"
            value={settings.gestures.double_click_interval_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, double_click_interval_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Right-click hold (ms)</span>
          <input
            className="settings-input"
            type="number"
            value={settings.gestures.right_click_hold_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, right_click_hold_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Movement threshold</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.gestures.movement_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, movement_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Jitter threshold</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.gestures.jitter_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, jitter_threshold: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <fieldset className="settings-section">
        <legend>Scrolling</legend>
        <label>
          <span>Precise-scroll sensitivity</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.precise_sensitivity}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, precise_sensitivity: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Movement smoothing</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.movement_smoothing}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, movement_smoothing: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Maximum scroll speed</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.max_scroll_speed}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, max_scroll_speed: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Fast-scroll threshold</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_threshold}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Fast-scroll acceleration threshold</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_acceleration_threshold}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_acceleration_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Fast-scroll duration (ms)</span>
          <input
            className="settings-input"
            type="number"
            value={settings.scroll.fast_scroll_duration_ms}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_duration_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          <span>Fast-scroll intensity</span>
          <input
            className="settings-input"
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_intensity}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_intensity: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <div className="settings-actions">
        <button className="button button-primary" type="submit" disabled={!token || loading}>Save settings</button>
        {message && <p className={`notice ${message === 'Settings saved.' ? 'notice-success' : 'notice-error'}`} role="status">{message}</p>}
      </div>
    </form>
  );
}
