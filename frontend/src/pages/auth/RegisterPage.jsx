import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, Building2, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '../../services/api';
import '../../styles/auth.css';

const ROLES = [
  { value: 'HR_ADMIN', label: 'HR Admin', desc: 'Manage employees & onboarding' },
  { value: 'MANAGER', label: 'Manager', desc: 'Oversee team onboarding' },
  { value: 'EMPLOYEE', label: 'Employee', desc: 'Personal onboarding dashboard' },
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', confirm_password: '',
    role: 'EMPLOYEE', organization_name: '',
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.full_name.trim()) e.full_name = 'Full name is required';
    if (!form.email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Enter a valid email';
    if (!form.password) e.password = 'Password is required';
    else if (form.password.length < 8) e.password = 'Minimum 8 characters';
    if (form.password !== form.confirm_password) e.confirm_password = 'Passwords do not match';
    if (form.role === 'SUPER_ADMIN' && !form.organization_name.trim())
      e.organization_name = 'Organization name is required for Super Admin';
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    const fieldErrors = validate();
    if (Object.keys(fieldErrors).length) { setErrors(fieldErrors); return; }
    setErrors({});
    setLoading(true);
    try {
      await api.post('/auth/register', {
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        role: form.role,
        organization_name: form.organization_name || undefined,
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => {
    setForm(f => ({ ...f, [field]: e.target.value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: '' }));
  };

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card" style={{ textAlign: 'center' }}>
          <CheckCircle size={48} color="var(--color-teal)" style={{ margin: '0 auto 16px' }} />
          <div className="auth-title">Account created!</div>
          <p className="auth-subtitle">Redirecting you to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-text">Onboard<span>X</span></div>
          <div className="auth-logo-sub">Employee Onboarding Platform</div>
        </div>

        <h2 className="auth-title">Create your account</h2>
        <p className="auth-subtitle">Get started with OnboardX today</p>

        {apiError && (
          <div className="auth-error">
            <AlertCircle size={14} style={{ marginRight: 6, flexShrink: 0 }} />
            {apiError}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" size={15} />
              <input className={`form-input input-with-icon${errors.full_name ? ' input-error' : ''}`}
                type="text" placeholder="John Smith" value={form.full_name} onChange={set('full_name')} />
            </div>
            {errors.full_name && <span className="field-error">{errors.full_name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Email address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={15} />
              <input className={`form-input input-with-icon${errors.email ? ' input-error' : ''}`}
                type="email" placeholder="you@company.com" value={form.email} onChange={set('email')} />
            </div>
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Role</label>
            <div className="role-selector">
              {ROLES.map(r => (
                <label key={r.value} className={`role-option${form.role === r.value ? ' selected' : ''}`}>
                  <input type="radio" name="role" value={r.value}
                    checked={form.role === r.value} onChange={set('role')} />
                  <div>
                    <div className="role-label">{r.label}</div>
                    <div className="role-desc">{r.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {form.role === 'SUPER_ADMIN' && (
            <div className="form-group">
              <label className="form-label">Organization Name</label>
              <div className="input-wrapper">
                <Building2 className="input-icon" size={15} />
                <input className={`form-input input-with-icon${errors.organization_name ? ' input-error' : ''}`}
                  type="text" placeholder="Acme Corp" value={form.organization_name}
                  onChange={set('organization_name')} />
              </div>
              {errors.organization_name && <span className="field-error">{errors.organization_name}</span>}
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={15} />
              <input className={`form-input input-with-icon input-with-right-icon${errors.password ? ' input-error' : ''}`}
                type={showPassword ? 'text' : 'password'} placeholder="Min. 8 characters"
                value={form.password} onChange={set('password')} />
              <button type="button" className="input-right-icon" onClick={() => setShowPassword(v => !v)} tabIndex={-1}>
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={15} />
              <input className={`form-input input-with-icon${errors.confirm_password ? ' input-error' : ''}`}
                type="password" placeholder="••••••••"
                value={form.confirm_password} onChange={set('confirm_password')} />
            </div>
            {errors.confirm_password && <span className="field-error">{errors.confirm_password}</span>}
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
