const Sidebar = {
  navItems: [
    { href: '/dashboard.html', label: 'Dashboard' },
    { href: '/calendar.html', label: 'Calendar' },
    { href: '/tasks.html', label: 'Tasks' },
    { href: '/notes.html', label: 'Notes' },
    { href: '/analytics.html', label: 'Analytics' },
  ],

  render() {
    const user = Api.getUser() || { name: 'User', level: 1 };
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';

    const navLinks = this.navItems.map(item => {
      const page = item.href.split('/').pop();
      return `<a href="${item.href}" class="${currentPage === page ? 'active' : ''}">${item.label}</a>`;
    }).join('');

    const container = document.getElementById('sidebar-container');
    if (!container) return;

    container.innerHTML = `
      <header class="top-bar">
        <div class="top-nav">
          <a href="/dashboard.html" class="top-nav-brand">FloTrack</a>
          <button class="nav-toggle" id="nav-toggle" aria-label="Menu">☰</button>
          <nav class="top-nav-links" id="top-nav-links">${navLinks}</nav>
          <div class="top-nav-user">
            <span class="user-badge">${this.escapeHtml(user.name)} · LVL ${user.level || 1}</span>
            <button class="btn btn-sm btn-secondary" id="logout-btn">Logout</button>
          </div>
        </div>
      </header>
    `;

    document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('top-nav-links');
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  init() {
    if (!Auth.requireAuth()) return;
    this.render();
    Auth.refreshUser().then(user => {
      if (user) this.render();
    });
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('sidebar-container')) {
    Sidebar.init();
  }
});
