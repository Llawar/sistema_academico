import { useState, useEffect, useMemo } from 'react';
import {
  registrosService,
  habitosService,
  materiasService
} from '../services/api';
import {
  CalendarDays, ChevronLeft, ChevronRight,
  BookOpen, Moon, Smartphone, Dumbbell, Coffee,
  Clock, BarChart3, Activity, Calendar
} from 'lucide-react';

/* ── Constantes ── */
const DIAS_SEMANA = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

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
export default function Actividad() {
  const [registros, setRegistros]     = useState([]);
  const [habitos, setHabitos]         = useState([]);
  const [materias, setMaterias]       = useState([]);
  const [loading, setLoading]         = useState(true);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear]   = useState(new Date().getFullYear());
  const [selectedDay, setSelectedDay]   = useState(null);

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

  /* ── Construir dias del calendario ── */
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay  = new Date(currentYear, currentMonth + 1, 0);
    const startOffset = (firstDay.getDay() + 6) % 7; // Lunes = 0
    const totalDays = lastDay.getDate();
    const today = new Date();

    const days = [];

    // Celdas vacias antes del dia 1
    for (let i = 0; i < startOffset; i++) {
      days.push({ empty: true });
    }

    // Dias del mes
    for (let d = 1; d <= totalDays; d++) {
      const isToday = d === today.getDate()
        && currentMonth === today.getMonth()
        && currentYear === today.getFullYear();
      const isSelected = selectedDay
        && selectedDay.day === d
        && selectedDay.month === currentMonth
        && selectedDay.year === currentYear;

      // Registros de este dia
      const dayRegs = registros.filter(r => {
        const rd = new Date(r.hora_inicio);
        return rd.getDate() === d
          && rd.getMonth() === currentMonth
          && rd.getFullYear() === currentYear;
      });

      // Habitos de este dia
      const dayHabs = habitos.filter(h => {
        const hd = new Date(h.fecha);
        return hd.getDate() === d
          && hd.getMonth() === currentMonth
          && hd.getFullYear() === currentYear;
      });

      days.push({
        day: d,
        isToday,
        isSelected,
        registros: dayRegs,
        habitos: dayHabs,
        hasData: dayRegs.length > 0 || dayHabs.length > 0,
      });
    }

    return days;
  }, [currentMonth, currentYear, registros, habitos, selectedDay]);

  /* ── Datos del dia seleccionado ── */
  const selectedDayData = useMemo(() => {
    if (!selectedDay) return null;

    const dayRegs = registros.filter(r => {
      const rd = new Date(r.hora_inicio);
      return rd.getDate() === selectedDay.day
        && rd.getMonth() === selectedDay.month
        && rd.getFullYear() === selectedDay.year;
    });

    const dayHabs = habitos.filter(h => {
      const hd = new Date(h.fecha);
      return hd.getDate() === selectedDay.day
        && hd.getMonth() === selectedDay.month
        && hd.getFullYear() === selectedDay.year;
    });

    const totalMin = dayRegs.reduce((sum, r) => {
      return sum + (new Date(r.hora_fin) - new Date(r.hora_inicio)) / 60000;
    }, 0);

    return {
      registros: dayRegs,
      habitos: dayHabs,
      totalHoras: (totalMin / 60).toFixed(1),
    };
  }, [selectedDay, registros, habitos]);

  /* ── Resumen semanal ── */
  const weeklySummary = useMemo(() => {
    if (!selectedDay) return null;

    const selected = new Date(selectedDay.year, selectedDay.month, selectedDay.day);
    const dow = (selected.getDay() + 6) % 7;
    const monday = new Date(selected);
    monday.setDate(monday.getDate() - dow);
    monday.setHours(0, 0, 0, 0);

    const sunday = new Date(monday);
    sunday.setDate(sunday.getDate() + 6);
    sunday.setHours(23, 59, 59, 999);

    const weekRegs = registros.filter(r => {
      const rd = new Date(r.hora_inicio);
      return rd >= monday && rd <= sunday;
    });

    const weekHabs = habitos.filter(h => {
      const hd = new Date(h.fecha);
      return hd >= monday && hd <= sunday;
    });

    // Estudio total
    const totalEstudioMin = weekRegs.reduce((sum, r) => {
      return sum + (new Date(r.hora_fin) - new Date(r.hora_inicio)) / 60000;
    }, 0);

    // Sueño promedio
    const suenoItems = weekHabs.filter(h => h.tipo === 'sueno');
    const promedioSuenoMin = suenoItems.length > 0
      ? suenoItems.reduce((s, h) => s + h.duracion_minutos, 0) / suenoItems.length
      : 0;

    // Ejercicio total
    const totalEjercicio = weekHabs
      .filter(h => h.tipo === 'ejercicio')
      .reduce((s, h) => s + h.duracion_minutos, 0);

    // Distraccion total
    const totalDistraccion = weekHabs
      .filter(h => h.tipo === 'distraccion')
      .reduce((s, h) => s + h.duracion_minutos, 0);

    // Dias con datos
    const daysSet = new Set();
    weekRegs.forEach(r => daysSet.add(new Date(r.hora_inicio).toDateString()));
    weekHabs.forEach(h => daysSet.add(new Date(h.fecha).toDateString()));

    return {
      monday,
      sunday,
      totalEstudio: (totalEstudioMin / 60).toFixed(1),
      promedioSueno: (promedioSuenoMin / 60).toFixed(1),
      totalEjercicio,
      totalDistraccion,
      daysWithData: daysSet.size,
    };
  }, [selectedDay, registros, habitos]);

  /* ── Navegacion ── */
  const goToPrevMonth = () => {
    setSelectedDay(null);
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const goToNextMonth = () => {
    setSelectedDay(null);
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const handleDayClick = (day) => {
    if (day.empty) return;
    setSelectedDay({ day: day.day, month: currentMonth, year: currentYear });
  };

  /* ── Helpers ── */
  const formatHora = (dateStr) => {
    return new Date(dateStr).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calcDuracion = (ini, fin) => {
    const min = Math.round((new Date(fin) - new Date(ini)) / 60000);
    if (min >= 60) {
      const h = Math.floor(min / 60);
      const m = min % 60;
      return m > 0 ? `${h}h ${m}min` : `${h}h`;
    }
    return `${min} min`;
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
            <CalendarDays size={28} /> Mi Actividad
          </h1>
          <p>Revisa tu historial de estudio y habitos</p>
        </div>
      </div>

      {/* ════════════════════════════════════════
          CALENDARIO
          ════════════════════════════════════════ */}
      <div className="card">
        <div className="calendar-header">
          <button className="calendar-nav-btn" onClick={goToPrevMonth}>
            <ChevronLeft size={18} />
          </button>
          <span className="calendar-header__title">
            {MESES[currentMonth]} {currentYear}
          </span>
          <button className="calendar-nav-btn" onClick={goToNextMonth}>
            <ChevronRight size={18} />
          </button>
        </div>

        <div className="calendar-weekdays">
          {DIAS_SEMANA.map(d => (
            <div key={d} className="calendar-weekday">{d}</div>
          ))}
        </div>

        <div className="calendar-grid">
          {calendarDays.map((day, idx) => (
            <div
              key={idx}
              className={[
                'calendar-day',
                day.empty && 'calendar-day--empty',
                day.isToday && 'calendar-day--today',
                day.isSelected && 'calendar-day--selected',
                day.hasData && 'calendar-day--has-data',
              ].filter(Boolean).join(' ')}
              onClick={() => handleDayClick(day)}
            >
              {!day.empty && (
                <>
                  <span className="calendar-day__number">{day.day}</span>
                  {day.hasData && (
                    <div className="calendar-day__dots">
                      {day.registros.length > 0 && (
                        <span className="calendar-day__dot calendar-day__dot--estudio"></span>
                      )}
                      {day.habitos.some(h => h.tipo === 'sueno') && (
                        <span className="calendar-day__dot calendar-day__dot--sueno"></span>
                      )}
                      {day.habitos.some(h => h.tipo === 'distraccion') && (
                        <span className="calendar-day__dot calendar-day__dot--distraccion"></span>
                      )}
                      {day.habitos.some(h => h.tipo === 'ejercicio') && (
                        <span className="calendar-day__dot calendar-day__dot--ejercicio"></span>
                      )}
                      {day.habitos.some(h => h.tipo === 'descanso') && (
                        <span className="calendar-day__dot calendar-day__dot--descanso"></span>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ════════════════════════════════════════
          DETALLE DEL DIA
          ════════════════════════════════════════ */}
      {selectedDayData ? (
        <div className="card" style={{ marginTop: 'var(--space-6)' }}>
          <h2 style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 600,
            marginBottom: 'var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)'
          }}>
            <Calendar size={18} />
            {selectedDay.day} de {MESES[selectedDay.month]} {selectedDay.year}
          </h2>

          {/* Registros */}
          {selectedDayData.registros.length > 0 && (
            <div className="detail-section">
              <h3 className="detail-section__title">
                <BookOpen size={14} /> Registros de Estudio
              </h3>
              <div className="data-grid" style={{ marginTop: 0 }}>
                {selectedDayData.registros.map(reg => (
                  <div key={reg.id} className="list-card">
                    <span className="badge-pill">{reg.tipo_actividad}</span>
                    <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
                      {reg.materia_id
                        ? materiaMap[reg.materia_id] || `Materia #${reg.materia_id}`
                        : 'General'}
                    </span>
                    <span className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                      <Clock size={12} />
                      {formatHora(reg.hora_inicio)} - {formatHora(reg.hora_fin)}
                    </span>
                    <span className="badge">
                      {calcDuracion(reg.hora_inicio, reg.hora_fin)}
                    </span>
                  </div>
                ))}
              </div>
              <p style={{
                marginTop: 'var(--space-3)',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)'
              }}>
                Total: <strong className="text-gradient">{selectedDayData.totalHoras} horas</strong> de estudio
              </p>
            </div>
          )}

          {/* Habitos */}
          {selectedDayData.habitos.length > 0 && (
            <div className="detail-section">
              <h3 className="detail-section__title">
                <Activity size={14} /> Habitos
              </h3>
              <div className="data-grid" style={{ marginTop: 0 }}>
                {selectedDayData.habitos.map(hab => (
                  <div key={hab.id} className="list-card">
                    <HabitoIcon tipo={hab.tipo} size={16} />
                    <span className={`badge tipo-${hab.tipo}`}>{hab.tipo}</span>
                    <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
                      {hab.duracion_minutos} min
                    </span>
                    {hab.notas && (
                      <span className="text-muted">{hab.notas}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sin datos */}
          {selectedDayData.registros.length === 0
            && selectedDayData.habitos.length === 0 && (
            <div className="detail-empty">
              <CalendarDays size={32} className="detail-empty__icon" />
              <p>No hay actividad registrada este dia</p>
            </div>
          )}
        </div>
      ) : (
        <div className="card detail-empty" style={{ marginTop: 'var(--space-6)' }}>
          <CalendarDays size={32} className="detail-empty__icon" />
          <p>Selecciona un dia en el calendario para ver el detalle</p>
        </div>
      )}

      {/* ════════════════════════════════════════
          RESUMEN SEMANAL
          ════════════════════════════════════════ */}
      {weeklySummary && (
        <div className="card" style={{ marginTop: 'var(--space-6)' }}>
          <h2 style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 600,
            marginBottom: 'var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)'
          }}>
            <BarChart3 size={18} />
            Resumen: {weeklySummary.monday.getDate()} - {weeklySummary.sunday.getDate()} de {MESES[currentMonth]}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="progress-row">
              <span className="progress-row__label">
                <BookOpen size={14} /> Estudio total
              </span>
              <div className="progress-row__track">
                <div
                  className="progress-row__fill"
                  style={{ width: `${Math.min((parseFloat(weeklySummary.totalEstudio) / 20) * 100, 100)}%` }}
                />
              </div>
              <span className="progress-row__value">{weeklySummary.totalEstudio}h</span>
            </div>

            <div className="progress-row">
              <span className="progress-row__label">
                <Moon size={14} style={{ color: '#8b5cf6' }} /> Sueno promedio
              </span>
              <div className="progress-row__track">
                <div
                  className="progress-row__fill progress-row__fill--cyan"
                  style={{ width: `${Math.min((parseFloat(weeklySummary.promedioSueno) / 8) * 100, 100)}%` }}
                />
              </div>
              <span className="progress-row__value">{weeklySummary.promedioSueno}h</span>
            </div>

            <div className="progress-row">
              <span className="progress-row__label">
                <Dumbbell size={14} style={{ color: '#10b981' }} /> Ejercicio
              </span>
              <div className="progress-row__track">
                <div
                  className="progress-row__fill progress-row__fill--success"
                  style={{ width: `${Math.min((weeklySummary.totalEjercicio / 150) * 100, 100)}%` }}
                />
              </div>
              <span className="progress-row__value">{weeklySummary.totalEjercicio} min</span>
            </div>

            <div className="progress-row">
              <span className="progress-row__label">
                <Smartphone size={14} style={{ color: '#ef4444' }} /> Distracciones
              </span>
              <div className="progress-row__track">
                <div
                  className="progress-row__fill progress-row__fill--danger"
                  style={{ width: `${Math.min((weeklySummary.totalDistraccion / 120) * 100, 100)}%` }}
                />
              </div>
              <span className="progress-row__value">{weeklySummary.totalDistraccion} min</span>
            </div>
          </div>

          <p style={{
            marginTop: 'var(--space-4)',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-muted)'
          }}>
            Dias con datos: {weeklySummary.daysWithData} / 7
          </p>
        </div>
      )}
    </div>
  );
}