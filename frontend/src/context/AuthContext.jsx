import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authService.getMe()
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('usuario');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await authService.login({ email, password });
    localStorage.setItem('token', res.data.access_token);
    
    // El backend actual SÍ devuelve usuario en login, pero por robustez 
    // hacemos getMe() como fallback si no viniera
    let userData = res.data.usuario;
    if (!userData) {
      const meRes = await authService.getMe();
      userData = meRes.data;
    }
    
    localStorage.setItem('usuario', JSON.stringify(userData));
    setUser(userData);
    return res.data;
  };

  const register = async (data) => {
    const res = await authService.register(data);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    setUser(null);
  };

  const updateUser = async (data) => {
    const res = await authService.updateMe(data);
    setUser(res.data);
    localStorage.setItem('usuario', JSON.stringify(res.data));
    return res.data;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
