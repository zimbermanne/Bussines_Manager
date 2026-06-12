import React, { useEffect, useState } from 'react';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

const CATEGORIES = ['rent', 'transport', 'utilities', 'salary', 'supplies', 'other'];

const emptyForm = {
  business_unit_id: '',
  expense_date: new Date().toISOString().slice(0, 10),
  category: 'other',
  description: '',
  amount: '',
};

export default function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [units, setUnits] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([api.get('/expenses/'), api.get('/business-units/')])
      .then(([e, u]) => { setExpenses(e); setUnits(u); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/expenses/', {
        ...form,
        business_unit_id: form.business_unit_id || null,
        amount: parseFloat(form.amount),
      });
      setShowModal(false);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading"><span className="spinner" /> Loading…</div>;

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Expenses</h1>
          <p className="page-subtitle">Business expenses by category</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Expense</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th><th>Category</th><th>Description</th><th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {expenses.length === 0 ? (
              <tr><td colSpan={4} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No expenses yet</td></tr>
            ) : expenses.map((ex) => (
              <tr key={ex.id}>
                <td>{formatDate(ex.expense_date)}</td>
                <td><span className="badge badge-gray">{ex.category}</span></td>
                <td>{ex.description || '—'}</td>
                <td className="mono">{formatTZS(ex.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Expense"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="expense-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="expense-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={form.expense_date} onChange={set('expense_date')} required />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select value={form.category} onChange={set('category')}>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Description</label>
              <input value={form.description} onChange={set('description')} />
            </div>
            <div className="form-group">
              <label>Amount (TZS)</label>
              <input type="number" step="0.01" value={form.amount} onChange={set('amount')} required />
            </div>
            <div className="form-group">
              <label>Business Unit</label>
              <select value={form.business_unit_id} onChange={set('business_unit_id')}>
                <option value="">— None —</option>
                {units.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
