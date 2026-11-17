import { apiRequest } from './client';

export function registerUser(payload: { username: string; email: string; password: string }) {
  return apiRequest<{ id: string; username: string; email: string }>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload: { username: string; password: string }) {
  return apiRequest<{ access_token: string; token_type: string }>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function logoutUser(token: string) {
  return apiRequest<{ ok: boolean }>('/api/auth/logout', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchCurrentUser(token: string) {
  return apiRequest<{ id: string; username: string; email: string }>('/api/users/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
}
