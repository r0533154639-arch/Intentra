import { FormEvent, useState } from 'react';
import { registerUser } from '../api/auth';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await registerUser({ username, email, password });
      setMessage('Registration successful');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Registration failed');
    }
  }

  return (
    <section className="auth-layout">
      <div className="auth-card">
        <div className="page-heading">
          <span className="eyebrow">Get started</span>
          <h1>Create your account</h1>
          <p>Set up an account to sync your preferences across your devices.</p>
        </div>
        <form className="form-stack" onSubmit={onSubmit}>
          <label className="form-field">
            <span>Username</span>
            <input
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
            />
          </label>
          <label className="form-field">
            <span>Email</span>
            <input
              inputMode="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </label>
          <label className="form-field">
            <span>Password</span>
            <input
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a password"
            />
          </label>
          <button className="button button-primary button-wide" type="submit">Create account</button>
          {message && <p className="notice notice-info" role="status">{message}</p>}
        </form>
      </div>
    </section>
  );
}
