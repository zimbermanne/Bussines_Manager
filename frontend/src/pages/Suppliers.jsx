import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  name: '',
  contact_phone: '',
  contact_email: '',
  location: '',
  items_supplied: '',
  notes: '',
};

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get('/suppliers/').then(setSuppliers).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/suppliers/', form);
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
          <h1 className="page-title">Suppliers</h1>
          <p className="page-subtitle">Supplier directory for purchases and tenders</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Supplier</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th><th>Phone</th><th>Location</th><th>Items</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.length === 0 ? (
              <tr><td colSpan={4} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No suppliers yet</td></tr>
            ) : suppliers.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.contact_phone || '—'}</td>
                <td>{s.location || '—'}</td>
                <td>{s.items_supplied || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Supplier"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="supplier-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="supplier-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Name</label>
              <input value={form.name} onChange={set('name')} required />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input value={form.contact_phone} onChange={set('contact_phone')} />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.contact_email} onChange={set('contact_email')} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Location</label>
              <input value={form.location} onChange={set('location')} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Items Supplied</label>
              <textarea value={form.items_supplied} onChange={set('items_supplied')} />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
