import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

export default function EditProfileForm({ profile, saving, error, onClose, onSubmit }) {
  const [fullName, setFullName] = useState(profile.full_name || '');
  const [localError, setLocalError] = useState('');
  useEffect(() => {
    const onKeyDown = (event) => { if (event.key === 'Escape' && !saving) onClose(); };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose, saving]);
  const submit = async (event) => {
    event.preventDefault();
    const cleaned = fullName.trim();
    if (!cleaned) { setLocalError('Please enter your full name.'); return; }
    if (cleaned.length > 255) { setLocalError('Your name must be 255 characters or fewer.'); return; }
    setLocalError('');
    await onSubmit({ full_name: cleaned });
  };
  return (
    <div className="profile-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) onClose(); }}>
      <section className="profile-modal" role="dialog" aria-modal="true" aria-labelledby="profile-edit-title">
        <div className="profile-modal-heading"><div><span className="profile-eyebrow">PERSONAL DETAILS</span><h2 id="profile-edit-title">Edit your profile</h2><p>Update the name shown across OnboardX.</p></div><button type="button" className="profile-modal-close" onClick={onClose} disabled={saving} aria-label="Close"><X size={19} /></button></div>
        <form onSubmit={submit}><label className="profile-form-label" htmlFor="profile-full-name">Full name</label><input id="profile-full-name" className="profile-form-input" value={fullName} onChange={(event) => setFullName(event.target.value)} maxLength={255} autoFocus /><p className="profile-form-hint">Your email and employment information can only be changed by HR.</p>
          {(localError || error) && <div className="profile-form-error" role="alert">{localError || error}</div>}
          <div className="profile-modal-actions"><button type="button" className="profile-secondary-btn" onClick={onClose} disabled={saving}>Cancel</button><button type="submit" className="profile-primary-btn" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</button></div>
        </form>
      </section>
    </div>
  );
}
