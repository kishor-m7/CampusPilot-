import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Reminders() {
  const [reminders, setReminders] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // New reminder form
  const [title, setTitle] = useState('');
  const [courseId, setCourseId] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rems, crs] = await Promise.all([api.getReminders(), api.getCourses()]);
      setReminders(rems);
      setCourses(crs);
      if (crs.length > 0) setCourseId(crs[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (item) => {
    const nextStatus = item.status === 'completed' ? 'pending' : 'completed';
    try {
      const updated = await api.updateReminder(item.id, { status: nextStatus });
      setReminders((prev) => prev.map((r) => (r.id === item.id ? updated : r)));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this reminder?')) return;
    try {
      await api.deleteReminder(id);
      setReminders((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      setCreating(true);
      const created = await api.createReminder({
        title,
        course_id: courseId || null,
        priority,
        due_date: dueDate ? new Date(dueDate).toISOString() : new Date().toISOString()
      });
      setReminders((prev) => [created, ...prev]);
      setShowAddModal(false);
      setTitle('');
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const filtered = reminders.filter((r) => {
    if (filter === 'all') return true;
    return r.status === filter;
  });

  return (
    <div className="flex flex-col gap-space-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Academic Reminders</h1>
          <p className="font-body-md text-on-surface-variant">
            Nudges for assignments, lab submissions, and Alexa-assisted audio alerts.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm hover:bg-primary-container transition-all shadow-sm"
        >
          <span className="material-symbols-outlined text-base">add_alert</span>
          <span>Add Reminder</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 p-1.5 rounded-xl bg-surface-container-low max-w-fit">
        {['all', 'pending', 'completed'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-3.5 py-1.5 rounded-lg font-title-sm text-xs capitalize transition-all ${
              filter === tab
                ? 'bg-surface-container-lowest text-on-surface font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-12 flex justify-center text-on-surface-variant font-body-md">
          Loading reminders...
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-8 rounded-2xl bg-surface-container-low text-center flex flex-col items-center gap-2">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant">notifications_none</span>
          <p className="font-title-sm text-on-surface">No reminders found.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="p-space-md rounded-xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex items-center justify-between gap-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 min-w-0">
                <button
                  onClick={() => handleToggle(item)}
                  className={`w-6 h-6 rounded flex items-center justify-center transition-all ${
                    item.status === 'completed'
                      ? 'bg-secondary text-on-secondary'
                      : 'border-2 border-outline hover:border-primary'
                  }`}
                >
                  {item.status === 'completed' && (
                    <span className="material-symbols-outlined text-sm font-bold">check</span>
                  )}
                </button>

                <div className="flex flex-col min-w-0">
                  <span
                    className={`font-title-sm text-on-surface font-semibold truncate ${
                      item.status === 'completed' ? 'line-through text-on-surface-variant' : ''
                    }`}
                  >
                    {item.title}
                  </span>
                  <span className="font-body-sm text-on-surface-variant text-xs mt-0.5">
                    {item.course_code ? `${item.course_code} • ` : ''}Due: {item.due_date ? new Date(item.due_date).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Soon'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded-full font-label-sm text-[11px] font-bold uppercase ${
                    item.priority === 'urgent'
                      ? 'bg-error-container text-on-error-container'
                      : item.priority === 'medium'
                      ? 'bg-tertiary-fixed text-on-tertiary-fixed'
                      : 'bg-secondary-container text-on-secondary-container'
                  }`}
                >
                  {item.priority}
                </span>

                <button
                  onClick={() => handleDelete(item.id)}
                  className="p-1 rounded text-on-surface-variant hover:text-error"
                  title="Delete"
                >
                  <span className="material-symbols-outlined text-base">delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Reminder Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-2xl p-6 border border-surface-container">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container">
              <h2 className="font-title-md font-bold text-on-surface">Create Reminder</h2>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <form onSubmit={handleCreate} className="flex flex-col gap-4 mt-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Reminder Text</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Review RSA proof before quiz"
                  className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Related Course</label>
                  <select
                    value={courseId}
                    onChange={(e) => setCourseId(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  >
                    <option value="">None (General)</option>
                    {courses.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.code} - {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Trigger Date & Time</label>
                <input
                  type="datetime-local"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg text-sm text-on-surface-variant hover:bg-surface-container"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 rounded-lg text-sm bg-primary text-on-primary font-title-sm hover:bg-primary-container"
                >
                  {creating ? 'Saving...' : 'Set Reminder'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
