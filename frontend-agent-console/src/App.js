import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/pages/Login';
import Dashboard from './components/pages/Dashboard';
import AdminDashboard from './components/pages/AdminDashboard';
import ProtectedRoute from './components/pages/ProtectedRoute';

function App() {
  const agentId = localStorage.getItem('agentId');
  const isAdmin = localStorage.getItem('isAdmin') === '1' || localStorage.getItem('isAdmin') === 1;

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute>
            {isAdmin ? <AdminDashboard /> : <Navigate to="/dashboard" />}
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
