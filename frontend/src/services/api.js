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
    return Promise.reject(error);
  }
);

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
  delete: (id) => api.delete(`/habitos/${id}`),
};

export const evaluacionesService = {
  getAll: (params) => api.get('/evaluaciones', { params }),
  create: (data) => api.post('/evaluaciones', data),
  delete: (id) => api.delete(`/evaluaciones/${id}`),
};

export const analisisService = {
  getPredicciones: () => api.get('/analisis/predicciones'),
  getPrediccionMateria: (id) => api.get(`/analisis/predicciones/${id}`),
  getRecomendaciones: () => api.get('/analisis/recomendaciones'),
  getEstadisticas: () => api.get('/analisis/estadisticas'),
};

export default api;
