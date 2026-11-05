import { api } from './api';

const queryString = (params) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value);
  });
  return query.toString();
};

export const employeeService = {
  list: (filters = {}) => api.get(`/employees?${queryString(filters)}`),
  get: (employeeId) => api.get(`/employees/${employeeId}`),
  create: (payload) => api.post('/employees', payload),
  update: (employeeId, payload) => api.patch(`/employees/${employeeId}`, payload),
  deactivate: (employeeId) => api.delete(`/employees/${employeeId}`),
};
