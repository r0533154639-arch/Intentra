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
    <form onSubmit={onSubmit} style={{ maxWidth: 360 }}>
      <h2>Register</h2>
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        style={{ display: 'block', width: '100%', margin: '0.5rem 0', padding: '0.5rem' }}
      />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        style={{ display: 'block', width: '100%', margin: '0.5rem 0', padding: '0.5rem' }}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        style={{ display: 'block', width: '100%', margin: '0.5rem 0', padding: '0.5rem' }}
      />
      <button type="submit" style={{ padding: '0.5rem 1rem' }}>Register</button>
      {message && <p>{message}</p>}
    </form>
  );
}
