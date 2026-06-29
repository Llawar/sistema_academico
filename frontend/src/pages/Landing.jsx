import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-hero">
        <h1>🎓 Sistema de Predicción de Rendimiento Académico</h1>
        <p>Analiza tus hábitos de estudio, predice tus resultados y mejora tu rendimiento académico con IA</p>
        <div className="landing-buttons">
          <Link to="/login" className="btn-primary">Iniciar Sesión</Link>
          <Link to="/register" className="btn-secondary">Registrarse</Link>
        </div>
      </div>
      <div className="features">
        <div className="feature">
          <h3>📊 Análisis de Hábitos</h3>
          <p>Registra y analiza tus patrones de estudio, descansos y distracciones</p>
        </div>
        <div className="feature">
          <h3>🤖 Predicciones con IA</h3>
          <p>Machine learning para predecir tu rendimiento académico</p>
        </div>
        <div className="feature">
          <h3>💡 Recomendaciones Personalizadas</h3>
          <p>Recibe sugerencias adaptadas a tu situación académica</p>
        </div>
      </div>
    </div>
  );
}
