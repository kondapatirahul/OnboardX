import { useCallback, useEffect, useState } from 'react';
import { departmentService } from '../services/departments';

export function useDepartments() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setItems(await departmentService.list());
    } catch (err) {
      setError(err.message || 'Unable to load departments.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return { items, loading, error, refresh };
}
