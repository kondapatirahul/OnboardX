import { BriefcaseBusiness, Mail, ShieldCheck } from 'lucide-react';

const roleLabels = { SUPER_ADMIN: 'Super Admin', HR_ADMIN: 'HR Admin', MANAGER: 'Manager', EMPLOYEE: 'Employee' };

export default function ProfileHeader({ profile, onEdit }) {
  const initials = (profile.full_name || 'User').trim().split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  return (
    <section className="profile-hero">
      <div className="profile-hero-main">
        <div className="profile-avatar" aria-hidden="true">{initials || 'U'}</div>
        <div className="profile-identity">
          <span className="profile-eyebrow">EMPLOYEE SELF SERVICE</span>
          <h1>{profile.full_name}</h1>
          <div className="profile-identity-meta"><span><Mail size={14} />{profile.email}</span><span><ShieldCheck size={14} />{roleLabels[profile.role] || profile.role}</span></div>
        </div>
      </div>
      <button type="button" className="profile-primary-btn" onClick={onEdit}>Edit profile</button>
      <div className="profile-hero-designation"><BriefcaseBusiness size={15} />{profile.designation || 'Designation not set'}</div>
    </section>
  );
}
