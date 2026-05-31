const Notes = {
  notes: [],
  activeNoteId: null,
  saveTimeout: null,

  async load(query = '') {
    try {
      const endpoint = query ? `/api/notes?q=${encodeURIComponent(query)}` : '/api/notes';
      this.notes = await Api.get(endpoint);
      this.renderList();
    } catch (err) {
      console.error('Notes load error:', err);
    }
  },

  renderList() {
    const container = document.getElementById('notes-list');
    if (!this.notes.length) {
      container.innerHTML = '<div class="empty-state"><p>No notes yet</p></div>';
      return;
    }

    container.innerHTML = this.notes.map(n => `
      <div class="note-list-item ${n.id === this.activeNoteId ? 'active' : ''}" data-id="${n.id}">
        <div class="note-title">${this.escape(n.title)}</div>
        <div class="note-preview">${this.escape(n.content || 'No content')}</div>
        <div class="note-date">${this.formatDate(n.created_at)}</div>
      </div>
    `).join('');

    container.querySelectorAll('.note-list-item').forEach(el => {
      el.addEventListener('click', () => this.selectNote(el.dataset.id));
    });
  },

  selectNote(noteId) {
    this.activeNoteId = noteId;
    const note = this.notes.find(n => n.id === noteId);
    if (!note) return;

    document.getElementById('notes-empty').classList.add('hidden');
    document.getElementById('notes-editor').classList.remove('hidden');

    document.getElementById('note-title-input').value = note.title;
    document.getElementById('note-content-input').value = note.content || '';
    this.renderList();
  },

  createNote() {
    this.activeNoteId = null;
    document.getElementById('notes-empty').classList.add('hidden');
    document.getElementById('notes-editor').classList.remove('hidden');
    document.getElementById('note-title-input').value = '';
    document.getElementById('note-content-input').value = '';
    document.getElementById('note-title-input').focus();
    this.renderList();
  },

  scheduleSave() {
    clearTimeout(this.saveTimeout);
    this.saveTimeout = setTimeout(() => this.saveNote(), 800);
  },

  async saveNote() {
    const title = document.getElementById('note-title-input').value.trim();
    const content = document.getElementById('note-content-input').value;

    if (!title) return;

    try {
      if (this.activeNoteId) {
        await Api.put(`/api/notes/${this.activeNoteId}`, { title, content });
      } else {
        const note = await Api.post('/api/notes', { title, content });
        this.activeNoteId = note.id;
      }
      await this.load(document.getElementById('notes-search').value.trim());
      this.selectNote(this.activeNoteId);
    } catch (err) {
      console.error('Save note error:', err);
    }
  },

  async deleteNote() {
    if (!this.activeNoteId) return;
    if (!confirm('Delete this note?')) return;

    try {
      await Api.delete(`/api/notes/${this.activeNoteId}`);
      this.activeNoteId = null;
      document.getElementById('notes-editor').classList.add('hidden');
      document.getElementById('notes-empty').classList.remove('hidden');
      await this.load();
    } catch (err) {
      console.error('Delete note error:', err);
    }
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    });
  },

  escape(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('notes-page')) return;

  Notes.load();

  document.getElementById('new-note-btn').addEventListener('click', () => Notes.createNote());
  document.getElementById('delete-note-btn').addEventListener('click', () => Notes.deleteNote());
  document.getElementById('note-title-input').addEventListener('input', () => Notes.scheduleSave());
  document.getElementById('note-content-input').addEventListener('input', () => Notes.scheduleSave());

  let searchTimeout;
  document.getElementById('notes-search').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => Notes.load(e.target.value.trim()), 300);
  });
});
