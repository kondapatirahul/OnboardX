import { useMemo, useState } from 'react';
import { AlertCircle, ChevronLeft, ChevronRight, Plus, RefreshCw, Search, Users } from 'lucide-react';
import { employeeService } from '../services/employees';
import { useEmployees } from '../hooks/useEmployees';
import EmployeeTable from '../components/employees/EmployeeTable';
import EmployeeForm from '../components/employees/EmployeeForm';
import EmployeeDetails from '../components/employees/EmployeeDetails';
import '../styles/employees/employees.css';

export default function EmployeesPage() {
  const { items, meta, filters, loading, error, updateFilters, changePage, refresh } = useEmployees();
  const [searchText, setSearchText] = useState('');
  const [formEmployee, setFormEmployee] = useState(undefined);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [actionError, setActionError] = useState('');
  const departments = useMemo(() => [...new Map(items.filter((item) => item.department_id).map((item) => [item.department_id, { id: item.department_id, name: item.department_name || item.department_id }])).values()], [items]);

  const openCreate = () => { setFormEmployee(null); setFormError(''); };
  const openEdit = (employee) => { setSelectedEmployee(null); setFormEmployee(employee); setFormError(''); };
  const closeForm = () => { setFormEmployee(undefined); setFormError(''); };

  const submitForm = async (payload) => {
    setSaving(true); setFormError('');
    try {
      if (formEmployee) await employeeService.update(formEmployee.id, payload);
      else await employeeService.create(payload);
      closeForm();
      await refresh();
    } catch (err) {
      setFormError(err.message || 'Unable to save employee.');
    } finally { setSaving(false); }
  };

  const deactivate = async (employee) => {
    if (!window.confirm(`Deactivate ${employee.full_name}? They will no longer be able to sign in.`)) return;
    setActionError('');
    try { await employeeService.deactivate(employee.id); await refresh(); }
    catch (err) { setActionError(err.message || 'Unable to deactivate employee.'); }
  };

  const search = (event) => { event.preventDefault(); updateFilters({ search: searchText }); };

  return (
    <section className="employees-page">
      <div className="employees-page-header"><div><div className="employees-eyebrow">PEOPLE MANAGEMENT</div><h1>Employees</h1><p>Manage your organization’s employee directory and profiles.</p></div><button type="button" className="employee-btn employee-btn--primary" onClick={openCreate}><Plus size={17} /> Add employee</button></div>
      <div className="employees-summary-row"><div className="employees-summary-icon"><Users size={19} /></div><div><strong>{meta.total.toLocaleString()}</strong><span>Total employees in your organization</span></div><button type="button" className="employees-refresh" onClick={refresh} disabled={loading}><RefreshCw size={15} /> Refresh</button></div>
      <div className="employees-toolbar"><form className="employees-search" onSubmit={search}><Search size={17} /><input value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder="Search by name, email or employee ID" aria-label="Search employees" /><button type="submit">Search</button></form><div className="employees-filters"><select aria-label="Filter by status" value={filters.status} onChange={(event) => updateFilters({ status: event.target.value })}><option value="">All statuses</option><option value="active">Active</option><option value="onboarding">Onboarding</option><option value="inactive">Inactive</option></select><select aria-label="Filter by department" value={filters.department_id} onChange={(event) => updateFilters({ department_id: event.target.value })}><option value="">All departments</option>{departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}</select></div></div>
      {(error || actionError) && <div className="employees-alert" role="alert"><AlertCircle size={17} /><span>{error || actionError}</span>{error && <button type="button" onClick={refresh}>Retry</button>}</div>}
      <div className="employees-table-card"><div className="employees-table-heading"><div><h2>Employee directory</h2><p>{meta.total} {meta.total === 1 ? 'employee' : 'employees'} found</p></div><span className="employees-page-size">10 per page</span></div><EmployeeTable employees={items} loading={loading} onView={setSelectedEmployee} onEdit={openEdit} onDeactivate={deactivate} /><div className="employees-pagination"><span>Page {meta.pages ? meta.page : 0} of {meta.pages}</span><div><button type="button" aria-label="Previous page" disabled={loading || meta.page <= 1} onClick={() => changePage(meta.page - 1)}><ChevronLeft size={17} /></button><button type="button" aria-label="Next page" disabled={loading || meta.page >= meta.pages} onClick={() => changePage(meta.page + 1)}><ChevronRight size={17} /></button></div></div></div>
      {formEmployee !== undefined && <EmployeeForm employee={formEmployee} departments={departments} onClose={closeForm} onSubmit={submitForm} saving={saving} error={formError} />}
      {selectedEmployee && <EmployeeDetails employee={selectedEmployee} onClose={() => setSelectedEmployee(null)} onEdit={openEdit} />}
    </section>
  );
}
