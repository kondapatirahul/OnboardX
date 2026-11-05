import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User } from 'lucide-react';
import { api } from '../../services/api';
import '../../styles/auth.css';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm_password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/register', {
        full_name: form.full_name,
        email: form.email,
        password: form.password,
      });
      navigate('/login');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-text">Onboard<span>X</span></div>
          <div className="auth-logo-sub">Employee Onboarding Platform</div>
        </div>

        <div className="auth-title">Create account</div>
        <div className="auth-subtitle">Get started with OnboardX</div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" />
              <input className="form-input input-with-icon" type="text" placeholder="John Smith"
                value={form.full_name} onChange={set('full_name')} required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <div className="input-wrapper">
              <Mail className="input-icon" />
              <input className="form-input input-with-icon" type="email" placeholder="you@company.com"
                value={form.email} onChange={set('email')} required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" />
              <input className="form-input input-with-icon" type="password" placeholder="••••••••"
                value={form.password} onChange={set('password')} required minLength={8} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" />
              <input className="form-input input-with-icon" type="password" placeholder="••••••••"
                value={form.confirm_password} onChange={set('confirm_password')} required />
            </div>
          </div>

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
