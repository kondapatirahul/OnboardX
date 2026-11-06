const configuredBase = import.meta.env.VITE_API_URL || '/api/v1';
export const API_BASE_URL = configuredBase.replace(/\/+$/, '');

function explainNetworkError(error) {
  if (error instanceof TypeError || error?.name === 'TypeError') {
    return `Cannot reach the OnboardX API at ${API_BASE_URL}. Start the FastAPI server on port 8000 and check your VITE_API_URL setting.`;
  }
  return error?.message || 'An unexpected network error occurred.';
}

async function readResponse(response) {
  if (response.status === 204) return null;
  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => ({}))
    : { detail: await response.text().catch(() => '') };
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg).join(', ')
      : payload.detail;
    throw new Error(detail || payload.message || `Request failed (${response.status})`);
  }
  return payload;
}

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { Accept: 'application/json', ...options.headers };
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) headers.Authorization = `Bearer ${token}`;

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    return await readResponse(response);
  } catch (error) {
    if (error instanceof TypeError || error?.name === 'TypeError') {
      throw new Error(explainNetworkError(error));
    }
    throw error;
  }
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (path, body) => request(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: 'DELETE' }),
  postForm: (path, formData) => request(path, { method: 'POST', body: formData }),
  postUrlEncoded: (path, values) => request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(values),
  }),
  checkConnection: () => request('/health'),
  resolveOrganization: (code) => request(`/auth/organizations/resolve/${encodeURIComponent(code)}`),
};
