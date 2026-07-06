import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, LogIn, AlertCircle, Eye, EyeOff, Brain } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">

      <div className="page-bg">
        <div className="orb orb--primary" />
        <div className="orb orb--cyan" />
      </div>

      <div className="card card--glass card--centered">

        <div className="card__header">
          <div className="icon-box icon-box--md icon-box--primary">
            <Brain size={24} />
          </div>
          <h1 className="card__title">Iniciar Sesión</h1>
          <p className="card__subtitle">
            Bienvenido de nuevo, continúa con tu progreso
          </p>
        </div>

        {error && (
          <div className="error-message">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form className="card__form" onSubmit={handleSubmit}>

          <div className="form-input">
            <label htmlFor="login-email">Correo electrónico</label>
            <div className="form-input__wrapper">
              <Mail size={18} className="form-input__icon" />
              <input
                id="login-email"
                type="email"
                placeholder="tu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="form-input">
            <label htmlFor="login-password">Contraseña</label>
            <div className="form-input__wrapper">
              <Lock size={18} className="form-input__icon" />
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Tu contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="form-input__toggle"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn-primary btn-primary--block"
            disabled={loading}
          >
            {loading ? (
              <div className="spinner" />
            ) : (
              <>
                <LogIn size={18} />
                <span>Iniciar Sesión</span>
              </>
            )}
          </button>
        </form>

        <div className="card__footer">
          <p>
            ¿No tienes cuenta?{' '}
            <Link to="/register">Regístrate aquí</Link>
          </p>
        </div>

      </div>
    </div>
  );
}