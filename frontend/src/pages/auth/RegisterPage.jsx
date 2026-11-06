import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Mail, Lock, User, Eye, EyeOff, Building2, AlertCircle, CheckCircle,
  Wifi, WifiOff, Copy, ShieldCheck, KeyRound,
} from 'lucide-react';
import { api } from '../../services/api';
import '../../styles/auth.css';

const ROLES = [
  { value: 'HR_ADMIN', label: 'HR Admin', desc: 'Create and manage your organization' },
  { value: 'EMPLOYEE', label: 'Employee', desc: 'Join your company onboarding workspace' },
];

function passwordScore(password) {
  if (!password) return 0;
  let score = 0;
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  return score;
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', confirm_password: '',
    role: 'HR_ADMIN', organization_name: '', organization_code: '',
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [connection, setConnection] = useState({ state: 'checking', message: 'Checking API connection…' });
  const [organization, setOrganization] = useState(null);
  const [checkingOrganization, setCheckingOrganization] = useState(false);

  useEffect(() => {
    let active = true;
    api.checkConnection()
      .then((health) => {
        if (!active) return;
        if (health.database === 'connected') {
          setConnection({ state: 'online', message: 'API and database connected' });
        } else {
          setConnection({ state: 'degraded', message: 'API online, database unavailable' });
        }
      })
      .catch((error) => {
        if (active) setConnection({ state: 'offline', message: error.message });
      });
    return () => { active = false; };
  }, []);

  const strength = useMemo(() => passwordScore(form.password), [form.password]);
  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Excellent'][strength];

  const validate = () => {
    const next = {};
    if (form.full_name.trim().length < 2) next.full_name = 'Enter your full name';
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) next.email = 'Enter a valid email address';
    if (form.password.length < 8) next.password = 'Use at least 8 characters';
    if (form.password.length > 72) next.password = 'Password must be 72 characters or fewer';
    if (form.password !== form.confirm_password) next.confirm_password = 'Passwords do not match';
    if (form.role === 'HR_ADMIN' && form.organization_name.trim().length < 2) {
      next.organization_name = 'Enter your organization name';
    }
    if (form.role !== 'HR_ADMIN' && !form.organization_code.trim()) {
      next.organization_code = 'Enter the signup code shared by your HR team';
    }
    return next;
  };

  const updateField = (field) => (event) => {
    const value = event.target.value;
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: '' }));
    if (field === 'organization_code') setOrganization(null);
    setApiError('');
  };

  const verifyOrganization = async () => {
    if (!form.organization_code.trim()) {
      setErrors((current) => ({ ...current, organization_code: 'Enter an organization code first' }));
      return;
    }
    setCheckingOrganization(true);
    setOrganization(null);
    setApiError('');
    try {
      const result = await api.resolveOrganization(form.organization_code.trim());
      setOrganization(result);
      setErrors((current) => ({ ...current, organization_code: '' }));
    } catch (error) {
      setErrors((current) => ({ ...current, organization_code: error.message }));
    } finally {
      setCheckingOrganization(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setApiError('');
    const fieldErrors = validate();
    setErrors(fieldErrors);
    if (Object.keys(fieldErrors).length) return;
    if (connection.state === 'offline') {
      setApiError('The API is offline. Start the backend and try again.');
      return;
    }
    if (form.role !== 'HR_ADMIN' && !organization) {
      setApiError('Verify your organization code before creating the account.');
      return;
    }

    setLoading(true);
    try {
      const result = await api.post('/auth/register', {
        full_name: form.full_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        role: form.role,
        organization_name: form.role === 'HR_ADMIN' ? form.organization_name.trim() : undefined,
        organization_code: form.role !== 'HR_ADMIN' ? form.organization_code.trim() : undefined,
      });
      setSuccess(result);
    } catch (error) {
      setApiError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card auth-success-card">
          <CheckCircle size={48} color="var(--color-teal)" className="auth-success-icon" />
          <h2 className="auth-title">Account created!</h2>
          <p className="auth-subtitle">Your OnboardX account is ready. Sign in to continue.</p>
          {success.organization_code && (
            <div className="organization-code-result">
              <div className="organization-code-heading"><KeyRound size={16} /> Organization signup code</div>
              <strong>{success.organization_code}</strong>
              <button type="button" className="auth-copy-button" onClick={() => navigator.clipboard?.writeText(success.organization_code)}>
                <Copy size={14} /> Copy code
              </button>
              <p>Share this code with your managers and employees so they can join your organization.</p>
            </div>
          )}
          <button className="auth-submit" type="button" onClick={() => navigate('/login')}>Continue to sign in</button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card auth-register-card">
        <div className="auth-logo">
          <div className="auth-logo-text">Onboard<span>X</span></div>
          <div className="auth-logo-sub">Employee Onboarding Platform</div>
        </div>

        <div className={`api-connection api-${connection.state}`} role="status">
          {connection.state === 'offline' ? <WifiOff size={14} /> : <Wifi size={14} />}
          <span>{connection.message}</span>
          {connection.state === 'offline' && <button type="button" onClick={() => window.location.reload()}>Retry</button>}
        </div>

        <h2 className="auth-title">Create your account</h2>
        <p className="auth-subtitle">Set up your workspace or join your organization</p>

        {apiError && (
          <div className="auth-error" role="alert">
            <AlertCircle size={14} style={{ marginRight: 6, flexShrink: 0 }} />
            {apiError}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="register-name">Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" size={15} />
              <input id="register-name" className={`form-input input-with-icon${errors.full_name ? ' input-error' : ''}`}
                type="text" placeholder="John Smith" value={form.full_name} onChange={updateField('full_name')} autoComplete="name" />
            </div>
            {errors.full_name && <span className="field-error">{errors.full_name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="register-email">Email address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={15} />
              <input id="register-email" className={`form-input input-with-icon${errors.email ? ' input-error' : ''}`}
                type="email" placeholder="you@company.com" value={form.email} onChange={updateField('email')} autoComplete="email" />
            </div>
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Account type</label>
            <div className="role-selector">
              {ROLES.map((role) => (
                <label key={role.value} className={`role-option${form.role === role.value ? ' selected' : ''}`}>
                  <input type="radio" name="role" value={role.value} checked={form.role === role.value}
                    onChange={(event) => { updateField('role')(event); setOrganization(null); }} />
                  <div><div className="role-label">{role.label}</div><div className="role-desc">{role.desc}</div></div>
                </label>
              ))}
            </div>
          </div>

          {form.role === 'HR_ADMIN' ? (
            <div className="form-group">
              <label className="form-label" htmlFor="organization-name">Organization name</label>
              <div className="input-wrapper">
                <Building2 className="input-icon" size={15} />
                <input id="organization-name" className={`form-input input-with-icon${errors.organization_name ? ' input-error' : ''}`}
                  type="text" placeholder="Acme Corporation" value={form.organization_name} onChange={updateField('organization_name')} />
              </div>
              {errors.organization_name && <span className="field-error">{errors.organization_name}</span>}
              <span className="field-hint">A unique signup code will be generated after registration.</span>
            </div>
          ) : (
            <div className="form-group">
              <label className="form-label" htmlFor="organization-code">Organization signup code</label>
              <div className="organization-code-input">
                <div className="input-wrapper">
                  <KeyRound className="input-icon" size={15} />
                  <input id="organization-code" className={`form-input input-with-icon${errors.organization_code ? ' input-error' : ''}`}
                    type="text" placeholder="Paste code from your HR team" value={form.organization_code}
                    onChange={updateField('organization_code')} />
                </div>
                <button className="auth-secondary-button" type="button" onClick={verifyOrganization} disabled={checkingOrganization}>
                  {checkingOrganization ? 'Checking…' : 'Verify'}
                </button>
              </div>
              {errors.organization_code && <span className="field-error">{errors.organization_code}</span>}
              {organization && <span className="organization-verified"><ShieldCheck size={14} /> Joining {organization.name}</span>}
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="register-password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={15} />
              <input id="register-password" className={`form-input input-with-icon input-with-right-icon${errors.password ? ' input-error' : ''}`}
                type={showPassword ? 'text' : 'password'} placeholder="At least 8 characters" value={form.password}
                onChange={updateField('password')} autoComplete="new-password" />
              <button type="button" className="input-right-icon" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {form.password && <div className="password-strength"><div className="password-strength-track"><span style={{ width: `${strength * 20}%` }} /></div><span>{strengthLabel}</span></div>}
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirm-password">Confirm Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={15} />
              <input id="confirm-password" className={`form-input input-with-icon input-with-right-icon${errors.confirm_password ? ' input-error' : ''}`}
                type={showConfirmPassword ? 'text' : 'password'} placeholder="Re-enter your password" value={form.confirm_password}
                onChange={updateField('confirm_password')} autoComplete="new-password" />
              <button type="button" className="input-right-icon" onClick={() => setShowConfirmPassword((value) => !value)} aria-label={showConfirmPassword ? 'Hide confirmation' : 'Show confirmation'}>
                {showConfirmPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {errors.confirm_password && <span className="field-error">{errors.confirm_password}</span>}
          </div>

          <button className="auth-submit" type="submit" disabled={loading || connection.state === 'offline'}>
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">Already have an account? <Link to="/login">Sign in</Link></div>
      </div>
    </div>
  );
}
