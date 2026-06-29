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
      <h1>Predicciones de Rendimiento</h1>
      
      <div className="prediccion-summary">
        <div className="prediccion-main">
          <h2>Promedio Predicho</h2>
          <p className="prediccion-value">{predicciones?.promedio_predicho?.toFixed(1) || 'N/A'}</p>
          <p className="confianza">Confianza: {Math.round((predicciones?.confianza || 0) * 100)}%</p>
        </div>
      </div>

      <div className="predicciones-grid">
        {predicciones?.materias?.map((m, idx) => (
          <div key={m.materia_id} className="prediccion-card">
            <h3>{m.materia_nombre}</h3>
            <p className="prediccion-nota">Nota predicha: <strong>{m.prediccion_nota}</strong></p>
            <p className={`tendencia tendencia-${m.tendencia}`}>Tendencia: {m.tendencia}</p>
            <p className="confianza">Confianza: {Math.round(m.confianza * 100)}%</p>
            {m.factores?.length > 0 && (
              <div className="factores">
                <h4>Factores:</h4>
                <ul>
                  {m.factores.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            )}
          </div>
        )) || <p>Registra materias y evaluaciones para ver predicciones</p>}
      </div>

      {predicciones?.alertas?.length > 0 && (
        <div className="alerts-section">
          <h2>Alertas</h2>
          {predicciones.alertas.map((alerta, idx) => (
            <div key={idx} className="alert alert-warning">{alerta}</div>
          ))}
        </div>
      )}
    </div>
  );
}
