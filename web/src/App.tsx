import { Link, NavLink, Route, Routes } from 'react-router-dom';
import { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import DevicesPage from './pages/DevicesPage';
import GesturesPage from './pages/GesturesPage';
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
    <div className="app-shell">
      <header className="site-header">
        <nav className="site-nav" aria-label="Main navigation">
          <Link className="brand" to="/" aria-label="Intentra home">
            <span className="brand-mark" aria-hidden="true">I</span>
            <span>Intentra</span>
          </Link>
          <div className="nav-links">
            <NavLink className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`} end to="/">Dashboard</NavLink>
            <NavLink className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`} to="/gestures">Gestures</NavLink>
            <NavLink className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`} to="/settings">Settings</NavLink>
            <NavLink className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`} to="/devices">Devices</NavLink>
          </div>
          <div className="nav-account">
            {token ? (
              <button className="button button-quiet nav-action" type="button" onClick={() => void handleSignOut()}>
                Log out / switch user
              </button>
            ) : (
              <>
                <NavLink className="nav-link" to="/login">Login</NavLink>
                <NavLink className="button button-primary nav-register" to="/register">Create account</NavLink>
              </>
            )}
          </div>
        </nav>
      </header>

      <main className="main-content">
        <div className="content-container">
          {logoutError && <p className="notice notice-error" role="alert">{logoutError}</p>}
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/gestures" element={<GesturesPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/devices" element={<DevicesPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
