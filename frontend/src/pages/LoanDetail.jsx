import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, formatTZS, formatDate } from '../utils/api';
import Modal from '../components/Modal';

export default function LoanDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [payment, setPayment] = useState({
    payment_date: new Date().toISOString().slice(0, 10),
    amount_paid: '',
    notes: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = () => api.get(`/loans/${id}`).then(setData).finally(() => setLoading(false));

  useEffect(() => { load(); }, [id]);

  const handlePayment = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post(`/loans/${id}/payments`, {
        ...payment,
        amount_paid: parseFloat(payment.amount_paid),
      });
      setShowModal(false);
      setPayment({ payment_date: new Date().toISOString().slice(0, 10), amount_paid: '', notes: '' });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading"><span className="spinner" /> Loading…</div>;
  if (!data) return <div className="page"><p>Loan not found</p></div>;

  const { loan, payments, balance_remaining } = data;

  return (
    <div className="page">
      <Link to="/loans" style={{ fontSize: 13, color: 'var(--text-2)' }}>← Back to loans</Link>
      <h1 className="page-title" style={{ marginTop: 8 }}>{loan.lender_name}</h1>
      <p className="page-subtitle">{loan.interest_type} · {loan.interest_rate}% annual</p>

      <div className="stats-grid stats-grid-3">
        <div className="stat-card">
          <div className="stat-label">Balance Remaining</div>
          <div className="stat-value">{formatTZS(balance_remaining)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Interest Paid</div>
          <div className="stat-value">{formatTZS(data.total_interest_paid)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Principal Paid</div>
          <div className="stat-value">{formatTZS(data.total_principal_paid)}</div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600 }}>Payment History</h2>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>Log Payment</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th><th>Amount</th><th>Interest</th><th>Principal</th><th>Balance After</th>
            </tr>
          </thead>
          <tbody>
            {payments.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>No payments yet</td></tr>
            ) : payments.map((p) => (
              <tr key={p.id}>
                <td>{formatDate(p.payment_date)}</td>
                <td className="mono">{formatTZS(p.amount_paid)}</td>
                <td className="mono">{formatTZS(p.interest_portion)}</td>
                <td className="mono">{formatTZS(p.principal_portion)}</td>
                <td className="mono">{formatTZS(p.balance_after)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal
          title="Log Payment"
          onClose={() => setShowModal(false)}
          footer={<button type="submit" form="payment-form" className="btn btn-primary">Save</button>}
        >
          {error && <div className="alert alert-error">{error}</div>}
          <form id="payment-form" onSubmit={handlePayment} className="form-grid">
            <div className="form-group">
              <label>Payment Date</label>
              <input type="date" value={payment.payment_date} onChange={(e) => setPayment({ ...payment, payment_date: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Amount Paid (TZS)</label>
              <input type="number" value={payment.amount_paid} onChange={(e) => setPayment({ ...payment, amount_paid: e.target.value })} required />
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
