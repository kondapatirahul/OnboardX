import { api } from './api';

export const dashboardService = {
  getStats: () => api.get('/dashboard/stats'),
  getDepartments: () => api.get('/dashboard/departments'),
};
