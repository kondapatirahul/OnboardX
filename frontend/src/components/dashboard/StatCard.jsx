import { ArrowUpRight, Users, UserRoundCheck, ClipboardCheck, BadgeCheck } from 'lucide-react';

const iconMap = {
  employees: Users,
  onboarding: UserRoundCheck,
  approvals: ClipboardCheck,
  completed: BadgeCheck,
};

export default function StatCard({ label, value, description, tone = 'teal', icon }) {
  const Icon = iconMap[icon] || Users;

  return (
    <article className={`dashboard-stat-card dashboard-stat-card--${tone}`}>
      <div className="dashboard-stat-card__top">
        <span className="dashboard-stat-card__label">{label}</span>
        <span className="dashboard-stat-card__icon" aria-hidden="true"><Icon size={19} strokeWidth={1.8} /></span>
      </div>
      <div className="dashboard-stat-card__value">{value ?? 0}</div>
      <div className="dashboard-stat-card__footer">
        <span>{description}</span>
        <ArrowUpRight size={15} aria-hidden="true" />
      </div>
    </article>
  );
}
