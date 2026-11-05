import { api } from './api';

export const departmentService = {
  async list() {
    const response = await api.get('/departments');
    return response?.items ?? [];
  },
  create(payload) {
    return api.post('/departments', payload);
  },
  update(id, payload) {
    return api.patch(`/departments/${id}`, payload);
  },
  remove(id) {
    return api.delete(`/departments/${id}`);
  },
};
