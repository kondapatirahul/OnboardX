import { api } from './api';

export const performanceService = {
  goals: (params = {}) => api.get(`/performance/goals${params.employee_id ? `?employee_id=${encodeURIComponent(params.employee_id)}` : ''}`),
  createGoal: (payload) => api.post('/performance/goals', payload),
  updateGoal: (id, payload) => api.patch(`/performance/goals/${id}`, payload),
  updateKeyResult: (id, current_value) => api.patch(`/performance/key-results/${id}`, { current_value }),
  cycles: () => api.get('/performance/cycles'),
  createCycle: (payload) => api.post('/performance/cycles', payload),
  createReview: (cycleId, employeeId) => api.post(`/performance/cycles/${cycleId}/reviews?employee_id=${encodeURIComponent(employeeId)}`, {}),
  reviews: () => api.get('/performance/reviews'),
  selfReview: (id, payload) => api.patch(`/performance/reviews/${id}/self`, payload),
  managerReview: (id, payload) => api.patch(`/performance/reviews/${id}/manager`, payload),
  feedback: (id, payload) => api.post(`/performance/reviews/${id}/feedback`, payload),
  plans: () => api.get('/performance/improvement-plans'),
  createPlan: (payload) => api.post('/performance/improvement-plans', payload),
  analytics: () => api.get('/performance/analytics'),
  team: () => api.get('/performance/team'),
};
