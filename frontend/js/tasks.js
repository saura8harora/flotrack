const Tasks = {
  tasks: [],
  columns: ['dump', 'later', 'done'],
  selectedDate: null,

  getDateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const date = params.get('date');
    if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) return null;
    return date;
  },

  formatDateLabel(dateStr) {
    return new Date(`${dateStr}T12:00:00`).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  },

  initDateFilter() {
    this.selectedDate = this.getDateFromUrl();
    const banner = document.getElementById('tasks-date-banner');
    const subtitle = document.getElementById('tasks-subtitle');

    if (!this.selectedDate) {
      if (banner) banner.classList.add('hidden');
      if (subtitle) subtitle.textContent = 'Kanban board — dump · later · done';
      return;
    }

    if (banner) banner.classList.remove('hidden');
    if (subtitle) subtitle.textContent = `Tasks for ${this.formatDateLabel(this.selectedDate)}`;

    const label = document.getElementById('tasks-date-label');
    if (label) label.textContent = this.formatDateLabel(this.selectedDate);
  },

  async load() {
    try {
      const endpoint = this.selectedDate
        ? `/api/tasks?date=${this.selectedDate}`
        : '/api/tasks';
      this.tasks = await Api.get(endpoint);
      this.render();
    } catch (err) {
      console.error('Tasks load error:', err);
    }
  },

  render() {
    this.columns.forEach(status => {
      const container = document.getElementById(`column-${status}`);
      const filtered = this.tasks.filter(t => t.status === status);
      document.getElementById(`count-${status}`).textContent = filtered.length;

      if (!filtered.length) {
        container.innerHTML = '<div class="empty-state"><p>No tasks</p></div>';
        return;
      }

      container.innerHTML = filtered.map(t => this.renderCard(t)).join('');
      this.attachCardEvents(container);
      this.setupDragDrop(container, status);
    });
  },

  renderCard(task) {
    return `
      <div class="task-card" draggable="true" data-id="${task.id}">
        <div class="task-title">${this.escape(task.title)}</div>
        <div class="task-meta">
          <span class="priority-${task.priority}">${task.priority}</span>
          <div class="task-actions">
            <button class="btn-icon btn-sm edit-task" data-id="${task.id}" title="Edit">✎</button>
            <button class="btn-icon btn-sm delete-task" data-id="${task.id}" title="Delete">✕</button>
          </div>
        </div>
      </div>
    `;
  },

  attachCardEvents(container) {
    container.querySelectorAll('.edit-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openEditModal(btn.dataset.id);
      });
    });

    container.querySelectorAll('.delete-task').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.deleteTask(btn.dataset.id);
      });
    });
  },

  setupDragDrop(container, status) {
    container.querySelectorAll('.task-card').forEach(card => {
      card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', card.dataset.id);
        card.classList.add('dragging');
      });
      card.addEventListener('dragend', () => card.classList.remove('dragging'));
    });

    container.addEventListener('dragover', (e) => {
      e.preventDefault();
      container.style.background = 'var(--c-400)';
    });

    container.addEventListener('dragleave', () => {
      container.style.background = '';
    });

    container.addEventListener('drop', async (e) => {
      e.preventDefault();
      container.style.background = '';
      const taskId = e.dataTransfer.getData('text/plain');
      const task = this.tasks.find(t => t.id === taskId);
      if (task && task.status !== status) {
        await this.moveTask(taskId, status);
      }
    });
  },

  async moveTask(taskId, newStatus) {
    try {
      await Api.put(`/api/tasks/${taskId}`, { status: newStatus });
      await this.load();
    } catch (err) {
      console.error('Move task error:', err);
    }
  },

  openCreateModal() {
    document.getElementById('task-modal-title').textContent = 'New Task';
    document.getElementById('task-form').reset();
    document.getElementById('task-id').value = '';
    document.getElementById('task-modal').classList.add('active');
  },

  openEditModal(taskId) {
    const task = this.tasks.find(t => t.id === taskId);
    if (!task) return;

    document.getElementById('task-modal-title').textContent = 'Edit Task';
    document.getElementById('task-id').value = task.id;
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-status').value = task.status;
    document.getElementById('task-priority').value = task.priority;
    document.getElementById('task-modal').classList.add('active');
  },

  closeModal() {
    document.getElementById('task-modal').classList.remove('active');
  },

  async saveTask(e) {
    e.preventDefault();
    const id = document.getElementById('task-id').value;
    const payload = {
      title: document.getElementById('task-title').value.trim(),
      status: document.getElementById('task-status').value,
      priority: document.getElementById('task-priority').value,
    };

    if (this.selectedDate) {
      payload.date = this.selectedDate;
    }

    try {
      if (id) {
        await Api.put(`/api/tasks/${id}`, payload);
      } else {
        await Api.post('/api/tasks', payload);
      }
      this.closeModal();
      await this.load();
    } catch (err) {
      alert(err.message || 'Failed to save task');
    }
  },

  async deleteTask(taskId) {
    if (!confirm('Delete this task?')) return;
    try {
      await Api.delete(`/api/tasks/${taskId}`);
      await this.load();
    } catch (err) {
      console.error('Delete task error:', err);
    }
  },

  escape(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('tasks-page')) return;

  Tasks.initDateFilter();
  Tasks.load();

  document.getElementById('add-task-btn').addEventListener('click', () => Tasks.openCreateModal());
  document.getElementById('task-form').addEventListener('submit', (e) => Tasks.saveTask(e));
  document.getElementById('close-task-modal').addEventListener('click', () => Tasks.closeModal());
  document.getElementById('cancel-task-modal').addEventListener('click', () => Tasks.closeModal());
  document.getElementById('task-modal').addEventListener('click', (e) => {
    if (e.target.id === 'task-modal') Tasks.closeModal();
  });

  const clearBtn = document.getElementById('clear-date-filter');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      window.location.href = '/tasks.html';
    });
  }

  const calendarBtn = document.getElementById('back-to-calendar');
  if (calendarBtn) {
    calendarBtn.addEventListener('click', () => {
      window.location.href = '/calendar.html';
    });
  }
});
