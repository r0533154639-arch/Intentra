import { useEffect, useState } from 'react';

import { fetchCurrentUser } from '../api/auth';
import { fetchDevices, fetchSettings } from '../api/settings';
import { useAuth } from '../features/account/AuthContext';
import type { Device } from '../types';

interface DashboardState {
  username: string;
  devices: Device[];
  lastSync: string | null;
}

export default function DashboardPage() {
  const { token } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardState | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setDashboard(null);
    setError('');
    if (!token) {
      return () => {
        active = false;
      };
    }

    Promise.all([fetchCurrentUser(token), fetchDevices(token), fetchSettings(token)])
      .then(([user, devices, settings]) => {
        if (active) {
          setDashboard({ username: user.username, devices, lastSync: settings.updated_at ?? null });
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : 'Dashboard could not be loaded');
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  if (!token) {
    return <section><h1>Dashboard</h1><p>Log in to view your account and associated computers.</p></section>;
  }
  if (error) {
    return <section><h1>Dashboard</h1><p role="alert">{error}</p></section>;
  }
  if (!dashboard) {
    return <section><h1>Dashboard</h1><p role="status">Loading account...</p></section>;
  }

  return (
    <section>
      <h1>Dashboard</h1>
      <p>Account: {dashboard.username}</p>
      <p>Associated computers: {dashboard.devices.length}</p>
      <p>Last settings synchronization: {dashboard.lastSync ? new Date(dashboard.lastSync).toLocaleString() : 'Not yet synchronized'}</p>
    </section>
  );
}
