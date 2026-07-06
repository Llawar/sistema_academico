import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  User, Mail, Lock, Eye, EyeOff,
  AlertCircle, UserPlus, Brain
} from 'lucide-react';

export default function Register() {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    password: '',
    objetivo_promedio: 7.0,
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);

    try {
      await register(formData);
      await login(formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrarse');
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
          <h1 className="card__title">Crear Cuenta</h1>
          <p className="card__subtitle">
            Comienza a mejorar tu rendimiento académico
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
            <label htmlFor="reg-nombre">Nombre completo</label>
            <div className="form-input__wrapper">
              <User size={18} className="form-input__icon" />
              <input
                id="reg-nombre"
                type="text"
                placeholder="Tu nombre"
                value={formData.nombre}
                onChange={(e) => handleChange('nombre', e.target.value)}
                autoComplete="name"
                required
              />
            </div>
          </div>

          <div className="form-input">
            <label htmlFor="reg-email">Correo electrónico</label>
            <div className="form-input__wrapper">
              <Mail size={18} className="form-input__icon" />
              <input
                id="reg-email"
                type="email"
                placeholder="tu@email.com"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="form-input">
            <label htmlFor="reg-password">Contraseña</label>
            <div className="form-input__wrapper">
              <Lock size={18} className="form-input__icon" />
              <input
                id="reg-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Mínimo 6 caracteres"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                autoComplete="new-password"
                minLength={6}
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

          <div className="form-input">
            <label htmlFor="reg-confirm">Confirmar contraseña</label>
            <div className="form-input__wrapper">
              <Lock size={18} className="form-input__icon" />
              <input
                id="reg-confirm"
                type={showPassword ? 'text' : 'password'}
                placeholder="Repite tu contraseña"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
                required
              />
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
                <UserPlus size={18} />
                <span>Crear Cuenta</span>
              </>
            )}
          </button>
        </form>

        <div className="card__footer">
          <p>
            ¿Ya tienes cuenta?{' '}
            <Link to="/login">Inicia sesión</Link>
          </p>
        </div>

      </div>
    </div>
  );
}