import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Loans from './pages/Loans';
import Deadlines from './pages/Deadlines';
import Tenders from './pages/Tenders';
import Suppliers from './pages/Suppliers';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="sales" element={<Sales />} />
        <Route path="loans" element={<Loans />} />
        <Route path="deadlines" element={<Deadlines />} />
        <Route path="tenders" element={<Tenders />} />
        <Route path="suppliers" element={<Suppliers />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
