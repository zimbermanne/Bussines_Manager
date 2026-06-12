import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV = [
  { section: 'Overview', links: [
    { to: '/', label: 'Dashboard', icon: '📊' },
  ]},
  { section: 'Finance', links: [
    { to: '/sales', label: 'Sales', icon: '🛒' },
    { to: '/loans', label: 'Bank Loans', icon: '🏦' },
  ]},
  { section: 'Operations', links: [
    { to: '/deadlines', label: 'Deadlines', icon: '📅' },
    { to: '/tenders', label: 'Tenders', icon: '📋' },
    { to: '/suppliers', label: 'Suppliers', icon: '🚛' },
  ]},
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    // Changed "app-layout" to "app-shell" to link properly with index.css
    <div className="app-shell"> 
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>Company Manager</h1>
          <p>Business Control</p>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((group) => (
            <div key={group.section}>
              <div className="nav-section">{group.section}</div>
              {group.links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                >
                  <span className="icon">{link.icon}</span>
                  {link.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div style={{ fontWeight: '600', marginBottom: '4px' }}>{user?.full_name}</div>
          <button type="button" onClick={handleLogout}>Sign out</button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}