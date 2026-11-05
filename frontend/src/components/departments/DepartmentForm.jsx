import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

export default function DepartmentForm({ department, onClose, onSubmit, saving, error }) {
  const [name, setName] = useState(department?.name || '');
  useEffect(() => { setName(department?.name || ''); }, [department]);

  const submit = (event) => {
    event.preventDefault();
    onSubmit({ name: name.trim() });
  };

  return (
    <div className="department-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="department-modal" role="dialog" aria-modal="true" aria-labelledby="department-form-title">
        <header className="department-modal-header"><div><h2 id="department-form-title">{department ? 'Edit department' : 'Add department'}</h2><p>{department ? 'Update the department name.' : 'Create a department for your organization.'}</p></div><button type="button" className="department-close" onClick={onClose} aria-label="Close"><X size={18} /></button></header>
        <form className="department-form" onSubmit={submit}>
          <label htmlFor="department-name">Department name</label>
          <input id="department-name" autoFocus required minLength={2} maxLength={255} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Engineering" />
          {error && <p className="department-form-error" role="alert">{error}</p>}
          <div className="department-form-actions"><button type="button" className="department-btn department-btn--secondary" onClick={onClose}>Cancel</button><button type="submit" className="department-btn department-btn--primary" disabled={saving || name.trim().length < 2}>{saving ? 'Saving…' : department ? 'Save changes' : 'Create department'}</button></div>
        </form>
      </section>
    </div>
  );
}
