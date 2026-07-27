import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Materias from './pages/Materias';
import Actividad from './pages/Actividad';
import Predicciones from './pages/Predicciones';
import MiDia from './pages/MiDia';
import Evaluaciones from './pages/Evaluaciones';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/materias" element={
            <ProtectedRoute>
              <Materias />
            </ProtectedRoute>
          } />
          <Route path="/mi-dia" element={
            <ProtectedRoute>
              <MiDia />
            </ProtectedRoute>
          } />
          <Route path="/predicciones" element={
            <ProtectedRoute>
              <Predicciones />
            </ProtectedRoute>
          } />
          <Route path="/actividad" element={
            <ProtectedRoute>
              <Actividad />
            </ProtectedRoute>
          } />
          <Route path="/evaluaciones" element={
            <ProtectedRoute>
              <Evaluaciones />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
