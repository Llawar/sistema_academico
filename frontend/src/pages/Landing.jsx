import { Link } from 'react-router-dom';
import {
  Brain, BarChart3, Lightbulb, ArrowRight, Sparkles,
  TrendingUp, Shield, Zap
} from 'lucide-react';

import '../styles/Landing.css'; // importar el CSS específico para Landing

const features = [
  {
    icon: BarChart3,
    title: 'Análisis de Hábitos',
    description: 'Registra y analiza tus patrones de estudio, descansos y distracciones en tiempo real.',
    color: 'cyan',
    stat: '98%',
    statLabel: 'precisión'
  },
  {
    icon: Brain,
    title: 'Predicciones con IA',
    description: 'Machine Learning avanzado para predecir tu rendimiento académico antes de los exámenes.',
    color: 'purple',
    stat: '+40%',
    statLabel: 'mejora promedio'
  },
  {
    icon: Lightbulb,
    title: 'Recomendaciones',
    description: 'Sugerencias personalizadas y adaptadas a tu situación académica única.',
    color: 'blue',
    stat: '24/7',
    statLabel: 'disponible'
  }
];

const stats = [
  { value: '95%', label: 'Precisión del modelo' },
  { value: '2K+', label: 'Estudiantes activos' },
  { value: '4.9', label: 'Calificación promedio' },
  { value: '30%', label: 'Mejora en notas' },
];

export default function Landing() {
  return (
    <div className="landing">

      <div className="page-bg">
        <div className="orb orb--primary" />
        <div className="orb orb--cyan" />
        <div className="bg-grid" />
      </div>

      {/* HERO */}
      <section className="hero">
        <div className="badge-pill" style={{ animationDelay: '0s', animation: 'fadeInDown 0.6s ease both' }}>
          <Sparkles size={14} style={{ color: 'var(--color-cyan)' }} />
          <span>Inteligencia Artificial aplicada a la educación</span>
        </div>

        <h1 className="hero__title">
          Predice tu
          <span className="text-gradient"> rendimiento </span>
          académico
        </h1>

        <p className="hero__subtitle">
          Analiza tus hábitos de estudio, anticipa tus resultados y
          recibe recomendaciones personalizadas con el poder de la IA.
        </p>

        <div className="btn-group" style={{ marginBottom: '60px', animation: 'fadeInDown 0.6s ease 0.3s both' }}>
          <Link to="/register" className="btn-primary">
            <Zap size={18} />
            Comenzar ahora
            <ArrowRight size={18} />
          </Link>
          <Link to="/login" className="btn-ghost">
            Ya tengo cuenta
          </Link>
        </div>

        <div className="stats-bar" style={{ animation: 'fadeInUp 0.6s ease 0.4s both' }}>
          {stats.map((stat, i) => (
            <div key={i} className="stat-item">
              <span className="stat-item__value text-gradient">{stat.value}</span>
              <span className="stat-item__label">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section className="features-section">
        <div className="section-header">
          <p className="section-header__tag">
            <TrendingUp size={14} />
            ¿Cómo funciona?
          </p>
          <h2 className="section-header__title">
            Todo lo que necesitas para <br />
            <span className="text-gradient">mejorar tu rendimiento</span>
          </h2>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className={`card feature-card feature-card--${feature.color}`}
              >
                <span className="feature-card__step">0{index + 1}</span>
                <div className={`icon-box icon-box--lg icon-box--${feature.color}`}>
                  <Icon size={24} />
                </div>
                <h3 className="feature-card__title">{feature.title}</h3>
                <p className="feature-card__desc">{feature.description}</p>
                <div className="feature-card__stat">
                  <span className="feature-card__stat-value text-gradient">
                    {feature.stat}
                  </span>
                  <span className="feature-card__stat-label">{feature.statLabel}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="card cta-card">
          <div className="cta-card__glow" />
          <Shield size={32} className="cta-card__icon" />
          <h2 className="cta-card__title">
            ¿Listo para mejorar tu rendimiento?
          </h2>
          <p className="cta-card__subtitle">
            Únete a miles de estudiantes que ya usan IA para alcanzar sus metas académicas.
          </p>
          <Link to="/register" className="btn-primary">
            <Sparkles size={18} />
            Crear cuenta gratuita
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="landing-footer__logo">
          <Brain size={16} />
          <span>AcadémicAI</span>
        </div>
        <p className="landing-footer__text">
          © 2026 · Sistema de Predicción Académica con IA
        </p>
      </footer>

    </div>
  );
}