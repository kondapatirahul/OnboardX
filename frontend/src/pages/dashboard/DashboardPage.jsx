import { useAuth } from '../../context/AuthContext';
import '../../styles/layout.css';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.full_name?.split(' ')[0] || 'there'} 👋</h1>
          <p>Here's what's happening with your onboarding today.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Total Employees', value: '—', color: 'var(--color-teal)' },
          { label: 'Active Onboarding', value: '—', color: 'var(--color-coral)' },
          { label: 'Pending Approvals', value: '—', color: '#b85c2a' },
          { label: 'Completed', value: '—', color: 'var(--color-teal)' },
        ].map(stat => (
          <div key={stat.label} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>{stat.label}</div>
            <div style={{ fontSize: '28px', fontWeight: 700, color: stat.color }}>{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', textAlign: 'center', padding: '32px' }}>
          Dashboard charts and activity feed will be populated once data is available.
        </div>
      </div>
    </div>
  );
}
