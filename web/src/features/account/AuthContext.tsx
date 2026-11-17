import { createContext, ReactNode, useContext, useMemo, useState } from 'react';
import { logoutUser } from '../../api/auth';

interface AuthContextValue {
  token: string | null;
  signIn: (accessToken: string) => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      signIn: setToken,
      signOut: async () => {
        try {
          if (token) {
            await logoutUser(token);
          }
        } finally {
          setToken(null);
        }
      },
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
