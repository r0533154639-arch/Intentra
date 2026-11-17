const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { headers, ...requestOptions } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    let message = body || `Request failed with status ${response.status}`;
    if (body) {
      try {
        const parsed: unknown = JSON.parse(body);
        if (
          parsed &&
          typeof parsed === 'object' &&
          'detail' in parsed &&
          typeof parsed.detail === 'string'
        ) {
          message = parsed.detail;
        }
      } catch {
        message = body;
      }
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}
