import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

export default function VikobaDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [showMember, setShowMember] = useState(false);
  const [showHisa, setShowHisa] = useState(false);
  const [memberForm, setMemberForm] = useState({ full_name: '', phone: '' });
  const [hisaForm, setHisaForm] = useState({
    member_id: '',
    due_date: new Date().toISOString().slice(0, 10),
    amount: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get(`/vikoba/${id}`).then(setData).finally(() => setLoading(false));

  useEffect(() => { load(); }, [id]);

  const addMember = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/vikoba/${id}/members`, memberForm);
      setShowMember(false);
      setMemberForm({ full_name: '', phone: '' });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const addHisa = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/vikoba/${id}/hisa`, {
        ...hisaForm,
        amount: parseFloat(hisaForm.amount),
      });
      setShowHisa(false);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const markPaid = async (hisaId) => {
    await api.post(`/vikoba/${id}/hisa/${hisaId}/pay`, { paid_date: new Date().toISOString().slice(0, 10) });
    load();
  };

  if (loading) return <div className="loading"><span className="spinner" /> Loading…</div>;
  if (!data) return <div className="page"><p>Group not found</p></div>;

  const { group, members, hisa_payments, summary } = data;

  return (
    <div className="page">
      <Link to="/vikoba" style={{ fontSize: 13, color: 'var(--text-2)' }}>← Back to groups</Link>
      <h1 className="page-title" style={{ marginTop: 8 }}>{group.name}</h1>
      <p className="page-subtitle">{group.interval_type} hisa · {formatTZS(group.hisa_amount)}</p>

      <div className="stats-grid stats-grid-3">
        <div className="stat-card">
          <div className="stat-label">Members</div>
          <div className="stat-value">{summary.member_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Hisa Collected</div>
          <div className="stat-value">{formatTZS(summary.total_hisa_collected)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Penalties</div>
          <div className="stat-value">{formatTZS(summary.total_penalties)}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <button type="button" className="btn btn-secondary" onClick={() => setShowMember(true)}>+ Add Member</button>
        <button type="button" className="btn btn-primary" onClick={() => setShowHisa(true)}>+ Schedule Hisa</button>
      </div>

      <div className="section-divider"><h2>Members</h2><hr /></div>
      <div className="table-wrap" style={{ marginBottom: 24 }}>
        <table>
          <thead><tr><th>Name</th><th>Phone</th><th>Joined</th></tr></thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.id}>
                <td>{m.full_name}</td>
                <td>{m.phone || '—'}</td>
                <td>{formatDate(m.joined_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="section-divider"><h2>Hisa Payments</h2><hr /></div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Due Date</th><th>Amount</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {hisa_payments.map((h) => (
              <tr key={h.id}>
                <td>{formatDate(h.due_date)}</td>
                <td className="mono">{formatTZS(h.amount)}</td>
                <td><span className={`badge badge-${h.status === 'paid' ? 'green' : h.status === 'missed' ? 'red' : 'amber'}`}>{h.status}</span></td>
                <td>
                  {h.status === 'pending' && (
                    <button type="button" className="btn btn-sm btn-primary" onClick={() => markPaid(h.id)}>Mark Paid</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showMember && (
        <Modal title="Add Member" onClose={() => setShowMember(false)} footer={<button type="submit" form="member-form" className="btn btn-primary">Save</button>}>
          {error && <div className="alert alert-error">{error}</div>}
          <form id="member-form" onSubmit={addMember} className="form-grid">
            <div className="form-group">
              <label>Full Name</label>
              <input value={memberForm.full_name} onChange={(e) => setMemberForm({ ...memberForm, full_name: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input value={memberForm.phone} onChange={(e) => setMemberForm({ ...memberForm, phone: e.target.value })} />
            </div>
          </form>
        </Modal>
      )}

      {showHisa && (
        <Modal title="Schedule Hisa" onClose={() => setShowHisa(false)} footer={<button type="submit" form="hisa-form" className="btn btn-primary">Save</button>}>
          {error && <div className="alert alert-error">{error}</div>}
          <form id="hisa-form" onSubmit={addHisa} className="form-grid">
            <div className="form-group">
              <label>Member</label>
              <select value={hisaForm.member_id} onChange={(e) => setHisaForm({ ...hisaForm, member_id: e.target.value })} required>
                <option value="">Select member</option>
                {members.map((m) => <option key={m.id} value={m.id}>{m.full_name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Due Date</label>
              <input type="date" value={hisaForm.due_date} onChange={(e) => setHisaForm({ ...hisaForm, due_date: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Amount (TZS)</label>
              <input type="number" value={hisaForm.amount} onChange={(e) => setHisaForm({ ...hisaForm, amount: e.target.value })} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
