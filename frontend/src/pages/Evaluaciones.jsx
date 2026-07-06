import { useState, useEffect } from 'react';
import { evaluacionesService, materiasService } from '../services/api';

export default function Evaluaciones() {
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    materia_id: '',
    tipo: 'examen',
    nota: 7.0,
    ponderacion: 1.0
  });
  const [loading, setLoading] = useState(true);
  const tipos = ['examen', 'tarea', 'proyecto', 'quiz'];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [evRes, matRes] = await Promise.all([
        evaluacionesService.getAll(),
        materiasService.getAll()
      ]);
      setEvaluaciones(evRes.data);
      setMaterias(matRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await evaluacionesService.create({
        ...formData,
        materia_id: parseInt(formData.materia_id)
      });
      setFormData({ materia_id: '', tipo: 'examen', nota: 7.0, ponderacion: 1.0 });
      setShowForm(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await evaluacionesService.delete(id);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  const getMateriaNombre = (id) => materias.find(m => m.id === id)?.nombre || 'Desconocida';

  return (
    <div className="page-container">
      {/* Usamos page-header para que título y botón estén alineados */}
      <div className="page-header">
        <h1>Mis Evaluaciones</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : 'Registrar Evaluación'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card form-card">
          <div className="form-group">
            <label>Materia</label>
            <select value={formData.materia_id} onChange={(e) => setFormData({ ...formData, materia_id: e.target.value })} required>
              <option value="">Selecciona materia</option>
              {materias.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Tipo de Evaluación</label>
            <select value={formData.tipo} onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}>
              {tipos.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Nota</label>
            <input type="number" step="0.1" min="1" max="10" value={formData.nota} onChange={(e) => setFormData({ ...formData, nota: parseFloat(e.target.value) })} required />
          </div>
          <div className="form-group">
            <label>Ponderación</label>
            <input type="number" step="0.1" min="0.1" max="2" value={formData.ponderacion} onChange={(e) => setFormData({ ...formData, ponderacion: parseFloat(e.target.value) })} />
          </div>
          <button type="submit" className="btn-primary">Guardar</button>
        </form>
      )}

      {/* Usamos data-grid y list-card */}
      <div className="data-grid">
        {evaluaciones.length > 0 ? (
          evaluaciones.map(ev => (
            <div key={ev.id} className="card list-card">
              <span className="materia">{getMateriaNombre(ev.materia_id)}</span>
              {/* Aquí usamos el .badge global */}
              <span className={`badge tipo-${ev.tipo}`}>{ev.tipo}</span>
              <span className="nota">Nota: <strong className="text-gradient">{ev.nota}</strong></span>
              <span className="fecha text-muted">{new Date(ev.fecha).toLocaleDateString()}</span>
              <button className="btn-danger" onClick={() => handleDelete(ev.id)}>X</button>
            </div>
          ))
        ) : (
          <div className="card text-center text-muted">No hay evaluaciones. ¡Registra tus primeras notas!</div>
        )}
      </div>
    </div>
  );

}
