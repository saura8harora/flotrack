const Auth = {
  requireAuth() {
    if (!Api.getToken()) {
      window.location.href = '/login.html';
      return false;
    }
    return true;
  },

  redirectIfAuthenticated() {
    if (Api.getToken()) {
      window.location.href = '/dashboard.html';
    }
  },

  async login(email, password) {
    const data = await Api.post('/api/auth/login', { email, password });
    Api.setToken(data.access_token);
    Api.setUser(data.user);
    return data;
  },

  async signup(name, email, password) {
    const data = await Api.post('/api/auth/signup', { name, email, password });
    Api.setToken(data.access_token);
    Api.setUser(data.user);
    return data;
  },

  logout() {
    Api.clearToken();
    window.location.href = '/login.html';
  },

  async refreshUser() {
    try {
      const user = await Api.get('/api/auth/me');
      Api.setUser(user);
      return user;
    } catch {
      return null;
    }
  },
};

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    Auth.redirectIfAuthenticated();
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById('auth-error');
      errorEl.classList.add('hidden');

      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      if (!email || !password) {
        errorEl.textContent = 'Please fill in all fields';
        errorEl.classList.remove('hidden');
        return;
      }

      try {
        await Auth.login(email, password);
        window.location.href = '/dashboard.html';
      } catch (err) {
        errorEl.textContent = err.message || 'Login failed';
        errorEl.classList.remove('hidden');
      }
    });
  }

  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    Auth.redirectIfAuthenticated();
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById('auth-error');
      errorEl.classList.add('hidden');

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirm = document.getElementById('confirm-password').value;

      if (!name || !email || !password) {
        errorEl.textContent = 'Please fill in all fields';
        errorEl.classList.remove('hidden');
        return;
      }

      if (password.length < 6) {
        errorEl.textContent = 'Password must be at least 6 characters';
        errorEl.classList.remove('hidden');
        return;
      }

      if (password !== confirm) {
        errorEl.textContent = 'Passwords do not match';
        errorEl.classList.remove('hidden');
        return;
      }

      try {
        await Auth.signup(name, email, password);
        window.location.href = '/dashboard.html';
      } catch (err) {
        errorEl.textContent = err.message || 'Signup failed';
        errorEl.classList.remove('hidden');
      }
    });
  }
});
