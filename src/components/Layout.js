import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV = [
  { section: 'Overview', links: [
    { to: '/', label: 'Dashboard', icon: '📊' },
    { to: '/profit-loss', label: 'Profit & Loss', icon: '💰' },
  ]},
  { section: 'Finance', links: [
    { to: '/sales', label: 'Sales', icon: '�' },
    { to: '/purchases', label: 'Purchases', icon: '📦' },
    { to: '/expenses', label: 'Expenses', icon: '💸' },
  ]},
  { section: 'Operations', links: [
    { to: '/loans', label: 'Bank Loans', icon: '🏦' },
    { to: '/vikoba', label: 'Vikoba', icon: '�' },
    { to: '/tenders', label: 'Tenders', icon: '�' },
    { to: '/suppliers', label: 'Suppliers', icon: '🚛' },
    { to: '/deadlines', label: 'Deadlines', icon: '📅' },
  ]},
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getInitials = (name) => {
    if (!name) return 'ZE';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Company Manager</h2>
          <p>Business control panel</p>
        </div>
        <nav className="sidebar-menu">
          {NAV.map((group) => (
            <div key={group.section} className="menu-group">
              <h3>{group.section}</h3>
              {group.links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  className={({ isActive }) => `menu-item${isActive ? ' active' : ''}`}
                >
                  <span className="icon">{link.icon}</span>
                  {link.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar">{getInitials(user?.full_name)}</div>
            <span className="username">{user?.full_name || 'User'}</span>
          </div>
          <button className="btn-signout" onClick={handleLogout}>Sign out</button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
