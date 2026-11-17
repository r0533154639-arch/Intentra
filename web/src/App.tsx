import { Link, Route, Routes } from 'react-router-dom';
import { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import DevicesPage from './pages/DevicesPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SettingsPage from './pages/SettingsPage';
import { AuthProvider, useAuth } from './features/account/AuthContext';

export default function App() {
  return (
    <AuthProvider>
      <ApplicationRoutes />
    </AuthProvider>
  );
}

function ApplicationRoutes() {
  const { token, signOut } = useAuth();
  const [logoutError, setLogoutError] = useState('');

  async function handleSignOut() {
    setLogoutError('');
    try {
      await signOut();
    } catch (error) {
      setLogoutError(error instanceof Error ? error.message : 'Log out failed');
    }
  }

  return (
    <div>
      <nav style={{ display: 'flex', gap: '1rem', padding: '1rem', background: '#111827', color: 'white' }}>
        <Link to="/">Dashboard</Link>
        <Link to="/settings">Settings</Link>
        <Link to="/devices">Devices</Link>
        {token ? (
          <button type="button" onClick={() => void handleSignOut()}>Log out / switch user</button>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </nav>
      {logoutError && <p role="alert">{logoutError}</p>}

      <main style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/devices" element={<DevicesPage />} />
        </Routes>
      </main>
    </div>
  );
}
