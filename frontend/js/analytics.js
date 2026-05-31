const Analytics = {
  async load() {
    try {
      const data = await Api.get('/api/analytics');
      this.renderCompletion(data);
      this.renderWeekly(data.weekly_progress);
      this.renderMonthly(data.monthly_progress);
      this.renderXP(data);
      this.renderStreak(data.streak_history, data.current_streak);
    } catch (err) {
      console.error('Analytics load error:', err);
    }
  },

  renderCompletion(data) {
    document.getElementById('completion-pct').textContent = `${data.habit_completion_percentage}%`;
    document.getElementById('completion-detail').innerHTML = `
      <p><strong>${data.today_completions}</strong> of <strong>${data.total_habits}</strong> habits completed today</p>
      <p>Keep going to maintain your streak!</p>
    `;
  },

  renderWeekly(progress) {
    const max = Math.max(...progress.map(p => p.completions), 1);
    const container = document.getElementById('weekly-chart');
    container.innerHTML = progress.map(p => `
      <div class="chart-bar-group">
        <div class="chart-bar" style="height: ${(p.completions / max) * 100}%"></div>
        <span class="chart-bar-label">${p.label}</span>
      </div>
    `).join('');
  },

  renderMonthly(progress) {
    const max = Math.max(...progress.map(p => p.completions), 1);
    const container = document.getElementById('monthly-chart');
    const sampled = progress.filter((_, i) => i % 3 === 0);
    container.innerHTML = sampled.map(p => {
      const day = new Date(p.date).getDate();
      return `
        <div class="chart-bar-group">
          <div class="chart-bar" style="height: ${(p.completions / max) * 100}%"></div>
          <span class="chart-bar-label">${day}</span>
        </div>
      `;
    }).join('');
  },

  renderXP(data) {
    document.getElementById('xp-total').textContent = data.xp;
    document.getElementById('xp-level').textContent = data.level;
    document.getElementById('xp-next').textContent = 100 - (data.xp % 100);

    const max = Math.max(...data.xp_growth.map(p => p.xp), 1);
    const container = document.getElementById('xp-chart');
    container.innerHTML = data.xp_growth.map(p => {
      const day = new Date(p.date).toLocaleDateString('en-US', { weekday: 'short' });
      return `
        <div class="chart-bar-group">
          <div class="chart-bar" style="height: ${(p.xp / max) * 100}%"></div>
          <span class="chart-bar-label">${day}</span>
        </div>
      `;
    }).join('');
  },

  renderStreak(history, currentStreak) {
    document.getElementById('streak-current').textContent = currentStreak;
    const container = document.getElementById('streak-timeline');
    container.innerHTML = history.map(d => `
      <div class="streak-day">
        <div class="streak-dot ${d.active ? 'active' : 'inactive'}">${d.active ? '✓' : '·'}</div>
        <span class="label">${d.label}</span>
      </div>
    `).join('');
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('analytics-page')) {
    Analytics.load();
  }
});
