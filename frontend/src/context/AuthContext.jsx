import { createContext, useContext, useEffect, useState } from "react";
import * as api from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On page load: if we have a saved token, ask the backend who it belongs to.
  useEffect(() => {
    if (!api.getToken()) {
      setLoading(false);
      return;
    }
    api
      .getMe()
      .then(setUser)
      .catch(() => api.setToken(null))
      .finally(() => setLoading(false));
  }, []);

  const startSession = (data) => {
    api.setToken(data.token);
    setUser(data.user);
  };

  const login = async (email, password) => startSession(await api.login(email, password));
  const register = async (name, email, password) =>
    startSession(await api.register(name, email, password));

  const logout = async () => {
    try {
      await api.logout();
    } catch {
      /* even if the server call fails, log out locally */
    }
    api.setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
