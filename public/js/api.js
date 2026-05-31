const API_BASE_URL = (() => {
  const { hostname, port } = window.location;
  const isLocalFrontendServer = (hostname === '127.0.0.1' || hostname === 'localhost') && port && port !== '8000';
  return isLocalFrontendServer ? 'http://127.0.0.1:8000' : '';
})();

const Api = {
  getToken() {
    return localStorage.getItem('flotrack_token');
  },

  setToken(token) {
    localStorage.setItem('flotrack_token', token);
  },

  clearToken() {
    localStorage.removeItem('flotrack_token');
    localStorage.removeItem('flotrack_user');
  },

  getUser() {
    const user = localStorage.getItem('flotrack_user');
    return user ? JSON.parse(user) : null;
  },

  setUser(user) {
    localStorage.setItem('flotrack_user', JSON.stringify(user));
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (response.status === 401) {
      this.clearToken();
      if (!window.location.pathname.includes('login.html') &&
          !window.location.pathname.includes('signup.html')) {
        window.location.href = '/login.html';
      }
      throw new Error('Unauthorized');
    }

    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      let message = 'Request failed';
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail) && data.detail.length) {
        message = data.detail[0].msg || 'Validation error';
      }
      throw new Error(message);
    }

    return data;
  },

  get(endpoint) {
    return this.request(endpoint);
  },

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  },

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },
};
