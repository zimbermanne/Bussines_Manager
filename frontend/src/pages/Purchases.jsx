import React, { useEffect, useState } from 'react';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  business_unit_id: '',
  supplier_id: '',
  purchase_date: new Date().toISOString().slice(0, 10),
  item_name: '',
  quantity: '',
  unit_cost: '',
  notes: '',
};

export default function Purchases() {
  const [purchases, setPurchases] = useState([]);
  const [units, setUnits] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([
      api.get('/purchases/'),
      api.get('/business-units/'),
      api.get('/suppliers/'),
    ])
      .then(([p, u, s]) => { setPurchases(p); setUnits(u); setSuppliers(s); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/purchases/', {
        ...form,
        business_unit_id: form.business_unit_id || null,
        supplier_id: form.supplier_id || null,
        quantity: parseFloat(form.quantity),
        unit_cost: parseFloat(form.unit_cost),
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
          <h1 className="page-title">Purchases</h1>
          <p className="page-subtitle">Stock purchases per item</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Record Purchase</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th><th>Item</th><th>Qty</th><th>Unit Cost</th><th>Total</th>
            </tr>
          </thead>
          <tbody>
            {purchases.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No purchases yet</td></tr>
            ) : purchases.map((p) => (
              <tr key={p.id}>
                <td>{formatDate(p.purchase_date)}</td>
                <td>{p.item_name}</td>
                <td className="mono">{p.quantity}</td>
                <td className="mono">{formatTZS(p.unit_cost)}</td>
                <td className="mono">{formatTZS(p.total_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Record Purchase"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="purchase-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="purchase-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={form.purchase_date} onChange={set('purchase_date')} required />
            </div>
            <div className="form-group">
              <label>Business Unit</label>
              <select value={form.business_unit_id} onChange={set('business_unit_id')}>
                <option value="">— None —</option>
                {units.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Item Name</label>
              <input value={form.item_name} onChange={set('item_name')} required />
            </div>
            <div className="form-group">
              <label>Quantity</label>
              <input type="number" step="0.01" value={form.quantity} onChange={set('quantity')} required />
            </div>
            <div className="form-group">
              <label>Unit Cost (TZS)</label>
              <input type="number" step="0.01" value={form.unit_cost} onChange={set('unit_cost')} required />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Supplier</label>
              <select value={form.supplier_id} onChange={set('supplier_id')}>
                <option value="">— None —</option>
                {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
