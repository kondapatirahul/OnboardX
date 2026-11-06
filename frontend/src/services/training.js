import { api } from './api';

export const trainingService = {
  courses: () => api.get('/training/courses'),
  createCourse: (payload) => api.post('/training/courses', payload),
  updateCourse: (id, payload) => api.patch(`/training/courses/${id}`, payload),
  replaceLessons: (id, lessons) => api.put(`/training/courses/${id}/lessons`, lessons),
  assign: (id, payload) => api.post(`/training/courses/${id}/assignments`, payload),
  assignments: () => api.get('/training/assignments'),
  myLearning: () => api.get('/training/my-learning'),
  learningDetail: (id) => api.get(`/training/assignments/${id}`),
  updateLesson: (assignmentId, lessonId, completed = true) => api.patch(`/training/assignments/${assignmentId}/lessons/${lessonId}`, { completed }),
  certificates: () => api.get('/training/certificates'),
  analytics: () => api.get('/training/analytics'),
};
