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
    <form onSubmit={onSubmit} style={{ display: 'grid', gap: '0.75rem', maxWidth: 560 }}>
      <h2>Settings</h2>
      {!token && <p>Log in to load and save your settings.</p>}
      {loading && <p role="status">Loading or saving settings...</p>}
      <fieldset>
        <legend>Gaze tracking</legend>
        <label>
          Cursor smoothing
          <input
            type="number"
            step="0.01"
            value={settings.gaze.smoothing}
            onChange={(event) => setSettings({ ...settings, gaze: { ...settings.gaze, smoothing: Number(event.target.value) } })}
          />
        </label>
        <label>
          Cursor sensitivity
          <input
            type="number"
            step="0.01"
            value={settings.gaze.sensitivity}
            onChange={(event) => setSettings({ ...settings, gaze: { ...settings.gaze, sensitivity: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <fieldset>
        <legend>Gestures</legend>
        <label>
          Pinch threshold
          <input
            type="number"
            step="0.01"
            value={settings.gestures.pinch_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, pinch_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          Short-pinch maximum (ms)
          <input
            type="number"
            value={settings.gestures.short_pinch_max_duration_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, short_pinch_max_duration_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          Double-click interval (ms)
          <input
            type="number"
            value={settings.gestures.double_click_interval_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, double_click_interval_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          Right-click hold (ms)
          <input
            type="number"
            value={settings.gestures.right_click_hold_ms}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, right_click_hold_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          Movement threshold
          <input
            type="number"
            step="0.01"
            value={settings.gestures.movement_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, movement_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          Jitter threshold
          <input
            type="number"
            step="0.01"
            value={settings.gestures.jitter_threshold}
            onChange={(event) => setSettings({ ...settings, gestures: { ...settings.gestures, jitter_threshold: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <fieldset>
        <legend>Scrolling</legend>
        <label>
          Precise-scroll sensitivity
          <input
            type="number"
            step="0.01"
            value={settings.scroll.precise_sensitivity}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, precise_sensitivity: Number(event.target.value) } })}
          />
        </label>
        <label>
          Movement smoothing
          <input
            type="number"
            step="0.01"
            value={settings.scroll.movement_smoothing}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, movement_smoothing: Number(event.target.value) } })}
          />
        </label>
        <label>
          Maximum scroll speed
          <input
            type="number"
            step="0.01"
            value={settings.scroll.max_scroll_speed}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, max_scroll_speed: Number(event.target.value) } })}
          />
        </label>
        <label>
          Fast-scroll threshold
          <input
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_threshold}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          Fast-scroll acceleration threshold
          <input
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_acceleration_threshold}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_acceleration_threshold: Number(event.target.value) } })}
          />
        </label>
        <label>
          Fast-scroll duration (ms)
          <input
            type="number"
            value={settings.scroll.fast_scroll_duration_ms}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_duration_ms: Number(event.target.value) } })}
          />
        </label>
        <label>
          Fast-scroll intensity
          <input
            type="number"
            step="0.01"
            value={settings.scroll.fast_scroll_intensity}
            onChange={(event) => setSettings({ ...settings, scroll: { ...settings.scroll, fast_scroll_intensity: Number(event.target.value) } })}
          />
        </label>
      </fieldset>
      <button type="submit" disabled={!token || loading}>Save settings</button>
      {message && <p role="status">{message}</p>}
    </form>
  );
}
