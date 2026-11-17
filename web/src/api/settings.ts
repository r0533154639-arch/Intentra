import { apiRequest } from './client';
import type { Device, UserSettings } from '../types';

export function fetchSettings(token: string) {
  return apiRequest<UserSettings>('/api/settings', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function saveSettings(token: string, payload: Pick<UserSettings, 'gaze' | 'gestures' | 'scroll'>) {
  return apiRequest<UserSettings>('/api/settings', {
    method: 'PUT',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function fetchDevices(token: string) {
  return apiRequest<Device[]>('/api/devices', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function pairDevice(token: string, pairingCode: string) {
  return apiRequest<Device>('/api/devices/pair', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ pairing_code: pairingCode }),
  });
}
