import { useCallback, useEffect, useState } from 'react';
import { employeeService } from '../services/employees';

const PAGE_SIZE = 10;

export function useEmployees() {
  const [items, setItems] = useState([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 });
  const [filters, setFilters] = useState({ search: '', status: '', department_id: '', page: 1 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadEmployees = useCallback(async (overrides = {}) => {
    const next = { ...filters, ...overrides };
    setLoading(true);
    setError('');
    try {
      const result = await employeeService.list({
        search: next.search.trim(),
        status: next.status,
        department_id: next.department_id,
        page: next.page,
        page_size: PAGE_SIZE,
      });
      setItems(result.items || []);
      setMeta({ total: result.total ?? 0, page: result.page ?? next.page, page_size: result.page_size ?? PAGE_SIZE, pages: result.pages ?? 0 });
      setFilters(next);
    } catch (err) {
      setError(err.message || 'Unable to load employees.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { loadEmployees(); }, []); // Initial request only; filter changes are explicit.

  const updateFilters = (changes) => {
    const next = { ...filters, ...changes, page: 1 };
    setFilters(next);
    loadEmployees(next);
  };

  const changePage = (page) => loadEmployees({ page });
  const refresh = () => loadEmployees();

  return { items, meta, filters, loading, error, updateFilters, changePage, refresh, loadEmployees };
}
