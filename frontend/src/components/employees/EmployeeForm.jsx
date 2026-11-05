import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

const blankForm = { employee_id: '', full_name: '', email: '', temporary_password: '', department_id: '', designation: '', joining_date: '', status: 'onboarding' };

export default function EmployeeForm({ employee, departments = [], onClose, onSubmit, saving, error }) {
  const [form, setForm] = useState(blankForm);

  useEffect(() => {
    if (employee) {
      setForm({ employee_id: employee.employee_id || '', full_name: employee.full_name || '', email: employee.email || '', temporary_password: '', department_id: employee.department_id || '', designation: employee.designation || '', joining_date: employee.joining_date ? employee.joining_date.slice(0, 10) : '', status: employee.status || 'onboarding' });
    } else setForm(blankForm);
  }, [employee]);

  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  const submit = (event) => {
    event.preventDefault();
    const payload = { ...form, joining_date: form.joining_date ? new Date(`${form.joining_date}T00:00:00`).toISOString() : null, department_id: form.department_id || null };
    if (employee) {
      delete payload.employee_id;
      delete payload.temporary_password;
    }
    onSubmit(payload);
  };

  return (
    <div className="employee-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="employee-modal" role="dialog" aria-modal="true" aria-labelledby="employee-form-title">
        <header className="employee-modal-header"><div><h2 id="employee-form-title">{employee ? 'Edit employee' : 'Add employee'}</h2><p>{employee ? 'Update employee information.' : 'Create an employee profile and login account.'}</p></div><button type="button" className="employee-icon-button" onClick={onClose} aria-label="Close"><X size={19} /></button></header>
        <form onSubmit={submit} className="employee-form">
          <div className="employee-form-grid">
            {!employee && <label>Employee ID<input name="employee_id" value={form.employee_id} onChange={change} required maxLength={50} placeholder="e.g. EMP-1024" /></label>}
            <label>Full name<input name="full_name" value={form.full_name} onChange={change} required maxLength={255} placeholder="Employee full name" /></label>
            <label>Email address<input name="email" type="email" value={form.email} onChange={change} required /></label>
            {!employee && <label>Temporary password<input name="temporary_password" type="password" value={form.temporary_password} onChange={change} required minLength={8} autoComplete="new-password" /></label>}
            <label>Designation<input name="designation" value={form.designation} onChange={change} maxLength={255} placeholder="e.g. Product Designer" /></label>
            <label>Department<select name="department_id" value={form.department_id} onChange={change}><option value="">Not assigned</option>{departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}</select></label>
            <label>Joining date<input name="joining_date" type="date" value={form.joining_date} onChange={change} /></label>
            <label>Status<select name="status" value={form.status} onChange={change}><option value="onboarding">Onboarding</option><option value="active">Active</option><option value="inactive">Inactive</option></select></label>
          </div>
          {error && <p className="employee-form-error" role="alert">{error}</p>}
          <footer className="employee-form-actions"><button type="button" className="employee-btn employee-btn--secondary" onClick={onClose}>Cancel</button><button type="submit" className="employee-btn employee-btn--primary" disabled={saving}>{saving ? 'Saving...' : employee ? 'Save changes' : 'Create employee'}</button></footer>
        </form>
      </section>
    </div>
  );
}
