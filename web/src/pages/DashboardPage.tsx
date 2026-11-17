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
    return (
      <section className="page-section">
        <div className="page-heading">
          <span className="eyebrow">Your workspace</span>
          <h1>Dashboard</h1>
          <p>Log in to view your account and associated computers.</p>
        </div>
      </section>
    );
  }
  if (error) {
    return <section className="page-section"><div className="page-heading"><h1>Dashboard</h1></div><p className="notice notice-error" role="alert">{error}</p></section>;
  }
  if (!dashboard) {
    return <section className="page-section"><div className="page-heading"><h1>Dashboard</h1></div><p className="notice notice-info" role="status">Loading account...</p></section>;
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <span className="eyebrow">Your workspace</span>
        <h1>Dashboard</h1>
        <p>A quick overview of your Intentra account.</p>
      </div>
      <div className="dashboard-grid">
        <article className="summary-card">
          <span className="summary-label">Account</span>
          <strong className="summary-value">{dashboard.username}</strong>
          <span className="summary-detail">Signed-in user</span>
        </article>
        <article className="summary-card">
          <span className="summary-label">Connected computers</span>
          <strong className="summary-value">{dashboard.devices.length}</strong>
          <span className="summary-detail">Associated with your account</span>
        </article>
        <article className="summary-card summary-card-wide">
          <span className="summary-label">Settings synchronization</span>
          <strong className="summary-value summary-value-small">
            {dashboard.lastSync ? new Date(dashboard.lastSync).toLocaleString() : 'Not yet synchronized'}
          </strong>
          <span className="summary-detail">Most recent account settings update</span>
        </article>
      </div>
    </section>
  );
}
