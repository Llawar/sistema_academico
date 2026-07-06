import { useState, useEffect } from 'react';
import { analisisService } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Predicciones() {
  const [predicciones, setPredicciones] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPredicciones();
  }, []);

  const loadPredicciones = async () => {
    try {
      const res = await analisisService.getPredicciones();
      setPredicciones(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Predicciones de Rendimiento</h1>
      </div>
      
      {/* Reutilizamos los estilos del Dashboard para el Promedio gigante */}
      <div className="card stat-card card--centered" style={{ marginBottom: '40px' }}>
        <h3>Promedio Predicho</h3>
        <p className="stat-value text-gradient">{predicciones?.promedio_predicho?.toFixed(1) || 'N/A'}</p>
        <p className="text-muted mt-2">Confianza: {Math.round((predicciones?.confianza || 0) * 100)}%</p>
      </div>

      <h2 className="section-title">Detalle por Materia</h2>
      <div className="data-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        {predicciones?.materias?.map((m) => (
          <div key={m.materia_id} className="card">
            <h3 className="card__title">{m.materia_nombre}</h3>
            <p style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Nota predicha: <strong className="text-gradient">{m.prediccion_nota}</strong></p>
            <p style={{ marginBottom: '10px' }}><span className="badge badge-pill">{m.tendencia}</span></p>
            <p className="text-muted" style={{ marginBottom: '15px' }}>Confianza: {Math.round(m.confianza * 100)}%</p>
            
            {m.factores?.length > 0 && (
              <div style={{ paddingTop: '15px', borderTop: '1px solid var(--color-border)' }}>
                <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px', fontSize: '0.9rem' }}>Factores:</h4>
                <ul style={{ paddingLeft: '20px', color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  {m.factores.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            )}
          </div>
        )) || <div className="card text-center text-muted">Registra materias y evaluaciones para ver predicciones</div>}
      </div>

      {predicciones?.alertas?.length > 0 && (
        <div style={{ marginTop: '40px' }}>
          <h2 className="section-title">Alertas</h2>
          <div className="data-grid">
            {predicciones.alertas.map((alerta, idx) => (
              <div key={idx} className="alert-warning">{alerta}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
