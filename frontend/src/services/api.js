import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      window.location.href = '/login';
    }
    // Extraer el mensaje de error específico de FastAPI (campo "detail")
    const errorMessage = error.response?.data?.detail || 'Error en la solicitud';
    
    // Rechazamos con un objeto que incluye el mensaje limpio para la UI
    return Promise.reject({ 
      status: error.response?.status, 
      message: errorMessage 
    });
  }
);

// ─── SERVICIOS ───

export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
};

export const materiasService = {
  getAll: () => api.get('/materias'),
  create: (data) => api.post('/materias', data),
  update: (id, data) => api.put(`/materias/${id}`, data),
  delete: (id) => api.delete(`/materias/${id}`),
};

export const registrosService = {
  getAll: (params) => api.get('/registros', { params }),
  create: (data) => api.post('/registros', data),
  update: (id, data) => api.put(`/registros/${id}`, data),
  delete: (id) => api.delete(`/registros/${id}`),
};

export const habitosService = {
  getAll: (params) => api.get('/habitos', { params }),
  create: (data) => api.post('/habitos', data),
  update: (id, data) => api.put(`/habitos/${id}`, data),
  delete: (id) => api.delete(`/habitos/${id}`),
};

export const evaluacionesService = {
  getAll: (params) => api.get('/evaluaciones', { params }),
  create: (data) => api.post('/evaluaciones', data),
  update: (id, data) => api.put(`/evaluaciones/${id}`, data),
  delete: (id) => api.delete(`/evaluaciones/${id}`),
};

export const analisisService = {
  getPredicciones: () => api.get('/analisis/predicciones'),
  getPrediccionMateria: (id) => api.get(`/analisis/predicciones/${id}`),
  getRecomendaciones: () => api.get('/analisis/recomendaciones'),
  getEstadisticas: () => api.get('/analisis/estadisticas'),
  chat: (data) => api.post('/analisis/chat', data),
};

export default api;
