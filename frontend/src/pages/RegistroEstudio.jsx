import { useState, useEffect } from 'react';
import { registrosService, materiasService } from '../services/api';

export default function RegistroEstudio() {
  const [registros, setRegistros] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    materia_id: '',
    hora_inicio: '',
    hora_fin: '',
    tipo_actividad: 'estudio',
    descripcion: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [regRes, matRes] = await Promise.all([
        registrosService.getAll(),
        materiasService.getAll()
      ]);
      setRegistros(regRes.data);
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
      await registrosService.create({
        ...formData,
        materia_id: formData.materia_id || null,
        hora_inicio: new Date(formData.hora_inicio),
        hora_fin: new Date(formData.hora_fin)
      });
      setFormData({ materia_id: '', hora_inicio: '', hora_fin: '', tipo_actividad: 'estudio', descripcion: '' });
      setShowForm(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await registrosService.delete(id);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <div className="page-container">
      <h1>Registro de Estudio</h1>
      
      <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancelar' : 'Registrar Sesión'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="form-card">
          <div className="form-group">
            <label>Materia</label>
            <select
              value={formData.materia_id}
              onChange={(e) => setFormData({ ...formData, materia_id: e.target.value })}
            >
              <option value="">Selecciona materia</option>
              {materias.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Hora Inicio</label>
            <input
              type="datetime-local"
              value={formData.hora_inicio}
              onChange={(e) => setFormData({ ...formData, hora_inicio: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Hora Fin</label>
            <input
              type="datetime-local"
              value={formData.hora_fin}
              onChange={(e) => setFormData({ ...formData, hora_fin: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Tipo de Actividad</label>
            <select
              value={formData.tipo_actividad}
              onChange={(e) => setFormData({ ...formData, tipo_actividad: e.target.value })}
            >
              <option value="estudio">Estudio</option>
              <option value="practica">Práctica</option>
              <option value="repaso">Repaso</option>
            </select>
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-primary">Guardar</button>
        </form>
      )}

      <div className="registros-list">
        {registros.length > 0 ? (
          registros.map(reg => (
            <div key={reg.id} className="registro-card">
              <span className="materia">{reg.materia_id ? materias.find(m => m.id === reg.materia_id)?.nombre : 'Sin materia'}</span>
              <span className="tipo">{reg.tipo_actividad}</span>
              <span className="horario">{new Date(reg.hora_inicio).toLocaleString()} - {new Date(reg.hora_fin).toLocaleString()}</span>
              <button className="btn-danger" onClick={() => handleDelete(reg.id)}>X</button>
            </div>
          ))
        ) : (
          <p>No hay registros. ¡Registra tu primera sesión de estudio!</p>
        )}
      </div>
    </div>
  );
}
