import { useState, useEffect, useMemo } from 'react';
import {
  analisisService,
  registrosService,
  habitosService,
  materiasService
} from '../services/api';
import {
  PenLine, Send, Sparkles, CheckCircle2, AlertCircle,
  BookOpen, Moon, Smartphone, Dumbbell, Coffee,
  Clock, Calendar, CalendarDays, Activity
} from 'lucide-react';

/* ── Configuracion de iconos por tipo de habito ── */
const HABITO_MAP = {
  sueno:        { Icon: Moon,       color: '#8b5cf6' },
  distraccion:  { Icon: Smartphone, color: '#ef4444' },
  ejercicio:    { Icon: Dumbbell,   color: '#10b981' },
  descanso:     { Icon: Coffee,     color: '#3b82f6' },
  otro:         { Icon: Activity,   color: '#475569' },
};

function HabitoIcon({ tipo, size = 14 }) {
  const cfg = HABITO_MAP[tipo] || HABITO_MAP.otro;
  return <cfg.Icon size={size} style={{ color: cfg.color }} />;
}

/* ── Componente principal ── */
export default function MiDia() {
  const [mensaje, setMensaje]       = useState('');
  const [enviando, setEnviando]     = useState(false);
  const [resultado, setResultado]   = useState(null);
  const [materias, setMaterias]     = useState([]);
  const [registros, setRegistros]   = useState([]);
  const [habitos, setHabitos]       = useState([]);
  const [loading, setLoading]       = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [regRes, habRes, matRes] = await Promise.allSettled([
        registrosService.getAll(),
        habitosService.getAll(),
        materiasService.getAll(),
      ]);
      if (regRes.status === 'fulfilled') setRegistros(regRes.value.data);
      if (habRes.status === 'fulfilled') setHabitos(habRes.value.data);
      if (matRes.status === 'fulfilled') setMaterias(matRes.value.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /* ── Mapa de materias: id → nombre ── */
  const materiaMap = useMemo(() => {
    const map = {};
    materias.forEach(m => { map[m.id] = m.nombre; });
    return map;
  }, [materias]);

  /* ── Items recientes (mezcla registros + habitos, ordenados) ── */
  const recentItems = useMemo(() => {
    const items = [];

    registros.forEach(r => {
      items.push({
        key: `reg-${r.id}`,
        tipo: 'registro',
        fecha: new Date(r.hora_inicio),
        actividad: r.tipo_actividad,
        materia: r.materia_id ? materiaMap[r.materia_id] || `Materia #${r.materia_id}` : 'General',
        detalle: calcularDuracion(r.hora_inicio, r.hora_fin),
      });
    });

    habitos.forEach(h => {
      items.push({
        key: `hab-${h.id}`,
        tipo: 'habito',
        fecha: new Date(h.fecha),
        habitoTipo: h.tipo,
        detalle: `${h.duracion_minutos} min`,
      });
    });

    items.sort((a, b) => b.fecha - a.fecha);
    return items.slice(0, 6);
  }, [registros, habitos, materiaMap]);

  /* ── Enviar mensaje ── */
  const handleRegistrar = async (e) => {
    e.preventDefault();
    if (!mensaje.trim() || enviando) return;

    setEnviando(true);
    setResultado(null);

    try {
      const res = await analisisService.chat({ mensaje: mensaje.trim() });
      setResultado({ type: 'success', data: res.data });
      setMensaje('');
      await loadData();
    } catch (err) {
      setResultado({
        type: 'error',
        message: err.message || 'Error al comunicarse con la IA'
      });
    } finally {
      setEnviando(false);
    }
  };

  /* ── Helpers para renderizar el resultado ── */
  const getResultadoTexto = () => {
    if (!resultado?.data) return '';
    if (typeof resultado.data === 'string') return resultado.data;
    return resultado.data.respuesta || '';
  };

  const getRegistrosExtraidos = () => {
    if (!resultado?.data || typeof resultado.data === 'string') return [];
    return resultado.data.registros_extraidos || [];
  };

  const getHabitosExtraidos = () => {
    if (!resultado?.data || typeof resultado.data === 'string') return [];
    return resultado.data.habitos_extraidos || [];
  };

  if (loading) {
    return (
      <div className="page-center">
        <div className="loading">
          <div className="spinner"></div>Cargando...
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">

      {/* ── Header ── */}
      <div className="page-header">
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <PenLine size={28} /> Mi Dia
          </h1>
          <p>Describe tu actividad y la IA registrara todo automaticamente</p>
        </div>
      </div>

      {/* ── Input ── */}
      <form onSubmit={handleRegistrar} className="card">
        <div className="form-group">
          <label>¿Que hiciste hoy? (o dias anteriores)</label>
          <textarea
            value={mensaje}
            onChange={(e) => setMensaje(e.target.value)}
            placeholder={'Ejemplo: "Hoy estudie 2 horas de calculo, dormi 7 horas, me distraje 30 min con el celular..."'}
            rows={5}
            disabled={enviando}
          />
        </div>
        <button
          type="submit"
          className="btn-primary"
          disabled={enviando || !mensaje.trim()}
        >
          {enviando ? (
            <><div className="spinner"></div> Procesando...</>
          ) : (
            <><Send size={16} /> Registrar</>
          )}
        </button>
      </form>

      {/* ── Resultado ── */}
      {resultado && (
        <div className={`card ${resultado.type === 'success' ? 'result-card' : 'result-card result-card--error'}`}>

          {resultado.type === 'success' ? (
            <>
              <div className="result-header">
                <Sparkles size={18} className="result-header__icon" />
                <span>La IA detecto:</span>
              </div>

              {/* Registros extraidos */}
              {getRegistrosExtraidos().length > 0 && (
                <div className="detail-section">
                  <h4 className="detail-section__title">
                    <BookOpen size={14} /> Registros de estudio
                  </h4>
                  {getRegistrosExtraidos().map((r, i) => (
                    <div key={i} className="result-item">
                      <span className="result-item__icon">
                        <BookOpen size={14} style={{ color: '#6366f1' }} />
                      </span>
                      <span className="result-item__text">
                        {r.tipo_actividad || 'estudio'} - {r.materia || 'General'}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Habitos extraidos */}
              {getHabitosExtraidos().length > 0 && (
                <div className="detail-section">
                  <h4 className="detail-section__title">
                    <Activity size={14} /> Habitos
                  </h4>
                  {getHabitosExtraidos().map((h, i) => (
                    <div key={i} className="result-item">
                      <span className="result-item__icon">
                        <HabitoIcon tipo={h.tipo} size={14} />
                      </span>
                      <span className="result-item__text">{h.tipo}</span>
                      <span className="result-item__sub">{h.duracion_minutos} min</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Respuesta conversacional */}
              {getResultadoTexto() && (
                <p className="result-respuesta">{getResultadoTexto()}</p>
              )}

              <div className="success-message" style={{ marginTop: 'var(--space-4)' }}>
                <CheckCircle2 size={16} /> Todo guardado correctamente
              </div>
            </>
          ) : (
            <div className="error-message">
              <AlertCircle size={16} /> {resultado.message}
            </div>
          )}
        </div>
      )}

      {/* ── Actividad reciente ── */}
      <div style={{ marginTop: 'var(--space-8)' }}>
        <h2 style={{
          fontSize: 'var(--font-size-lg)',
          fontWeight: 600,
          marginBottom: 'var(--space-2)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)'
        }}>
          <Clock size={18} /> Actividad reciente
        </h2>
        <p className="text-muted" style={{ marginBottom: 'var(--space-2)', fontSize: 'var(--font-size-sm)' }}>
          Ultimos registros y habitos
        </p>

        {recentItems.length > 0 ? (
          <div className="recent-grid">
            {recentItems.map(item => (
              <div key={item.key} className="card recent-card">
                <div className="recent-card__header">
                  {item.tipo === 'registro' ? (
                    <>
                      <BookOpen size={14} style={{ color: '#6366f1' }} />
                      <span className="recent-card__title">{item.materia}</span>
                    </>
                  ) : (
                    <>
                      <HabitoIcon tipo={item.habitoTipo} size={14} />
                      <span className={`badge tipo-${item.habitoTipo}`}>
                        {item.habitoTipo}
                      </span>
                    </>
                  )}
                </div>

                <span style={{ color: 'var(--color-text-primary)', fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>
                  {item.detalle}
                </span>

                <div className="recent-card__meta">
                  <Calendar size={12} />
                  <span>{item.fecha.toLocaleDateString()}</span>
                  {item.tipo === 'registro' && (
                    <>
                      <Clock size={12} />
                      <span>{item.fecha.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card detail-empty">
            <CalendarDays size={32} className="detail-empty__icon" />
            <p>Aun no hay actividad registrada.</p>
            <p>Cuentale a la IA sobre tu dia!</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Helper: calcular duracion entre dos fechas ── */
function calcularDuracion(inicio, fin) {
  const ms = new Date(fin) - new Date(inicio);
  const minutos = Math.round(ms / 60000);
  if (minutos >= 60) {
    const h = Math.floor(minutos / 60);
    const m = minutos % 60;
    return m > 0 ? `${h}h ${m}min` : `${h}h`;
  }
  return `${minutos} min`;
}