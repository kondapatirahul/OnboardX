import { api } from './api';

export const profileService = {
  getMyProfile: () => api.get('/profile/me'),
  updateMyProfile: (payload) => api.patch('/profile/me', payload),
};
