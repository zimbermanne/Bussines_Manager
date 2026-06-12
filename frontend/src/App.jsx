import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import BusinessOverview from './pages/BusinessOverview';
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

function PrivateRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user } = useAuth();
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
            <Route path="overview" element={<BusinessOverview />} />
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
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
