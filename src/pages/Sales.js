import { useEffect, useState } from 'react';
import { api, formatTZS, formatDate } from '../utils/api';

const emptyForm = { item_name: '', quantity: '', unit_price: '', notes: '' };

export default function Sales() {
  const [sales, setSales] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => api.get('/sales/').then(setSales).catch((e) => setError(e.message)).finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/sales/', {
        item_name: form.item_name,
        quantity: parseFloat(form.quantity),
        unit_price: parseFloat(form.unit_price),
        notes: form.notes || null,
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
      <h1 className="page-title">Sales</h1>
      <p className="page-subtitle">Record daily sales per item</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header"><span className="card-title">New Sale</span></div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Item name</label>
                <input value={form.item_name} onChange={(e) => setForm({ ...form, item_name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input type="number" step="0.01" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} required />
              </div>
            </div>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Unit price (TZS)</label>
                <input type="number" step="0.01" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Notes</label>
                <input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Record sale'}
            </button>
          </form>
        </div>
      </div>

      {loading ? (
        <div className="loading"><span className="spinner" /></div>
      ) : sales.length === 0 ? (
        <div className="empty"><p>No sales recorded yet.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Date</th><th>Item</th><th>Qty</th><th>Total</th></tr>
              </thead>
              <tbody>
                {sales.map((s) => (
                  <tr key={s.id}>
                    <td>{formatDate(s.sale_date)}</td>
                    <td>{s.item_name}</td>
                    <td>{s.quantity}</td>
                    <td>{formatTZS(s.total_amount)}</td>
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
