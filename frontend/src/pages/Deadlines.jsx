import React, { useEffect, useState } from 'react';
import { api, formatDate, daysUntil } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  name: '',
  category: 'tra',
  interval_type: 'monthly',
  due_day: '7',
  next_due_date: new Date().toISOString().slice(0, 10),
  notes: '',
};

export default function Deadlines() {
  const [deadlines, setDeadlines] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get('/deadlines/').then(setDeadlines).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/deadlines/', {
        ...form,
        due_day: form.due_day ? parseInt(form.due_day, 10) : null,
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
          <h1 className="page-title">Compliance Deadlines</h1>
          <p className="page-subtitle">TRA, BRELA, NSSF and other reminders</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Deadline</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th><th>Category</th><th>Next Due</th><th>Days Left</th><th>Interval</th>
            </tr>
          </thead>
          <tbody>
            {deadlines.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No deadlines yet</td></tr>
            ) : deadlines.map((d) => {
              const days = daysUntil(d.next_due_date);
              const cls = days <= 1 ? 'urgency-high' : days <= 7 ? 'urgency-mid' : 'urgency-low';
              return (
                <tr key={d.id}>
                  <td>{d.name}</td>
                  <td><span className="badge badge-blue">{d.category}</span></td>
                  <td>{formatDate(d.next_due_date)}</td>
                  <td className={cls}>{days} days</td>
                  <td>{d.interval_type}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Deadline"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="deadline-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="deadline-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Name</label>
              <input value={form.name} onChange={set('name')} required placeholder="TRA PAYE" />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select value={form.category} onChange={set('category')}>
                <option value="tra">TRA</option>
                <option value="brela">BRELA</option>
                <option value="nssf">NSSF</option>
                <option value="wcf">WCF</option>
                <option value="osha">OSHA</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div className="form-group">
              <label>Interval</label>
              <select value={form.interval_type} onChange={set('interval_type')}>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
            <div className="form-group">
              <label>Due Day (monthly)</label>
              <input type="number" min="1" max="31" value={form.due_day} onChange={set('due_day')} />
            </div>
            <div className="form-group">
              <label>Next Due Date</label>
              <input type="date" value={form.next_due_date} onChange={set('next_due_date')} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
