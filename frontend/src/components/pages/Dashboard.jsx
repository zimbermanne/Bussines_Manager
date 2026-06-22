import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, formatTZS, formatDate, daysUntil } from '../utils/api';

function UrgencyBadge({ days }) {
  if (days < 0) return <span className="badge badge-red">OVERDUE</span>;
  if (days === 0) return <span className="badge badge-red">TODAY</span>;
  if (days <= 3)  return <span className="badge badge-red">{days}d left</span>;
  if (days <= 7)  return <span className="badge badge-amber">{days}d left</span>;
  return <span className="badge badge-green">{days}d left</span>;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/pnl/dashboard')
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading"><div className="spinner" />Loading dashboard…</div>;
  if (error)   return <div className="page"><div className="alert alert-error">{error}</div></div>;

  const { today, month, upcoming_deadlines, active_loans, recent_notifications } = data;

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Overview for {month?.period}</p>

      {/* Today */}
      <div className="section-divider"><h2>Today</h2><hr /></div>
      <div className="stats-grid stats-grid-4" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-label">Sales Today</div>
          <div className="stat-value positive">{formatTZS(today.sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Purchases</div>
          <div className="stat-value">{formatTZS(today.purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value">{formatTZS(today.expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Today</div>
          <div className={`stat-value ${today.net >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(today.net)}
          </div>
        </div>
      </div>

      {/* Month */}
      <div className="section-divider"><h2>{month.period}</h2><hr /></div>
      <div className="stats-grid stats-grid-4" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-label">Monthly Sales</div>
          <div className="stat-value positive">{formatTZS(month.sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Purchases</div>
          <div className="stat-value">{formatTZS(month.purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value">{formatTZS(month.expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Profit</div>
          <div className={`stat-value ${month.net >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(month.net)}
          </div>
          <div className="stat-sub">{month.net >= 0 ? '📈 Profitable' : '📉 Loss'}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Upcoming deadlines */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">📅 Upcoming Deadlines</span>
            <Link to="/deadlines" className="btn btn-secondary btn-sm">View all</Link>
          </div>
          <div style={{ padding: '0' }}>
            {upcoming_deadlines?.length === 0 && (
              <div className="empty" style={{ padding: 24 }}>
                <p>No deadlines in the next 30 days</p>
              </div>
            )}
            {upcoming_deadlines?.map(dl => (
              <div key={dl.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px 20px', borderBottom: '1px solid var(--border)',
              }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{dl.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{formatDate(dl.next_due_date)}</div>
                </div>
                <UrgencyBadge days={daysUntil(dl.next_due_date)} />
              </div>
            ))}
          </div>
        </div>

        {/* Recent notifications */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🔔 Recent Alerts</span>
            <Link to="/notifications" className="btn btn-secondary btn-sm">View all</Link>
          </div>
          <div>
            {recent_notifications?.length === 0 && (
              <div className="empty" style={{ padding: 24 }}><p>No recent alerts</p></div>
            )}
            {recent_notifications?.map(n => (
              <div key={n.id} style={{
                padding: '12px 20px', borderBottom: '1px solid var(--border)',
              }}>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{n.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-2)', marginTop: 2 }}>{n.message}</div>
                <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4 }}>
                  {formatDate(n.sent_at)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick links */}
      <div className="section-divider" style={{ marginTop: 28 }}><h2>Quick Actions</h2><hr /></div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Link to="/sales" className="btn btn-primary">+ Add Sale</Link>
        <Link to="/purchases" className="btn btn-secondary">+ Add Purchase</Link>
        <Link to="/expenses" className="btn btn-secondary">+ Add Expense</Link>
        <Link to="/loans" className="btn btn-secondary">🏦 {active_loans} Active Loans</Link>
        <Link to="/vikoba" className="btn btn-secondary">🤝 Vikoba Groups</Link>
      </div>
    </div>
  );
}