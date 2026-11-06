import { Building2, CalendarDays, CheckCircle2, Clock3, UserRound } from 'lucide-react';

const statusLabels = { ACTIVE: 'Active', ONBOARDING: 'Onboarding', INACTIVE: 'Inactive', TERMINATED: 'Terminated', ON_LEAVE: 'On leave', OFFBOARDING: 'Offboarding' };
function formatDate(value) {
  if (!value) return 'Not available';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Not available' : new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'long', year: 'numeric' }).format(date);
}
function InfoItem({ icon: Icon, label, value }) {
  return <div className="profile-info-item"><span className="profile-info-icon"><Icon size={17} /></span><div><span className="profile-info-label">{label}</span><strong>{value || 'Not available'}</strong></div></div>;
}
export default function ProfileInformation({ profile }) {
  const status = String(profile.status || '').toUpperCase();
  return (
    <div className="profile-content-grid">
      <section className="profile-panel"><div className="profile-panel-heading"><div><h2>Work information</h2><p>Your role and reporting details</p></div></div>
        <div className="profile-info-grid">
          <InfoItem icon={UserRound} label="Employee ID" value={profile.employee_id} />
          <InfoItem icon={Building2} label="Department" value={profile.department_name} />
          <InfoItem icon={UserRound} label="Reports to" value={profile.manager_name} />
          <InfoItem icon={CalendarDays} label="Joining date" value={formatDate(profile.joining_date)} />
        </div>
      </section>
      <section className="profile-panel profile-status-panel"><div className="profile-panel-heading"><div><h2>Account status</h2><p>Current employment and access status</p></div></div>
        <div className="profile-status-row">
          <span className={`profile-status-pill ${status === 'ACTIVE' ? 'is-active' : 'is-other'}`}><CheckCircle2 size={14} />{statusLabels[status] || profile.status || 'Unknown'}</span>
          <span className={`profile-status-pill ${profile.account_active ? 'is-active' : 'is-other'}`}><Clock3 size={14} />{profile.account_active ? 'Account enabled' : 'Account disabled'}</span>
        </div>
        <p className="profile-security-note">For security, your email, role, department, manager and employment status are managed by your HR team.</p>
      </section>
    </div>
  );
}
