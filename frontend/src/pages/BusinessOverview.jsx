import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, formatTZS, formatDate, daysUntil } from '../utils/api';

export default function BusinessOverview() {
  const [pnl, setPnl] = useState(null);
  const [deadlines, setDeadlines] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/pnl/daily'),
      api.get('/deadlines/'),
      api.get('/loans/'),
    ])
      .then(([p, d, l]) => {
        setPnl(p);
        setDeadlines(d.slice(0, 5));
        setLoans(l.slice(0, 3));
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading"><span className="spinner" /> Loading dashboard…</div>;

  return (
    <div className="page">
      <h1 className="page-title">Business Overview</h1>
      <p className="page-subtitle">Today&apos;s overview and upcoming alerts</p>

      <div className="stats-grid stats-grid-4">
        <div className="stat-card">
          <div className="stat-label">Today&apos;s Sales</div>
          <div className="stat-value">{formatTZS(pnl?.total_sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Purchases</div>
          <div className="stat-value">{formatTZS(pnl?.total_purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value">{formatTZS(pnl?.total_expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Profit</div>
          <div className={`stat-value ${pnl?.net_profit >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(pnl?.net_profit)}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Upcoming Deadlines</span>
            <Link to="/deadlines" className="btn btn-sm btn-secondary">View all</Link>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {deadlines.length === 0 ? (
              <div className="empty"><p>No deadlines yet</p></div>
            ) : (
              <table>
                <tbody>
                  {deadlines.map((d) => {
                    const days = daysUntil(d.next_due_date);
                    const cls = days <= 1 ? 'urgency-high' : days <= 7 ? 'urgency-mid' : 'urgency-low';
                    return (
                      <tr key={d.id}>
                        <td>{d.name}</td>
                        <td>{formatDate(d.next_due_date)}</td>
                        <td className={cls}>{days}d</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Active Loans</span>
            <Link to="/loans" className="btn btn-sm btn-secondary">View all</Link>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {loans.length === 0 ? (
              <div className="empty"><p>No active loans</p></div>
            ) : (
              <table>
                <tbody>
                  {loans.map((l) => (
                    <tr key={l.id}>
                      <td>{l.lender_name}</td>
                      <td className="mono">{formatTZS(l.balance_remaining)}</td>
                      <td>Due day {l.due_day}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
