import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const NAV = [
  { section: 'Overview' },
  { to: '/',           label: 'Dashboard',   icon: '📊' },
  { to: '/pnl',        label: 'Profit & Loss', icon: '📈' },
  { to: '/notifications', label: 'Alerts',   icon: '🔔' },

  { section: 'Finance' },
  { to: '/sales',      label: 'Sales',       icon: '🛒' },
  { to: '/purchases',  label: 'Purchases',   icon: '📦' },
  { to: '/expenses',   label: 'Expenses',    icon: '💸' },

  { section: 'Finance & Savings' },
  { to: '/loans',      label: 'Bank Loans',  icon: '🏦' },
  { to: '/vikoba',     label: 'Vikoba',      icon: '🤝' },

  { section: 'Operations' },
  { to: '/tenders',    label: 'Tenders',     icon: '📋' },
  { to: '/suppliers',  label: 'Suppliers',   icon: '🏪' },
  { to: '/deadlines',  label: 'Deadlines',   icon: '📅' },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>Company Manager</h1>
          <p>Zimbermanne Co. Ltd</p>
        </div>

        <nav className="sidebar-nav">
          {NAV.map((item, i) =>
            item.section ? (
              <div key={i} className="nav-section">{item.section}</div>
            ) : (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                <span className="icon">{item.icon}</span>
                {item.label}
              </NavLink>
            )
          )}
        </nav>

        <div className="sidebar-footer">
          <div>{user?.full_name}</div>
          <button onClick={logout}>Sign out</button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}