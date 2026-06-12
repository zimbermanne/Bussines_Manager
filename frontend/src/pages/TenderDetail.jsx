import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, formatTZS } from '../utils/api';
import Modal from '../components/Modal';

export default function TenderDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    item_name: '',
    quantity_needed: '',
    unit: '',
    estimated_unit_cost: '',
    status: 'pending',
    supplier_id: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([api.get(`/tenders/${id}`), api.get('/suppliers/')])
      .then(([t, s]) => { setData(t); setSuppliers(s); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id]);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/tenders/${id}/items`, {
        ...form,
        supplier_id: form.supplier_id || null,
        quantity_needed: parseFloat(form.quantity_needed),
        estimated_unit_cost: form.estimated_unit_cost ? parseFloat(form.estimated_unit_cost) : null,
      });
      setShowModal(false);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading"><span className="spinner" /> Loading…</div>;
  if (!data) return <div className="page"><p>Tender not found</p></div>;

  const { tender, procurement_items, summary } = data;

  return (
    <div className="page">
      <Link to="/tenders" style={{ fontSize: 13, color: 'var(--text-2)' }}>← Back to tenders</Link>
      <h1 className="page-title" style={{ marginTop: 8 }}>{tender.name}</h1>
      <p className="page-subtitle">{tender.client} · {tender.reference_number}</p>

      <div className="stats-grid stats-grid-4">
        <div className="stat-card">
          <div className="stat-label">Tender Value</div>
          <div className="stat-value">{formatTZS(tender.tender_value)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Estimated Cost</div>
          <div className="stat-value">{formatTZS(summary.total_estimated_cost)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Actual Spent</div>
          <div className="stat-value">{formatTZS(summary.total_actual_cost)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Budget Remaining</div>
          <div className="stat-value">{formatTZS(summary.budget_remaining)}</div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600 }}>Procurement Items ({summary.pending} pending)</h2>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Item</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th><th>Qty</th><th>Est. Cost</th><th>Actual</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {procurement_items.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No items yet</td></tr>
            ) : procurement_items.map((i) => (
              <tr key={i.id}>
                <td>{i.item_name}</td>
                <td className="mono">{i.quantity_needed} {i.unit}</td>
                <td className="mono">{formatTZS(i.estimated_unit_cost)}</td>
                <td className="mono">{formatTZS(i.actual_unit_cost)}</td>
                <td><span className={`badge badge-${i.status === 'delivered' ? 'green' : i.status === 'ordered' ? 'amber' : 'gray'}`}>{i.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Add Procurement Item"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="item-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="item-form" onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Item Name</label>
              <input value={form.item_name} onChange={set('item_name')} required />
            </div>
            <div className="form-group">
              <label>Quantity</label>
              <input type="number" step="0.01" value={form.quantity_needed} onChange={set('quantity_needed')} required />
            </div>
            <div className="form-group">
              <label>Unit</label>
              <input value={form.unit} onChange={set('unit')} placeholder="metres, pieces…" />
            </div>
            <div className="form-group">
              <label>Est. Unit Cost</label>
              <input type="number" value={form.estimated_unit_cost} onChange={set('estimated_unit_cost')} />
            </div>
            <div className="form-group">
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
