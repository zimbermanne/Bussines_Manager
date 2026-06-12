import React, { useEffect, useState } from 'react';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

const emptyForm = {
  business_unit_id: '',
  sale_date: new Date().toISOString().slice(0, 10),
  item_name: '',
  quantity: '',
  unit_price: '',
  notes: '',
};

export default function Sales() {
  const [sales, setSales] = useState([]);
  const [units, setUnits] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([api.get('/sales/'), api.get('/business-units/')])
      .then(([s, u]) => { setSales(s); setUnits(u); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/sales/', {
        ...form,
        business_unit_id: form.business_unit_id || null,
        quantity: parseFloat(form.quantity),
        unit_price: parseFloat(form.unit_price),
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
          <h1 className="page-title">Sales</h1>
          <p className="page-subtitle">Record daily sales per item</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Record Sale</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th><th>Item</th><th>Qty</th><th>Unit Price</th><th>Total</th>
            </tr>
          </thead>
          <tbody>
            {sales.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No sales recorded yet</td></tr>
            ) : sales.map((s) => (
              <tr key={s.id}>
                <td>{formatDate(s.sale_date)}</td>
                <td>{s.item_name}</td>
                <td className="mono">{s.quantity}</td>
                <td className="mono">{formatTZS(s.unit_price)}</td>
                <td className="mono">{formatTZS(s.total_amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Record Sale"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="sale-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="sale-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={form.sale_date} onChange={set('sale_date')} required />
            </div>
            <div className="form-group">
              <label>Business Unit</label>
              <select value={form.business_unit_id} onChange={set('business_unit_id')}>
                <option value="">— All / None —</option>
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
              <label>Unit Price (TZS)</label>
              <input type="number" step="0.01" value={form.unit_price} onChange={set('unit_price')} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
