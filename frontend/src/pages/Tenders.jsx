import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  name: '',
  reference_number: '',
  client: '',
  tender_value: '',
  procurement_budget: '',
  delivery_deadline: '',
  status: 'planning',
  notes: '',
};

export default function Tenders() {
  const [tenders, setTenders] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get('/tenders/').then(setTenders).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/tenders/', {
        ...form,
        tender_value: form.tender_value ? parseFloat(form.tender_value) : null,
        procurement_budget: form.procurement_budget ? parseFloat(form.procurement_budget) : null,
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
          <h1 className="page-title">Tenders</h1>
          <p className="page-subtitle">Procurement planning for projects</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Tender</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th><th>Client</th><th>Value</th><th>Delivery</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            {tenders.length === 0 ? (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No tenders yet</td></tr>
            ) : tenders.map((t) => (
              <tr key={t.id}>
                <td>{t.name}</td>
                <td>{t.client || '—'}</td>
                <td className="mono">{formatTZS(t.tender_value)}</td>
                <td>{formatDate(t.delivery_deadline)}</td>
                <td><span className="badge badge-blue">{t.status}</span></td>
                <td><Link to={`/tenders/${t.id}`} className="btn btn-sm btn-secondary">Details</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Tender"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="tender-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="tender-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Tender Name</label>
              <input value={form.name} onChange={set('name')} required />
            </div>
            <div className="form-group">
              <label>Reference Number</label>
              <input value={form.reference_number} onChange={set('reference_number')} />
            </div>
            <div className="form-group">
              <label>Client</label>
              <input value={form.client} onChange={set('client')} />
            </div>
            <div className="form-group">
              <label>Tender Value (TZS)</label>
              <input type="number" value={form.tender_value} onChange={set('tender_value')} />
            </div>
            <div className="form-group">
              <label>Procurement Budget (TZS)</label>
              <input type="number" value={form.procurement_budget} onChange={set('procurement_budget')} />
            </div>
            <div className="form-group">
              <label>Delivery Deadline</label>
              <input type="date" value={form.delivery_deadline} onChange={set('delivery_deadline')} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
