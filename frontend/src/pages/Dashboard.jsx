import { useState, useEffect } from 'react';
import { analisisService, materiasService, evaluacionesService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import '../styles/Dashboard.css'; // Asegúrate de importar el nuevo CSS

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [predicciones, setPredicciones] = useState([]);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const [statsRes, predRes, recRes] = await Promise.allSettled([
        analisisService.getEstadisticas(),
        analisisService.getPredicciones(),
        analisisService.getRecomendaciones(),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      else console.error('Error stats:', statsRes.reason);

      if (predRes.status === 'fulfilled') setPredicciones(predRes.value.data);
      else console.error('Error predicciones:', predRes.reason);

      if (recRes.status === 'fulfilled') setRecomendaciones(recRes.value.data);
      else console.error('Error recomendaciones:', recRes.reason);

      // Cargar materias y evaluaciones para el gráfico
      const [matRes, evalRes] = await Promise.all([
        materiasService.getAll(),
        evaluacionesService.getAll(),
      ]);
      setMaterias(matRes.data);
      setEvaluaciones(evalRes.data);
    } catch (err) {
      setError('Error al cargar el dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="page-center"><div className="loading"><div className="spinner"></div>Cargando dashboard...</div></div>;

  const chartData = predicciones?.materias?.map(m => ({
    name: m.materia_nombre,
    prediccion: m.prediccion_nota,
    tendencia: m.tendencia === 'positiva' ? 1 : m.tendencia === 'negativa' ? -1 : 0
  })) || [];

  return (
    /* 1. Añadimos 'page-container' para el centrado y max-width global */
    <div className="page-container dashboard">
      <h1 className="dashboard__title">Bienvenido, {user?.nombre}</h1>
      {error && <p className="error-message" style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
      
      <div className="stats-grid">
        {/* 2. Añadimos 'card' a todas las stat-card */}
        <div className="card stat-card">
          <h3>Materias</h3>
          <p className="stat-value">{stats?.total_materias || 0}</p>
        </div>
        <div className="card stat-card">
          <h3>Horas de Estudio</h3>
          <p className="stat-value">{(stats?.tiempo_estudio_total || 0).toFixed(1)}h</p>
        </div>
        <div className="card stat-card">
          <h3>Distracciones</h3>
          <p className="stat-value">{stats?.tiempo_distracciones || 0}min</p>
        </div>
        <div className="card stat-card">
          <h3>Nota Promedio</h3>
          <p className="stat-value text-gradient">{(stats?.nota_promedio || 0).toFixed(1)}</p>
        </div>
      </div>

      <div className="dashboard-section">
        <h2 className="section-title">Predicciones por Materia</h2>
        <div className="card"> {/* Envolvemos el gráfico en una card global */}
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis domain={[0, 10]} stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#f1f5f9' }} />
                <Bar dataKey="prediccion" fill="#6366f1" radius={[4, 4, 0, 0]} name="Predicción" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted">Registra materias y evaluaciones para ver predicciones</p>
          )}
        </div>
      </div>

      <div className="dashboard-section">
        <h2 className="section-title">Recomendaciones</h2>
        <div className="recomendaciones-grid">
          {recomendaciones.length > 0 ? (
            recomendaciones.map((rec, idx) => (
              /* 3. Añadimos 'card' a las rec-card */
              <div key={idx} className={`card rec-card rec-card--${rec.prioridad}`}>
                <h4>{rec.titulo}</h4>
                <p>{rec.descripcion}</p>
                {/* 4. Añadimos la clase global 'badge' para la etiqueta de prioridad */}
                <span className={`badge badge--${rec.prioridad}`}>{rec.prioridad}</span>
              </div>
            ))
          ) : (
            <div className="card text-center">
              <p className="text-muted">Completa tu perfil para recibir recomendaciones</p>
            </div>
          )}
        </div>
      </div>

      {predicciones?.alertas?.length > 0 && (
        <div className="dashboard-section">
          <h2 className="section-title">Alertas</h2>
          <div className="alerts-grid">
            {predicciones.alertas.map((alerta, idx) => (
              /* Ya usa 'alert alert-warning' de utilidades */
              <div key={idx} className="alert-warning">{alerta}</div> 
            ))}
          </div>
        </div>
      )}
    </div>
  );
}