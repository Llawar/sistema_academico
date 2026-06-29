import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🎓 Académico</Link>
      </div>
      <div className="navbar-links">
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/materias">Materias</Link>
            <Link to="/evaluaciones">Evaluaciones</Link>
            <Link to="/registro">Registro</Link>
            <Link to="/habitos">Hábitos</Link>
            <Link to="/predicciones">Predicciones</Link>
            <span className="user-name">{user.nombre}</span>
            <button onClick={handleLogout} className="btn-logout">Cerrar Sesión</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Registrarse</Link>
          </>
        )}
      </div>
    </nav>
  );
}
