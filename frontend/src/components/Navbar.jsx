import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Brain, LayoutDashboard, BookOpen, ClipboardCheck,
  PenLine, CalendarDays, Clock, Activity, TrendingUp, LogOut, User, Menu, X
} from 'lucide-react';
import { useState, useEffect } from 'react';

const navLinks = [
  { path: '/dashboard',    label: 'Dashboard',     icon: LayoutDashboard },
  { path: '/materias',     label: 'Materias',      icon: BookOpen },
  { path: '/evaluaciones', label: 'Evaluaciones',  icon: ClipboardCheck },
  { path: '/mi-dia',       label: 'Mi Día',        icon: PenLine },
  { path: '/actividad',    label: 'Actividad',     icon: CalendarDays },
  { path: '/predicciones', label: 'Predicciones',  icon: TrendingUp },
];

function renderNavLinks(links, currentPath) {
  return links.map((link) => {
    const Icon = link.icon;
    const isActive = currentPath === link.path;
    const cls = isActive
      ? 'navbar__link navbar__link--active'
      : 'navbar__link';

    return (
      <Link key={link.path} to={link.path} className={cls}>
        <Icon size={16} />
        <span>{link.label}</span>
        {isActive && <span className="navbar__link-indicator" />}
      </Link>
    );
  });
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>

      {/* LOGO */}
      <Link to="/" className="navbar__brand">
        <div className="icon-box icon-box--sm icon-box--primary">
          <Brain size={20} />
        </div>
        <span className="navbar__logo-text">AcadémicAI</span>
      </Link>

      {/* LINKS */}
      {user && (
        <div className={'navbar__links' + (mobileOpen ? ' navbar__links--open' : '')}>
          {renderNavLinks(navLinks, location.pathname)}
        </div>
      )}

      {/* ACTIONS */}
      <div className="navbar__actions">
        {user ? (
          <>
            <div className="navbar__user">
              <div className="avatar">
                <User size={14} />
              </div>
              <span className="navbar__username">{user.nombre}</span>
            </div>
            <button
              onClick={handleLogout}
              className="btn-ghost btn-ghost--sm btn-ghost--danger"
            >
              <LogOut size={16} />
              <span className="navbar__logout-text">Salir</span>
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="navbar__link">Iniciar Sesión</Link>
            <Link to="/register" className="btn-primary btn-primary--sm">
              Registrarse
            </Link>
          </>
        )}

        {user && (
          <button
            className="navbar__hamburger"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Menú"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        )}
      </div>

      {mobileOpen && (
        <div
          className="navbar__overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}
    </nav>
  );
}