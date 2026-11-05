import { useCallback, useEffect, useState } from 'react';
import { dashboardService } from '../services/dashboard';

export function useDashboardData() {
  const [stats, setStats] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [statsResult, departmentResult] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getDepartments(),
      ]);
      setStats(statsResult);
      setDepartments(Array.isArray(departmentResult) ? departmentResult : []);
    } catch (requestError) {
      setError(requestError.message || 'Unable to load dashboard information.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { stats, departments, loading, error, refresh };
}
