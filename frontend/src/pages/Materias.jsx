import { useState, useEffect } from 'react';
import { materiasService, evaluacionesService } from '../services/api';

export default function Materias() {
  const [materias, setMaterias] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ nombre: '', objetivo_nota: 7.0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMaterias();
  }, []);

  const loadMaterias = async () => {
    try {
      const res = await materiasService.getAll();
      setMaterias(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await materiasService.create(formData);
      setFormData({ nombre: '', objetivo_nota: 7.0 });
      setShowForm(false);
      loadMaterias();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (confirm('¿Eliminar materia?')) {
      try {
        await materiasService.delete(id);
        loadMaterias();
      } catch (err) {
        console.error(err);
      }
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <div className="page-container">
      <h1>Mis Materias</h1>
      
      <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancelar' : 'Agregar Materia'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="form-card">
          <div className="form-group">
            <label>Nombre de la Materia</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Objetivo de Nota</label>
            <input
              type="number"
              step="0.1"
              min="1"
              max="10"
              value={formData.objetivo_nota}
              onChange={(e) => setFormData({ ...formData, objetivo_nota: parseFloat(e.target.value) })}
            />
          </div>
          <button type="submit" className="btn-primary">Guardar</button>
        </form>
      )}

      <div className="materias-grid">
        {materias.length > 0 ? (
          materias.map(materia => (
            <div key={materia.id} className="materia-card">
              <h3>{materia.nombre}</h3>
              <p>Objetivo: {materia.objetivo_nota}</p>
              <button className="btn-danger" onClick={() => handleDelete(materia.id)}>
                Eliminar
              </button>
            </div>
          ))
        ) : (
          <p>No hay materias. ¡Agrega tu primera materia!</p>
        )}
      </div>
    </div>
  );
}
