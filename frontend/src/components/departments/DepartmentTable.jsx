import { Building2, Pencil, Trash2 } from 'lucide-react';

export default function DepartmentTable({ departments, loading, onEdit, onDelete }) {
  if (loading) return <div className="department-table-state">Loading departments…</div>;
  if (!departments.length) {
    return <div className="department-table-state department-table-empty"><Building2 size={25} /><strong>No departments found</strong><span>Create your first department to organize employees.</span></div>;
  }

  return (
    <div className="department-table-wrap">
      <table className="department-table">
        <thead><tr><th>Department</th><th>Employees</th><th>Created</th><th>Actions</th></tr></thead>
        <tbody>
          {departments.map((department) => (
            <tr key={department.id}>
              <td><div className="department-name-cell"><span className="department-icon"><Building2 size={16} /></span><strong>{department.name}</strong></div></td>
              <td><span className="department-count">{Number(department.employee_count || 0).toLocaleString()}</span></td>
              <td>{department.created_at ? new Date(department.created_at).toLocaleDateString() : '—'}</td>
              <td><div className="department-actions"><button type="button" aria-label={`Edit ${department.name}`} onClick={() => onEdit(department)}><Pencil size={15} /></button><button type="button" className="department-delete" aria-label={`Delete ${department.name}`} onClick={() => onDelete(department)} disabled={Number(department.employee_count) > 0} title={Number(department.employee_count) > 0 ? 'Move employees before deleting this department' : 'Delete department'}><Trash2 size={15} /></button></div></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
