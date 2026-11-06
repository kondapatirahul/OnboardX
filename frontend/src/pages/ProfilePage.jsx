import { useState } from 'react';
import { AlertCircle, RefreshCw, UserRound } from 'lucide-react';
import { useMyProfile } from '../hooks/useMyProfile';
import { useAuth } from '../context/AuthContext';
import ProfileHeader from '../components/profile/ProfileHeader';
import ProfileInformation from '../components/profile/ProfileInformation';
import EditProfileForm from '../components/profile/EditProfileForm';
import '../styles/profile/profile.css';

export default function ProfilePage() {
  const { profile, loading, error, saving, refresh, update } = useMyProfile();
  const { updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [notice, setNotice] = useState('');
  const saveProfile = async (payload) => {
    try { const updated = await update(payload); updateUser({ full_name: updated.full_name }); setEditing(false); setNotice('Your profile has been updated.'); }
    catch { /* The hook exposes the API error to the edit form. */ }
  };
  if (loading && !profile) return <section className="profile-page"><div className="profile-state-card"><span className="profile-loader" /><strong>Loading your profile…</strong></div></section>;
  if (error && !profile) return <section className="profile-page"><div className="profile-state-card profile-state-error"><AlertCircle size={22} /><h2>We couldn't load your profile</h2><p>{error}</p><button type="button" className="profile-primary-btn" onClick={refresh}><RefreshCw size={15} /> Try again</button></div></section>;
  if (!profile) return <section className="profile-page"><div className="profile-state-card"><UserRound size={24} /><strong>No employee profile is available for this account.</strong></div></section>;
  return (
    <section className="profile-page">
      <div className="profile-page-heading"><div><span className="profile-eyebrow">MY ACCOUNT</span><h1>My profile</h1><p>View your employee information and manage your personal details.</p></div><button type="button" className="profile-refresh-btn" onClick={refresh} disabled={loading}><RefreshCw size={15} /> Refresh</button></div>
      {notice && <div className="profile-success-message" role="status">{notice}<button type="button" onClick={() => setNotice('')} aria-label="Dismiss">×</button></div>}
      {error && <div className="profile-inline-error" role="alert"><AlertCircle size={16} />{error}</div>}
      <ProfileHeader profile={profile} onEdit={() => { setNotice(''); setEditing(true); }} />
      <ProfileInformation profile={profile} />
      {editing && <EditProfileForm profile={profile} saving={saving} error={error} onClose={() => setEditing(false)} onSubmit={saveProfile} />}
    </section>
  );
}
