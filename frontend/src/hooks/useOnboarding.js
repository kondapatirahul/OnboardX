import { useCallback, useEffect, useState } from 'react';
import { onboardingService } from '../services/onboarding';

export function useOnboarding() {
  const [templates, setTemplates] = useState([]);
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [templateResult, instanceResult] = await Promise.all([
        onboardingService.listTemplates(), onboardingService.listInstances(),
      ]);
      setTemplates(templateResult?.items ?? []);
      setInstances(instanceResult ?? []);
    } catch (err) {
      setError(err.message || 'Unable to load onboarding data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);
  return { templates, instances, loading, error, refresh, setInstances };
}
