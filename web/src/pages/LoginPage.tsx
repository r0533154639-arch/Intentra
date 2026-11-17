import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/auth';
import { useAuth } from '../features/account/AuthContext';

export default function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const payload = await loginUser({ username, password });
      signIn(payload.access_token);
      navigate('/');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Login failed');
    }
  }

  return (
    <section className="auth-layout">
      <div className="auth-card">
        <div className="page-heading">
          <span className="eyebrow">Welcome back</span>
          <h1>Login</h1>
          <p>Sign in to manage your Intentra settings and devices.</p>
        </div>
        <form className="form-stack" onSubmit={onSubmit}>
          <label className="form-field">
            <span>Username</span>
            <input
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your username"
            />
          </label>
          <label className="form-field">
            <span>Password</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
            />
          </label>
          <button className="button button-primary button-wide" type="submit">Login</button>
          {message && <p className="notice notice-error" role="alert">{message}</p>}
        </form>
      </div>
    </section>
  );
}
