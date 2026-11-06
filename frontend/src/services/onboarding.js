import { api } from './api';

export const onboardingService = {
  listTemplates: () => api.get('/onboarding/templates'),
  createTemplate: (payload) => api.post('/onboarding/templates', payload),
  updateTemplate: (id, payload) => api.patch(`/onboarding/templates/${id}`, payload),
  listInstances: () => api.get('/onboarding/instances'),
  assign: (payload) => api.post('/onboarding/assignments', payload),
  updateTask: (instanceId, taskId, status) => api.patch(`/onboarding/instances/${instanceId}/tasks/${taskId}`, { status }),
  updateInstance: (instanceId, status) => api.patch(`/onboarding/instances/${instanceId}/status`, { status }),
};
