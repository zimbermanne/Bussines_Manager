import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV = [
  { section: 'Overview', items: [
    { to: '/overview', label: 'Business Overview', icon: '📊' },
    { to: '/profit-loss', label: 'Profit & Loss', icon: '💰' },
  ]},
  { section: 'Finance', items: [
    { to: '/sales', label: 'Sales', icon: '🛒' },
    { to: '/purchases', label: 'Purchases', icon: '📦' },
    { to: '/expenses', label: 'Expenses', icon: '💸' },
  ]},
  { section: 'Operations', items: [
    { to: '/loans', label: 'Bank Loans', icon: '🏦' },
    { to: '/vikoba', label: 'Vikoba', icon: '👥' },
    { to: '/tenders', label: 'Tenders', icon: '📋' },
    { to: '/suppliers', label: 'Suppliers', icon: '🏭' },
    { to: '/deadlines', label: 'Deadlines', icon: '📅' },
  ]},
];

export default function Layout() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  const isDashboard = pathname === '/';

  if (isDashboard) {
    return <Outlet />;
  }

  return (
    <div className="app-shell">
      <aside className="nav-sidebar">
        <div className="sidebar-logo">
          <h1>Company Manager</h1>
          <p>Business control panel</p>
        </div>
        <nav className="sidebar-nav">
          <div>
            <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
              <span className="icon">⚡</span>
              Agent Dashboard
            </NavLink>
          </div>
          {NAV.map((group) => (
            <div key={group.section}>
              <div className="nav-section">{group.section}</div>
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/overview'}
                  className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                >
                  <span className="icon">{item.icon}</span>
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div>{user?.full_name}</div>
          <button type="button" onClick={logout}>Sign out</button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
