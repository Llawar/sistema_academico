import { useState, useEffect } from 'react';
import { analisisService, materiasService, evaluacionesService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [predicciones, setPredicciones] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, predRes, recRes] = await Promise.all([
        analisisService.getEstadisticas(),
        analisisService.getPredicciones(),
        analisisService.getRecomendaciones(),
      ]);
      setStats(statsRes.data);
      setPredicciones(predRes.data);
      setRecomendaciones(recRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando dashboard...</div>;

  const chartData = predicciones?.materias?.map(m => ({
    name: m.materia_nombre,
    prediccion: m.prediccion_nota,
    tendencia: m.tendencia === 'positiva' ? 1 : m.tendencia === 'negativa' ? -1 : 0
  })) || [];

  return (
    <div className="dashboard">
      <h1>Bienvenido, {user?.nombre}</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Materias</h3>
          <p className="stat-value">{stats?.total_materias || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Horas de Estudio</h3>
          <p className="stat-value">{(stats?.tiempo_estudio_total || 0).toFixed(1)}h</p>
        </div>
        <div className="stat-card">
          <h3>Distracciones</h3>
          <p className="stat-value">{stats?.tiempo_distracciones || 0}min</p>
        </div>
        <div className="stat-card">
          <h3>Nota Promedio</h3>
          <p className="stat-value">{(stats?.nota_promedio || 0).toFixed(1)}</p>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Predicciones por Materia</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Bar dataKey="prediccion" fill="#4F46E5" name="Predicción" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p>Registra materias y evaluaciones para ver predicciones</p>
        )}
      </div>

      <div className="dashboard-section">
        <h2>Recomendaciones</h2>
        <div className="recomendaciones-list">
          {recomendaciones.length > 0 ? (
            recomendaciones.map((rec, idx) => (
              <div key={idx} className={`rec-card rec-${rec.prioridad}`}>
                <h4>{rec.titulo}</h4>
                <p>{rec.descripcion}</p>
                <span className="rec-prioridad">{rec.prioridad}</span>
              </div>
            ))
          ) : (
            <p>Completa tu perfil para recibir recomendaciones</p>
          )}
        </div>
      </div>

      {predicciones?.alertas?.length > 0 && (
        <div className="dashboard-section">
          <h2>Alertas</h2>
          <div className="alerts">
            {predicciones.alertas.map((alerta, idx) => (
              <div key={idx} className="alert alert-warning">{alerta}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
