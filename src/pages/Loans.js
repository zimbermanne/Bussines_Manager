import { useEffect, useState } from 'react';
import { api, formatTZS } from '../utils/api';

const emptyForm = {
  lender_name: '',
  principal_amount: '',
  interest_type: 'reducing_balance',
  interest_rate: '',
  start_date: new Date().toISOString().slice(0, 10),
  due_day: '15',
};

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => api.get('/loans/').then(setLoans).catch((e) => setError(e.message)).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/loans/', {
        lender_name: form.lender_name,
        principal_amount: parseFloat(form.principal_amount),
        interest_type: form.interest_type,
        interest_rate: parseFloat(form.interest_rate),
        start_date: form.start_date,
        due_day: parseInt(form.due_day, 10),
      });
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Bank Loans</h1>
      <p className="page-subtitle">Track loans and repayment balances</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header"><span className="card-title">Add Loan</span></div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Lender</label>
                <input value={form.lender_name} onChange={(e) => setForm({ ...form, lender_name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Principal (TZS)</label>
                <input type="number" value={form.principal_amount} onChange={(e) => setForm({ ...form, principal_amount: e.target.value })} required />
              </div>
            </div>
            <div className="form-grid-3">
              <div className="form-group">
                <label>Interest type</label>
                <select value={form.interest_type} onChange={(e) => setForm({ ...form, interest_type: e.target.value })}>
                  <option value="simple">Simple</option>
                  <option value="reducing_balance">Reducing balance</option>
                </select>
              </div>
              <div className="form-group">
                <label>Annual rate (%)</label>
                <input type="number" step="0.01" value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Due day of month</label>
                <input type="number" min="1" max="31" value={form.due_day} onChange={(e) => setForm({ ...form, due_day: e.target.value })} required />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Add loan'}
            </button>
          </form>
        </div>
      </div>

      {loading ? (
        <div className="loading"><span className="spinner" /></div>
      ) : loans.length === 0 ? (
        <div className="empty"><p>No loans yet.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Lender</th><th>Principal</th><th>Balance</th><th>Rate</th></tr>
              </thead>
              <tbody>
                {loans.map((l) => (
                  <tr key={l.id}>
                    <td>{l.lender_name}</td>
                    <td>{formatTZS(l.principal_amount)}</td>
                    <td>{formatTZS(l.balance_remaining)}</td>
                    <td>{l.interest_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
