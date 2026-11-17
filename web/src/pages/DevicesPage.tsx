import { FormEvent, useEffect, useState } from 'react';

import { fetchDevices, pairDevice } from '../api/settings';
import { useAuth } from '../features/account/AuthContext';
import type { Device } from '../types';

export default function DevicesPage() {
  const { token } = useAuth();
  const [devices, setDevices] = useState<Device[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [pairingCode, setPairingCode] = useState('');

  useEffect(() => {
    let active = true;
    setDevices([]);
    setError('');
    if (!token) {
      return () => {
        active = false;
      };
    }

    setLoading(true);
    fetchDevices(token)
      .then((result) => {
        if (active) {
          setDevices(result);
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : 'Devices could not be loaded');
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

  async function onPairDevice(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setError('Log in to associate a desktop installation.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await pairDevice(token, pairingCode);
      setPairingCode('');
      setDevices(await fetchDevices(token));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Device pairing failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>Computers / Devices</h1>
      {!token && <p>Log in to view your associated desktop installations.</p>}
      {token && (
        <form onSubmit={onPairDevice}>
          <label>
            Pair a desktop installation
            <input
              value={pairingCode}
              onChange={(event) => setPairingCode(event.target.value.toUpperCase())}
              minLength={10}
              maxLength={16}
              autoComplete="off"
              required
            />
          </label>
          <button type="submit" disabled={loading}>Associate desktop</button>
        </form>
      )}
      {loading && <p role="status">Loading devices...</p>}
      {error && <p role="alert">{error}</p>}
      {token && !loading && !error && devices.length === 0 && <p>No devices are associated yet.</p>}
      {devices.length > 0 && (
        <ul>
          {devices.map((device) => (
            <li key={device.installation_id}>
              <strong>{device.device_name}</strong> - Intentra {device.desktop_version}
              <div>Last seen: {new Date(device.last_seen).toLocaleString()}</div>
              <div>OS user identifier: {device.os_user_identifier}</div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
