import { useEffect, useState } from 'react';
import { api, formatTZS } from '../utils/api';

export default function Tenders() {
  const [tenders, setTenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/tenders/')
      .then(setTenders)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Tenders</h1>
      <p className="page-subtitle">Procurement planning for upcoming projects</p>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <div className="loading"><span className="spinner" /></div>
      ) : tenders.length === 0 ? (
        <div className="empty"><p>No tenders yet. Use the API or add a create form here next.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Client</th><th>Value</th><th>Delivery</th><th>Status</th></tr>
              </thead>
              <tbody>
                {tenders.map((t) => (
                  <tr key={t.id}>
                    <td>{t.name}</td>
                    <td>{t.client || '—'}</td>
                    <td>{formatTZS(t.tender_value)}</td>
                    <td>{t.delivery_deadline}</td>
                    <td>{t.status}</td>
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
