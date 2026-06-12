import React, { useEffect, useState } from 'react';
import { api, formatTZS } from '../utils/api';

export default function ProfitLoss() {
  const [daily, setDaily] = useState(null);
  const [monthly, setMonthly] = useState(null);
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/pnl/daily?target_date=${date}`),
      api.get('/pnl/monthly'),
    ])
      .then(([d, m]) => { setDaily(d); setMonthly(m); })
      .finally(() => setLoading(false));
  }, [date]);

  if (loading) return <div className="loading"><span className="spinner" /> Loading…</div>;

  return (
    <div className="page">
      <h1 className="page-title">Profit & Loss</h1>
      <p className="page-subtitle">Daily and monthly financial summary</p>

      <div className="form-group" style={{ maxWidth: 200, marginBottom: 24 }}>
        <label>Daily view date</label>
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      </div>

      <div className="section-divider"><h2>Daily P&amp;L — {daily?.date}</h2><hr /></div>
      <div className="stats-grid stats-grid-4">
        <div className="stat-card">
          <div className="stat-label">Sales Revenue</div>
          <div className="stat-value">{formatTZS(daily?.total_sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Purchases</div>
          <div className="stat-value">{formatTZS(daily?.total_purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value">{formatTZS(daily?.total_expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Net Profit</div>
          <div className={`stat-value ${daily?.net_profit >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(daily?.net_profit)}
          </div>
        </div>
      </div>

      <div className="section-divider"><h2>Monthly P&amp;L — {monthly?.period}</h2><hr /></div>
      <div className="stats-grid stats-grid-4">
        <div className="stat-card">
          <div className="stat-label">Total Sales</div>
          <div className="stat-value">{formatTZS(monthly?.total_sales)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Purchases</div>
          <div className="stat-value">{formatTZS(monthly?.total_purchases)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Expenses</div>
          <div className="stat-value">{formatTZS(monthly?.total_expenses)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Monthly Net</div>
          <div className={`stat-value ${monthly?.net_profit >= 0 ? 'positive' : 'negative'}`}>
            {formatTZS(monthly?.net_profit)}
          </div>
        </div>
      </div>
    </div>
  );
}
