import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    company_name: '',
    full_name: '',
    email: '',
    password: '',
    tin: '',
    region: 'Kilimanjaro',
    district: 'Moshi',
  });
  const [error, setError] = useState('');

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <div className="card-body">
          <h1 className="page-title">Register Company</h1>
          <p className="page-subtitle">14-day free trial included</p>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Company name</label>
                <input value={form.company_name} onChange={update('company_name')} required />
              </div>
              <div className="form-group">
                <label>Your full name</label>
                <input value={form.full_name} onChange={update('full_name')} required />
              </div>
            </div>
            <div className="form-grid-2">
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={update('email')} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={form.password} onChange={update('password')} required minLength={6} />
              </div>
            </div>
            <div className="form-grid-3">
              <div className="form-group">
                <label>TIN (optional)</label>
                <input value={form.tin} onChange={update('tin')} />
              </div>
              <div className="form-group">
                <label>Region</label>
                <input value={form.region} onChange={update('region')} />
              </div>
              <div className="form-group">
                <label>District</label>
                <input value={form.district} onChange={update('district')} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          <p style={{ marginTop: 16, fontSize: 13, color: 'var(--text-2)' }}>
            Already registered? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
