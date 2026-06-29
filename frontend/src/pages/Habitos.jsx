import { useState, useEffect } from 'react';
import { habitosService, materiasService } from '../services/api';

export default function Habitos() {
  const [habitos, setHabitos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ tipo: 'descanso', duracion_minutos: 30, notas: '' });
  const [loading, setLoading] = useState(true);
  const tipos = ['descanso', 'distraccion', 'ejercicio', 'sueno'];

  useEffect(() => {
    loadHabitos();
  }, []);

  const loadHabitos = async () => {
    try {
      const res = await habitosService.getAll();
      setHabitos(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await habitosService.create(formData);
      setFormData({ tipo: 'descanso', duracion_minutos: 30, notas: '' });
      setShowForm(false);
      loadHabitos();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await habitosService.delete(id);
      loadHabitos();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <div className="page-container">
      <h1>Mis Hábitos</h1>
      
      <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancelar' : 'Registrar Hábito'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="form-card">
          <div className="form-group">
            <label>Tipo de Hábito</label>
            <select
              value={formData.tipo}
              onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
            >
              {tipos.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Duración (minutos)</label>
            <input
              type="number"
              min="1"
              value={formData.duracion_minutos}
              onChange={(e) => setFormData({ ...formData, duracion_minutos: parseInt(e.target.value) })}
              required
            />
          </div>
          <div className="form-group">
            <label>Notas (opcional)</label>
            <textarea
              value={formData.notas}
              onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-primary">Guardar</button>
        </form>
      )}

      <div className="habitos-list">
        {habitos.length > 0 ? (
          habitos.map(habito => (
            <div key={habito.id} className="habito-card">
              <span className={`tipo-badge tipo-${habito.tipo}`}>{habito.tipo}</span>
              <span className="duracion">{habito.duracion_minutos} min</span>
              <span className="fecha">{new Date(habito.fecha).toLocaleDateString()}</span>
              <button className="btn-danger" onClick={() => handleDelete(habito.id)}>X</button>
            </div>
          ))
        ) : (
          <p>No hay hábitos registrados. ¡Registra tus hábitos diarios!</p>
        )}
      </div>
    </div>
  );
}
