import { RefreshCw } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import DepartmentBreakdown from '../../components/dashboard/DepartmentBreakdown';
import StatCard from '../../components/dashboard/StatCard';
import { useDashboardData } from '../../hooks/useDashboardData';
import '../../styles/layout.css';
import '../../styles/dashboard/dashboard.css';
import '../../styles/dashboard/responsive.css';

export default function DashboardPage() {
  const { user } = useAuth();
  const { stats, departments, loading, error, refresh } = useDashboardData();
  const firstName = user?.full_name?.trim().split(/\s+/)[0] || 'there';

  const cards = [
    { label: 'Total employees', value: stats?.total_employees, description: 'People in your organization', tone: 'teal', icon: 'employees' },
    { label: 'Active onboarding', value: stats?.active_onboarding, description: 'Currently in progress', tone: 'coral', icon: 'onboarding' },
    { label: 'Pending approvals', value: stats?.pending_approvals, description: 'Documents awaiting review', tone: 'amber', icon: 'approvals' },
    { label: 'Completed onboarding', value: stats?.completed_onboarding, description: 'Successfully completed', tone: 'teal', icon: 'completed' },
  ];

  return (
    <div className="dashboard-page">
      <div className="page-header dashboard-page__header">
        <div>
          <span className="dashboard-eyebrow">OVERVIEW</span>
          <h1>Welcome back, {firstName}</h1>
          <p>Here’s what’s happening with your onboarding today.</p>
        </div>
        <button className="btn btn-secondary dashboard-refresh" type="button" onClick={refresh} disabled={loading}>
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="dashboard-alert" role="alert">
          <span>{error}</span>
          <button type="button" onClick={refresh}>Try again</button>
        </div>
      )}

      <section className="dashboard-stats-grid" aria-label="Organization statistics" aria-busy={loading}>
        {cards.map((card) => (
          <StatCard key={card.label} {...card} value={loading && !stats ? '—' : card.value} />
        ))}
      </section>

      <div className="dashboard-content-grid">
        <DepartmentBreakdown departments={departments} />
        <section className="card onboarding-progress-card" aria-labelledby="onboarding-progress-heading">
          <div className="dashboard-section-heading">
            <div>
              <h2 id="onboarding-progress-heading">Onboarding completion</h2>
              <p>Overall completion across your organization</p>
            </div>
          </div>
          <div className="completion-value">{loading && !stats ? '—' : `${stats?.completion_percentage ?? 0}%`}</div>
          <div className="completion-track" role="progressbar" aria-label="Onboarding completion" aria-valuenow={stats?.completion_percentage ?? 0} aria-valuemin="0" aria-valuemax="100">
            <span style={{ width: `${Math.min(100, Math.max(0, stats?.completion_percentage ?? 0))}%` }} />
          </div>
          <p className="completion-caption">Completion rate across all onboarding records in your organization</p>
        </section>
      </div>

      {loading && <p className="dashboard-loading-note" role="status">Updating dashboard data…</p>}
    </div>
  );
}
