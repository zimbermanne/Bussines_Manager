import { useEffect, useState } from 'react';
import { api } from '../utils/api';

const emptyForm = {
  name: '',
  category: 'TRA',
  interval_type: 'monthly',
  due_day: '7',
  next_due_date: new Date().toISOString().slice(0, 10),
};

export default function Deadlines() {
  const [deadlines, setDeadlines] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => api.get('/deadlines/').then(setDeadlines).catch((e) => setError(e.message)).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/deadlines/', {
        name: form.name,
        category: form.category,
        interval_type: form.interval_type,
        due_day: parseInt(form.due_day, 10),
        next_due_date: form.next_due_date,
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
      <h1 className="page-title">Compliance Deadlines</h1>
      <p className="page-subtitle">TRA, BRELA, NSSF and other reminders</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header"><span className="card-title">Add Deadline</span></div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required placeholder="TRA PAYE Filing" />
              </div>
              <div className="form-group">
                <label>Category</label>
                <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required />
              </div>
            </div>
            <div className="form-grid-3">
              <div className="form-group">
                <label>Interval</label>
                <select value={form.interval_type} onChange={(e) => setForm({ ...form, interval_type: e.target.value })}>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              <div className="form-group">
                <label>Due day</label>
                <input type="number" min="1" max="31" value={form.due_day} onChange={(e) => setForm({ ...form, due_day: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Next due date</label>
                <input type="date" value={form.next_due_date} onChange={(e) => setForm({ ...form, next_due_date: e.target.value })} required />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Add deadline'}
            </button>
          </form>
        </div>
      </div>

      {loading ? (
        <div className="loading"><span className="spinner" /></div>
      ) : deadlines.length === 0 ? (
        <div className="empty"><p>No deadlines configured.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Category</th><th>Interval</th><th>Next Due</th></tr>
              </thead>
              <tbody>
                {deadlines.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{d.category}</td>
                    <td>{d.interval_type}</td>
                    <td>{d.next_due_date}</td>
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
