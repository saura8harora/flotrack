const Dashboard = {
  async load() {
    try {
      const data = await Api.get('/api/dashboard');
      this.renderStats(data);
      this.renderHabits(data.today_habits);
      this.renderTasks(data.today_tasks);
      this.renderProductivity(data.productivity_summary);
    } catch (err) {
      console.error('Dashboard load error:', err);
    }
  },

  renderStats(data) {
    document.getElementById('stat-xp').textContent = data.xp;
    document.getElementById('stat-level').textContent = data.level;
    document.getElementById('stat-streak').textContent = data.current_streak;
    document.getElementById('stat-productivity').textContent = `${data.productivity_summary.score}%`;
  },

  renderHabits(habits) {
    const container = document.getElementById('habits-list');
    if (!habits.length) {
      container.innerHTML = '<div class="empty-state"><p>No habits yet. Create habits from the Calendar page.</p></div>';
      return;
    }

    container.innerHTML = habits.map(h => `
      <div class="habit-item" data-id="${h.id}">
        <div class="habit-check ${h.completed_today ? 'completed' : ''}" data-id="${h.id}">
          ${h.completed_today ? '✓' : ''}
        </div>
        <div class="habit-info">
          <div class="title">${this.escape(h.title)}</div>
          <div class="meta">${this.escape(h.category)} · ${h.xp_reward} XP</div>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.habit-check').forEach(el => {
      el.addEventListener('click', () => this.toggleHabit(el.dataset.id));
    });
  },

  renderTasks(tasks) {
    const container = document.getElementById('tasks-list');
    if (!tasks.length) {
      container.innerHTML = '<div class="empty-state"><p>No tasks for today.</p></div>';
      return;
    }

    container.innerHTML = tasks.map(t => `
      <div class="task-item">
        <div class="task-status ${t.status}"></div>
        <div class="habit-info">
          <div class="title">${this.escape(t.title)}</div>
          <div class="meta">${t.status} · ${t.priority} priority</div>
        </div>
      </div>
    `).join('');
  },

  renderProductivity(summary) {
    const score = summary.score;
    const ring = document.getElementById('productivity-ring');

    ring.innerHTML = `
      <div class="productivity-meter">
        <div class="meter-bar-wrap">
          <div class="meter-bar-fill" style="width: ${score}%"></div>
          <div class="meter-bar-label">${score}%</div>
        </div>
      </div>
    `;

    document.getElementById('prod-habits').textContent = `${summary.habits_completed}/${summary.habits_total}`;
    document.getElementById('prod-tasks').textContent = `${summary.tasks_done}/${summary.tasks_total}`;
  },

  async toggleHabit(habitId) {
    try {
      const result = await Api.post(`/api/habits/${habitId}/toggle`);
      document.getElementById('stat-xp').textContent = result.xp;
      document.getElementById('stat-level').textContent = result.level;
      this.load();
    } catch (err) {
      console.error('Toggle habit error:', err);
    }
  },

  escape(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('dashboard-page')) {
    Dashboard.load();
  }
});
