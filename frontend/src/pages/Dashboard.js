import { useEffect, useState } from 'react';
import { api, formatTZS } from '../utils/api';

export default function Dashboard() {
  const [daily, setDaily] = useState(null);
  const [monthly, setMonthly] = useState(null);
  const [deadlines, setDeadlines] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/pnl/daily'),
      api.get('/pnl/monthly'),
      api.get('/deadlines/'),
      api.get('/loans/'),
    ])
      .then(([d, m, dl, ln]) => {
        setDaily(d);
        setMonthly(m);
        setDeadlines(dl.slice(0, 5));
        setLoans(ln.slice(0, 5));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="page"><div className="loading"><span className="spinner" /> Loading dashboard…</div></div>;
  }

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Today&apos;s financial snapshot and upcoming alerts</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid stats-grid-4">
        <div className="stat-card">
          <div className="stat-label">Today&apos;s Sales</div>
          <div className="stat-value">{formatTZS(daily?.total_sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Today&apos;s Purchases</div>
          <div className="stat-value">{formatTZS(daily?.total_purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Today&apos;s Expenses</div>
          <div className="stat-value">{formatTZS(daily?.total_expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Today&apos;s Net Profit</div>
          <div className={`stat-value ${(daily?.net_profit ?? 0) >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(daily?.net_profit)}
          </div>
        </div>
      </div>

      <div className="stats-grid stats-grid-2">
        <div className="stat-card">
          <div className="stat-label">Monthly Net Profit</div>
          <div className={`stat-value ${(monthly?.net_profit ?? 0) >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(monthly?.net_profit)}
          </div>
          <div className="stat-sub">{monthly?.period}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Monthly Sales</div>
          <div className="stat-value">{formatTZS(monthly?.total_sales)}</div>
        </div>
      </div>

      <div className="section-divider"><h2>Upcoming Deadlines</h2><hr /></div>
      {deadlines.length === 0 ? (
        <div className="empty"><p>No deadlines yet. Add compliance reminders under Deadlines.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Category</th><th>Due Date</th></tr>
              </thead>
              <tbody>
                {deadlines.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{d.category}</td>
                    <td>{d.next_due_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="section-divider"><h2>Active Loans</h2><hr /></div>
      {loans.length === 0 ? (
        <div className="empty"><p>No bank loans recorded yet.</p></div>
      ) : (
        <div className="card">
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr><th>Lender</th><th>Balance</th><th>Due Day</th></tr>
              </thead>
              <tbody>
                {loans.map((l) => (
                  <tr key={l.id}>
                    <td>{l.lender_name}</td>
                    <td>{formatTZS(l.balance_remaining)}</td>
                    <td>{l.due_day}th of month</td>
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
