import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Purchases from './pages/Purchases';
import Expenses from './pages/Expenses';
import ProfitLoss from './pages/ProfitLoss';
import BankLoans from './pages/BankLoans';
import LoanDetail from './pages/LoanDetail';
import Deadlines from './pages/Deadlines';
import Suppliers from './pages/Suppliers';
import Tenders from './pages/Tenders';
import TenderDetail from './pages/TenderDetail';
import Vikoba from './pages/Vikoba';
import VikobaDetail from './pages/VikobaDetail';
import Documents from './pages/Documents';
import CompanyCare from './pages/CompanyCare';
import Customers from './pages/Customers';
import Staff from './pages/Staff';

function NotFound() {
  return (
    <div className="empty" style={{ padding: '80px 20px' }}>
      <div className="empty-icon">🤔</div>
      <h3>Page not found</h3>
      <p>The page you're looking for doesn't exist or may have moved.</p>
      <a href="/" className="btn btn-primary" style={{ marginTop: 16, display: 'inline-flex' }}>
        Back to Dashboard
      </a>
    </div>
  );
}

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  // If your AuthContext exposes a `loading` flag while it checks a stored
  // token on first mount, this prevents a flash-redirect to /login before
  // that check finishes. If AuthContext doesn't have `loading` yet, this
  // safely no-ops (loading is undefined/falsy) and behaves as before.
  if (loading) return <div className="loading"><div className="spinner" />Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading"><div className="spinner" />Loading…</div>;
  if (user) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="sales" element={<Sales />} />
            <Route path="purchases" element={<Purchases />} />
            <Route path="expenses" element={<Expenses />} />
            <Route path="profit-loss" element={<ProfitLoss />} />
            <Route path="loans" element={<BankLoans />} />
            <Route path="loans/:id" element={<LoanDetail />} />
            <Route path="deadlines" element={<Deadlines />} />
            <Route path="suppliers" element={<Suppliers />} />
            <Route path="tenders" element={<Tenders />} />
            <Route path="tenders/:id" element={<TenderDetail />} />
            <Route path="vikoba" element={<Vikoba />} />
            <Route path="vikoba/:id" element={<VikobaDetail />} />
            <Route path="documents" element={<Documents />} />
            <Route path="company-care" element={<CompanyCare />} />
            <Route path="customers" element={<Customers />} />
            <Route path="staff" element={<Staff />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
