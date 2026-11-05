import { CalendarDays, Mail, UserRound, X } from 'lucide-react';

const readableDate = (value) => value ? new Date(value).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : 'Not provided';

export default function EmployeeDetails({ employee, onClose, onEdit }) {
  if (!employee) return null;
  const initials = employee.full_name?.split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'U';
  return (
    <div className="employee-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="employee-modal employee-details-modal" role="dialog" aria-modal="true" aria-labelledby="employee-details-title">
        <header className="employee-modal-header"><div><h2 id="employee-details-title">Employee profile</h2><p>Employee information and account status.</p></div><button type="button" className="employee-icon-button" onClick={onClose} aria-label="Close"><X size={19} /></button></header>
        <div className="employee-profile-heading"><span className="employee-profile-avatar">{initials}</span><div><h3>{employee.full_name}</h3><p>{employee.designation || 'No designation'} · {employee.employee_id}</p><span className={`employee-status ${employee.status === 'active' ? 'employee-status--active' : employee.status === 'onboarding' ? 'employee-status--onboarding' : 'employee-status--inactive'}`}>{employee.status}</span></div></div>
        <div className="employee-detail-grid">
          <div><Mail size={16} /><span><small>Email</small><strong>{employee.email}</strong></span></div>
          <div><UserRound size={16} /><span><small>Department</small><strong>{employee.department_name || 'Not assigned'}</strong></span></div>
          <div><CalendarDays size={16} /><span><small>Joining date</small><strong>{readableDate(employee.joining_date)}</strong></span></div>
          <div><UserRound size={16} /><span><small>Account</small><strong>{employee.is_active ? 'Active' : 'Disabled'}</strong></span></div>
        </div>
        <footer className="employee-form-actions"><button type="button" className="employee-btn employee-btn--secondary" onClick={onClose}>Close</button><button type="button" className="employee-btn employee-btn--primary" onClick={() => onEdit(employee)}>Edit employee</button></footer>
      </section>
    </div>
  );
}
