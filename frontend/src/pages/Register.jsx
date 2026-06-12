import React, { useState } from 'react';
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

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--green-800)', padding: 20 }}>
      <div className="card" style={{ width: '100%', maxWidth: 520 }}>
        <div className="card-body">
          <h1 className="page-title">Register Company</h1>
          <p className="page-subtitle">14-day free trial — all modules included</p>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit} className="form-grid form-grid-2">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Company Name</label>
              <input value={form.company_name} onChange={set('company_name')} required />
            </div>
            <div className="form-group">
              <label>Your Full Name</label>
              <input value={form.full_name} onChange={set('full_name')} required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={set('email')} required />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={set('password')} required minLength={6} />
            </div>
            <div className="form-group">
              <label>TIN (optional)</label>
              <input value={form.tin} onChange={set('tin')} />
            </div>
            <div className="form-group">
              <label>Region</label>
              <input value={form.region} onChange={set('region')} />
            </div>
            <div className="form-group">
              <label>District</label>
              <input value={form.district} onChange={set('district')} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ gridColumn: '1 / -1' }} disabled={loading}>
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
