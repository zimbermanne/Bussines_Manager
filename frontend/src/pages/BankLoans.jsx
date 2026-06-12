import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, formatTZS } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  lender_name: '',
  principal_amount: '',
  interest_type: 'reducing_balance',
  interest_rate: '',
  start_date: new Date().toISOString().slice(0, 10),
  due_day: '1',
  grace_period_months: '0',
  notes: '',
};

export default function BankLoans() {
  const [loans, setLoans] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get('/loans/').then(setLoans).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/loans/', {
        ...form,
        principal_amount: parseFloat(form.principal_amount),
        interest_rate: parseFloat(form.interest_rate),
        due_day: parseInt(form.due_day, 10),
        grace_period_months: parseInt(form.grace_period_months, 10),
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
          <h1 className="page-title">Bank Loans</h1>
          <p className="page-subtitle">Track loans and log payments</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Loan</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Lender</th><th>Principal</th><th>Balance</th><th>Rate</th><th>Due Day</th><th></th>
            </tr>
          </thead>
          <tbody>
            {loans.length === 0 ? (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No loans yet</td></tr>
            ) : loans.map((l) => (
              <tr key={l.id}>
                <td>{l.lender_name}</td>
                <td className="mono">{formatTZS(l.principal_amount)}</td>
                <td className="mono">{formatTZS(l.balance_remaining)}</td>
                <td>{l.interest_rate}% ({l.interest_type})</td>
                <td>{l.due_day}</td>
                <td><Link to={`/loans/${l.id}`} className="btn btn-sm btn-secondary">Details</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Bank Loan"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="loan-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="loan-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group">
              <label>Lender</label>
              <input value={form.lender_name} onChange={set('lender_name')} required placeholder="CRDB, NMB…" />
            </div>
            <div className="form-group">
              <label>Principal (TZS)</label>
              <input type="number" value={form.principal_amount} onChange={set('principal_amount')} required />
            </div>
            <div className="form-group">
              <label>Interest Type</label>
              <select value={form.interest_type} onChange={set('interest_type')}>
                <option value="simple">Simple</option>
                <option value="reducing_balance">Reducing Balance</option>
              </select>
            </div>
            <div className="form-group">
              <label>Annual Rate (%)</label>
              <input type="number" step="0.01" value={form.interest_rate} onChange={set('interest_rate')} required />
            </div>
            <div className="form-group">
              <label>Start Date</label>
              <input type="date" value={form.start_date} onChange={set('start_date')} required />
            </div>
            <div className="form-group">
              <label>Due Day of Month</label>
              <input type="number" min="1" max="31" value={form.due_day} onChange={set('due_day')} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
