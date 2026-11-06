import { useCallback, useEffect, useState } from 'react';
import { profileService } from '../services/profile';

export function useMyProfile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await profileService.getMyProfile();
      setProfile(result);
      return result;
    } catch (err) {
      setError(err.message || 'Unable to load your profile.');
      return null;
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const update = useCallback(async (payload) => {
    setSaving(true);
    setError('');
    try {
      const result = await profileService.updateMyProfile(payload);
      setProfile(result);
      return result;
    } catch (err) {
      setError(err.message || 'Unable to update your profile.');
      throw err;
    } finally { setSaving(false); }
  }, []);

  return { profile, loading, error, saving, refresh, update };
}
