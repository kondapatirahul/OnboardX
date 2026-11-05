import { Building2 } from 'lucide-react';

export default function DepartmentBreakdown({ departments = [] }) {
  const total = departments.reduce((sum, department) => sum + department.employee_count, 0);

  return (
    <section className="card department-card" aria-labelledby="department-heading">
      <div className="dashboard-section-heading">
        <div>
          <h2 id="department-heading">Employees by department</h2>
          <p>How your organization is distributed</p>
        </div>
        <span className="department-card__total">{total} employees</span>
      </div>

      {departments.length === 0 ? (
        <div className="dashboard-empty-state">
          <Building2 size={25} strokeWidth={1.6} />
          <strong>No departments yet</strong>
          <span>Departments will appear here once they are added to your organization.</span>
        </div>
      ) : (
        <div className="department-list">
          {departments.map((department) => {
            const percentage = total > 0 ? (department.employee_count / total) * 100 : 0;
            return (
              <div className="department-row" key={department.department_id}>
                <div className="department-row__details">
                  <span className="department-row__name">{department.department_name}</span>
                  <span className="department-row__count">{department.employee_count}</span>
                </div>
                <div className="department-progress" role="progressbar" aria-label={`${department.department_name} employee share`} aria-valuenow={Math.round(percentage)} aria-valuemin="0" aria-valuemax="100">
                  <span style={{ width: `${percentage}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
