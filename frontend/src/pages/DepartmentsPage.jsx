import { useMemo, useState } from 'react';
import { AlertCircle, Building2, Plus, RefreshCw, Search, Users } from 'lucide-react';
import { departmentService } from '../services/departments';
import { useDepartments } from '../hooks/useDepartments';
import DepartmentTable from '../components/departments/DepartmentTable';
import DepartmentForm from '../components/departments/DepartmentForm';
import '../styles/departments/departments.css';

export default function DepartmentsPage() {
  const { items, loading, error, refresh } = useDepartments();
  const [query, setQuery] = useState('');
  const [editing, setEditing] = useState(undefined);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [actionError, setActionError] = useState('');
  const totalEmployees = useMemo(() => items.reduce((sum, item) => sum + Number(item.employee_count || 0), 0), [items]);
  const filtered = useMemo(() => items.filter((item) => item.name.toLowerCase().includes(query.trim().toLowerCase())), [items, query]);

  const saveDepartment = async (payload) => {
    setSaving(true); setFormError('');
    try {
      if (editing) await departmentService.update(editing.id, payload);
      else await departmentService.create(payload);
      setEditing(undefined);
      await refresh();
    } catch (err) { setFormError(err.message || 'Unable to save department.'); }
    finally { setSaving(false); }
  };

  const deleteDepartment = async (department) => {
    if (Number(department.employee_count) > 0) return;
    if (!window.confirm(`Delete ${department.name}? This action cannot be undone.`)) return;
    setActionError('');
    try { await departmentService.remove(department.id); await refresh(); }
    catch (err) { setActionError(err.message || 'Unable to delete department.'); }
  };

  return (
    <section className="departments-page">
      <header className="departments-page-header"><div><div className="departments-eyebrow">ORGANIZATION STRUCTURE</div><h1>Departments</h1><p>Organize teams and manage department membership across your organization.</p></div><button type="button" className="department-btn department-btn--primary" onClick={() => { setEditing(null); setFormError(''); }}><Plus size={17} /> Add department</button></header>
      <div className="departments-metrics"><article><span className="department-metric-icon"><Building2 size={18} /></span><div><strong>{items.length.toLocaleString()}</strong><span>Total departments</span></div></article><article><span className="department-metric-icon department-metric-icon--coral"><Users size={18} /></span><div><strong>{totalEmployees.toLocaleString()}</strong><span>Employees assigned</span></div></article><button type="button" className="department-refresh" onClick={refresh} disabled={loading}><RefreshCw size={15} /> Refresh</button></div>
      <div className="departments-toolbar"><div className="department-search"><Search size={16} /><input aria-label="Search departments" placeholder="Search departments" value={query} onChange={(event) => setQuery(event.target.value)} /></div><span>{filtered.length} {filtered.length === 1 ? 'department' : 'departments'}</span></div>
      {(error || actionError) && <div className="department-alert" role="alert"><AlertCircle size={17} /><span>{error || actionError}</span>{error && <button type="button" onClick={refresh}>Retry</button>}</div>}
      <div className="department-card"><div className="department-card-heading"><div><h2>Department directory</h2><p>View and maintain your organization’s departments.</p></div></div><DepartmentTable departments={filtered} loading={loading} onEdit={(department) => { setEditing(department); setFormError(''); }} onDelete={deleteDepartment} /></div>
      {editing !== undefined && <DepartmentForm department={editing} onClose={() => { setEditing(undefined); setFormError(''); }} onSubmit={saveDepartment} saving={saving} error={formError} />}
    </section>
  );
}
