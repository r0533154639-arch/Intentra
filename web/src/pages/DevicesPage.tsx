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
    <section className="page-section">
      <div className="page-heading">
        <span className="eyebrow">Your setup</span>
        <h1>Devices</h1>
        <p>Manage the desktop installations associated with your account.</p>
      </div>
      {!token && <p className="notice notice-info">Log in to view your associated desktop installations.</p>}
      {token && (
        <form className="pairing-panel" onSubmit={onPairDevice}>
          <div>
            <h2>Associate a desktop</h2>
            <p>Enter the pairing code shown in your Intentra desktop app.</p>
          </div>
          <label className="form-field pairing-field">
            <span>Pairing code</span>
            <input
              value={pairingCode}
              onChange={(event) => setPairingCode(event.target.value.toUpperCase())}
              placeholder="Enter pairing code"
              minLength={10}
              maxLength={16}
              autoComplete="off"
              required
            />
          </label>
          <button className="button button-primary pairing-button" type="submit" disabled={loading}>Associate desktop</button>
        </form>
      )}
      {loading && <p className="notice notice-info" role="status">Loading devices...</p>}
      {error && <p className="notice notice-error" role="alert">{error}</p>}
      {token && !loading && !error && devices.length === 0 && (
        <div className="empty-state">
          <span className="empty-state-icon" aria-hidden="true">↗</span>
          <h2>No devices yet</h2>
          <p>Pair a desktop installation to see it listed here.</p>
        </div>
      )}
      {devices.length > 0 && (
        <ul className="device-list">
          {devices.map((device) => (
            <li className="device-card" key={device.installation_id}>
              <div className="device-card-heading">
                <span className="device-icon" aria-hidden="true">PC</span>
                <div>
                  <h2>{device.device_name}</h2>
                  <p>Intentra {device.desktop_version}</p>
                </div>
              </div>
              <dl className="device-details">
                <div><dt>Last seen</dt><dd>{new Date(device.last_seen).toLocaleString()}</dd></div>
                <div><dt>OS user identifier</dt><dd>{device.os_user_identifier}</dd></div>
              </dl>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
