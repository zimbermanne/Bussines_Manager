import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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
    return <div className="loading"><span className="spinner" /> Loading dashboard…</div>;
  }

  return (
    <>
      <header className="content-header">
        <h1>Dashboard</h1>
        <p>Today's overview and upcoming alerts</p>
      </header>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="metrics-grid">
        <div className="card metric-card">
          <span className="card-label">Today's Sales</span>
          <span className="card-value">{formatTZS(daily?.total_sales)} <span className="currency">TZS</span></span>
        </div>
        <div className="card metric-card">
          <span className="card-label">Purchases</span>
          <span className="card-value">{formatTZS(daily?.total_purchases)} <span className="currency">TZS</span></span>
        </div>
        <div className="card metric-card">
          <span className="card-label">Expenses</span>
          <span className="card-value">{formatTZS(daily?.total_expenses)} <span className="currency">TZS</span></span>
        </div>
        <div className={`card metric-card profit ${(daily?.net_profit ?? 0) >= 0 ? '' : 'negative'}`}>
          <span className="card-label">Net Profit</span>
          <span className="card-value">{formatTZS(daily?.net_profit)} <span className="currency">TZS</span></span>
        </div>
      </div>

      <div className="data-split-row">
        <div className="card data-panel">
          <div className="panel-header">
            <h3>Upcoming Deadlines</h3>
            <Link to="/deadlines" className="view-all">View all</Link>
          </div>
          {deadlines.length === 0 ? (
            <div className="panel-empty-state">
              <p>No deadlines yet</p>
            </div>
          ) : (
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
          )}
        </div>

        <div className="card data-panel">
          <div className="panel-header">
            <h3>Active Loans</h3>
            <Link to="/loans" className="view-all">View all</Link>
          </div>
          {loans.length === 0 ? (
            <div className="panel-empty-state">
              <p>No active loans</p>
            </div>
          ) : (
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
          )}
        </div>
      </div>
    </>
  );
}
