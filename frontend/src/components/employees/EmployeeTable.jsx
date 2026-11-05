import { Eye, Pencil, UserX, Users } from 'lucide-react';

const statusClass = (status) => {
  if (status === 'active') return 'employee-status employee-status--active';
  if (status === 'onboarding') return 'employee-status employee-status--onboarding';
  if (status === 'inactive') return 'employee-status employee-status--inactive';
  return 'employee-status';
};

const initials = (name = '') => name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'U';

export default function EmployeeTable({ employees, loading, onView, onEdit, onDeactivate }) {
  if (loading) return <div className="employee-table-state">Loading employees...</div>;
  if (!employees.length) return (
    <div className="employee-table-state employee-table-empty">
      <Users size={28} />
      <strong>No employees found</strong>
      <span>Try changing your search or filters, or add a new employee.</span>
    </div>
  );

  return (
    <div className="employee-table-wrap">
      <table className="employee-table">
        <thead><tr><th>Employee</th><th>Employee ID</th><th>Department</th><th>Designation</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id}>
              <td><div className="employee-person"><span className="employee-avatar">{initials(employee.full_name)}</span><span><strong>{employee.full_name}</strong><small>{employee.email}</small></span></div></td>
              <td className="employee-id">{employee.employee_id}</td>
              <td>{employee.department_name || '—'}</td>
              <td>{employee.designation || '—'}</td>
              <td><span className={statusClass(employee.status)}>{employee.status?.replaceAll('_', ' ') || 'Unknown'}</span></td>
              <td><div className="employee-row-actions">
                <button type="button" aria-label={`View ${employee.full_name}`} title="View details" onClick={() => onView(employee)}><Eye size={16} /></button>
                <button type="button" aria-label={`Edit ${employee.full_name}`} title="Edit employee" onClick={() => onEdit(employee)}><Pencil size={16} /></button>
                {employee.is_active && <button type="button" className="employee-action-danger" aria-label={`Deactivate ${employee.full_name}`} title="Deactivate employee" onClick={() => onDeactivate(employee)}><UserX size={16} /></button>}
              </div></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
