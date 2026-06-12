import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, formatTZS } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  name: '',
  lifespan_type: 'one_year',
  start_date: new Date().toISOString().slice(0, 10),
  interval_type: 'monthly',
  hisa_amount: '',
  penalty_type: 'fixed',
  penalty_value: '',
  loan_interest_rate: '0',
};

export default function Vikoba() {
  const [groups, setGroups] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get('/vikoba/').then(setGroups).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/vikoba/', {
        ...form,
        hisa_amount: parseFloat(form.hisa_amount),
        penalty_value: form.penalty_value ? parseFloat(form.penalty_value) : null,
        loan_interest_rate: parseFloat(form.loan_interest_rate),
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
          <h1 className="page-title">Vikoba Groups</h1>
          <p className="page-subtitle">Savings groups, hisa and penalties</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Group</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Group</th><th>Hisa Amount</th><th>Interval</th><th>Members</th><th></th>
            </tr>
          </thead>
          <tbody>
            {groups.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No groups yet</td></tr>
            ) : groups.map((g) => (
              <tr key={g.id}>
                <td>{g.name}</td>
                <td className="mono">{formatTZS(g.hisa_amount)}</td>
                <td>{g.interval_type}</td>
                <td>{g.member_count}</td>
                <td><Link to={`/vikoba/${g.id}`} className="btn btn-sm btn-secondary">Details</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Create Vikoba Group"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="vikoba-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="vikoba-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Group Name</label>
              <input value={form.name} onChange={set('name')} required />
            </div>
            <div className="form-group">
              <label>Lifespan</label>
              <select value={form.lifespan_type} onChange={set('lifespan_type')}>
                <option value="one_year">1 Year</option>
                <option value="two_years">2 Years</option>
                <option value="permanent">Permanent</option>
              </select>
            </div>
            <div className="form-group">
              <label>Hisa Interval</label>
              <select value={form.interval_type} onChange={set('interval_type')}>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div className="form-group">
              <label>Hisa Amount (TZS)</label>
              <input type="number" value={form.hisa_amount} onChange={set('hisa_amount')} required />
            </div>
            <div className="form-group">
              <label>Start Date</label>
              <input type="date" value={form.start_date} onChange={set('start_date')} required />
            </div>
            <div className="form-group">
              <label>Penalty Type</label>
              <select value={form.penalty_type} onChange={set('penalty_type')}>
                <option value="fixed">Fixed</option>
                <option value="percentage">Percentage</option>
              </select>
            </div>
            <div className="form-group">
              <label>Penalty Value</label>
              <input type="number" value={form.penalty_value} onChange={set('penalty_value')} />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
