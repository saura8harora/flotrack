const Calendar = {
  currentYear: new Date().getFullYear(),
  currentMonth: new Date().getMonth() + 1,
  selectedDate: null,
  monthData: null,

  async init() {
    await this.loadMonth();
    this.bindEvents();
  },

  bindEvents() {
    document.getElementById('prev-month').addEventListener('click', () => this.changeMonth(-1));
    document.getElementById('next-month').addEventListener('click', () => this.changeMonth(1));
    document.getElementById('add-habit-btn').addEventListener('click', () => this.openHabitModal());
    document.getElementById('habit-form').addEventListener('submit', (e) => this.saveHabit(e));
    document.getElementById('close-habit-modal').addEventListener('click', () => this.closeHabitModal());
    document.getElementById('cancel-habit-modal').addEventListener('click', () => this.closeHabitModal());
    document.getElementById('habit-modal').addEventListener('click', (e) => {
      if (e.target.id === 'habit-modal') this.closeHabitModal();
    });
  },

  async changeMonth(delta) {
    this.currentMonth += delta;
    if (this.currentMonth > 12) {
      this.currentMonth = 1;
      this.currentYear++;
    } else if (this.currentMonth < 1) {
      this.currentMonth = 12;
      this.currentYear--;
    }
    await this.loadMonth();
  },

  async loadMonth() {
    try {
      this.monthData = await Api.get(`/api/calendar/${this.currentYear}/${this.currentMonth}`);
      this.renderCalendar();
    } catch (err) {
      console.error('Calendar load error:', err);
    }
  },

  renderCalendar() {
    const monthNames = ['January','February','March','April','May','June',
      'July','August','September','October','November','December'];
    document.getElementById('calendar-title').textContent =
      `${monthNames[this.currentMonth - 1]} ${this.currentYear}`;

    const grid = document.getElementById('calendar-grid');
    const firstDay = new Date(this.currentYear, this.currentMonth - 1, 1).getDay();
    const daysInMonth = new Date(this.currentYear, this.currentMonth, 0).getDate();
    const today = new Date().toISOString().split('T')[0];

    let html = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
      .map(d => `<div class="calendar-day-label">${d}</div>`).join('');

    const prevMonthDays = new Date(this.currentYear, this.currentMonth - 1, 0).getDate();
    for (let i = firstDay - 1; i >= 0; i--) {
      html += `<div class="calendar-day other-month"><span class="day-num">${prevMonthDays - i}</span></div>`;
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${this.currentYear}-${String(this.currentMonth).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
      const dayData = this.monthData.days[dateStr] || { tasks: 0, habits: 0, notes: 0 };
      const isToday = dateStr === today;
      const isSelected = dateStr === this.selectedDate;

      let dots = '';
      if (dayData.tasks) dots += `<span class="day-dot tasks" title="${dayData.tasks} tasks"></span>`;
      if (dayData.habits) dots += `<span class="day-dot habits" title="${dayData.habits} habits"></span>`;
      if (dayData.notes) dots += `<span class="day-dot notes" title="${dayData.notes} notes"></span>`;

      html += `
        <div class="calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}"
             data-date="${dateStr}">
          <span class="day-num">${day}</span>
          <div class="day-dots">${dots}</div>
        </div>
      `;
    }

    const totalCells = firstDay + daysInMonth;
    const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
    for (let i = 1; i <= remaining; i++) {
      html += `<div class="calendar-day other-month"><span class="day-num">${i}</span></div>`;
    }

    grid.innerHTML = html;

    grid.querySelectorAll('.calendar-day[data-date]').forEach(el => {
      el.addEventListener('click', () => {
        window.location.href = `/tasks.html?date=${el.dataset.date}`;
      });
    });
  },

  async selectDay(dateStr) {
    this.selectedDate = dateStr;
    this.renderCalendar();

    const panel = document.getElementById('day-panel');
    panel.classList.remove('hidden-panel');
    document.getElementById('panel-date').textContent = new Date(dateStr + 'T12:00:00')
      .toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

    try {
      const data = await Api.get(`/api/calendar/day/${dateStr}`);
      this.renderPanel(data);
    } catch (err) {
      console.error('Day detail error:', err);
    }
  },

  renderPanel(data) {
    this.renderPanelSection('panel-tasks', data.tasks, 'task', async (title) => {
      await Api.post('/api/tasks', { title, status: 'dump', priority: 'medium', date: this.selectedDate });
      this.selectDay(this.selectedDate);
      this.loadMonth();
    }, async (id) => {
      await Api.delete(`/api/tasks/${id}`);
      this.selectDay(this.selectedDate);
      this.loadMonth();
    });

    this.renderPanelHabits(data.habits);

    this.renderPanelSection('panel-notes', data.notes, 'note', async (title) => {
      await Api.post('/api/notes', { title, content: '' });
      this.selectDay(this.selectedDate);
      this.loadMonth();
    }, async (id) => {
      await Api.delete(`/api/notes/${id}`);
      this.selectDay(this.selectedDate);
      this.loadMonth();
    });
  },

  renderPanelSection(containerId, items, type, onAdd, onDelete) {
    const container = document.getElementById(containerId);
    const listHtml = items.length
      ? items.map(item => `
          <div class="panel-item">
            <span style="flex:1">${this.escape(item.title)}</span>
            <button class="btn-icon btn-sm delete-${type}" data-id="${item.id}">✕</button>
          </div>
        `).join('')
      : '<p style="color:var(--text-muted);font-size:0.85rem">No items</p>';

    container.innerHTML = listHtml + `
      <div class="panel-add-form">
        <input type="text" placeholder="Add ${type}..." class="add-${type}-input">
        <button class="btn btn-primary btn-sm add-${type}-btn">Add</button>
      </div>
    `;

    container.querySelector(`.add-${type}-btn`).addEventListener('click', async () => {
      const input = container.querySelector(`.add-${type}-input`);
      const title = input.value.trim();
      if (!title) return;
      await onAdd(title);
      input.value = '';
    });

    container.querySelectorAll(`.delete-${type}`).forEach(btn => {
      btn.addEventListener('click', () => onDelete(btn.dataset.id));
    });
  },

  renderPanelHabits(habits) {
    const container = document.getElementById('panel-habits');
    const listHtml = habits.length
      ? habits.map(h => `
          <div class="panel-item">
            <div class="habit-check ${h.completed ? 'completed' : ''}" data-id="${h.id}">
              ${h.completed ? '✓' : ''}
            </div>
            <span style="flex:1">${this.escape(h.title)}</span>
            <span class="badge badge-accent">${h.xp_reward} XP</span>
            <button class="btn-icon btn-sm delete-habit" data-id="${h.id}">✕</button>
          </div>
        `).join('')
      : '<p style="color:var(--text-muted);font-size:0.85rem">No habits</p>';

    container.innerHTML = listHtml;

    container.querySelectorAll('.habit-check').forEach(el => {
      el.addEventListener('click', async () => {
        await Api.post(`/api/habits/${el.dataset.id}/toggle?date=${this.selectedDate}`);
        this.selectDay(this.selectedDate);
        this.loadMonth();
      });
    });

    container.querySelectorAll('.delete-habit').forEach(btn => {
      btn.addEventListener('click', async () => {
        await Api.delete(`/api/habits/${btn.dataset.id}`);
        this.selectDay(this.selectedDate);
        this.loadMonth();
      });
    });
  },

  openHabitModal() {
    document.getElementById('habit-form').reset();
    document.getElementById('habit-id').value = '';
    document.getElementById('habit-modal').classList.add('active');
  },

  closeHabitModal() {
    document.getElementById('habit-modal').classList.remove('active');
  },

  async saveHabit(e) {
    e.preventDefault();
    const payload = {
      title: document.getElementById('habit-title').value.trim(),
      category: document.getElementById('habit-category').value.trim(),
      xp_reward: parseInt(document.getElementById('habit-xp').value, 10),
    };

    try {
      await Api.post('/api/habits', payload);
      this.closeHabitModal();
      if (this.selectedDate) this.selectDay(this.selectedDate);
      await this.loadMonth();
    } catch (err) {
      alert(err.message || 'Failed to save habit');
    }
  },

  escape(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('calendar-page')) {
    Calendar.init();
  }
});
