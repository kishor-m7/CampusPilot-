import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Assignments() {
  const [assignments, setAssignments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New assignment form state
  const [newTitle, setNewTitle] = useState('');
  const [newCourseId, setNewCourseId] = useState('');
  const [newDueDate, setNewDueDate] = useState('');
  const [newPriority, setNewPriority] = useState('medium');
  const [newWeight, setNewWeight] = useState(10);
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [assns, crs] = await Promise.all([api.getAssignments(), api.getCourses()]);
      setAssignments(assns);
      setCourses(crs);
      if (crs.length > 0) setNewCourseId(crs[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (item) => {
    const nextStatus = item.status === 'completed' ? 'pending' : 'completed';
    try {
      const updated = await api.updateAssignment(item.id, { status: nextStatus });
      setAssignments((prev) => prev.map((a) => (a.id === item.id ? updated : a)));
    } catch (err) {
      alert(`Failed to update assignment: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this assignment?')) return;
    try {
      await api.deleteAssignment(id);
      setAssignments((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      setCreating(true);
      const created = await api.createAssignment({
        title: newTitle,
        course_id: newCourseId,
        due_date: newDueDate || new Date(Date.now() + 7 * 86400000).toISOString(),
        priority: newPriority,
        weight_percentage: parseFloat(newWeight) || 10,
        description: newDesc,
        status: 'pending'
      });
      setAssignments((prev) => [created, ...prev]);
      setShowAddModal(false);
      setNewTitle('');
      setNewDesc('');
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const filtered = assignments.filter((a) => {
    if (filter === 'all') return true;
    return a.status === filter;
  });

  return (
    <div className="flex flex-col gap-space-lg">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Assignments & Coursework</h1>
          <p className="font-body-md text-on-surface-variant">
            Track deadlines, priority tasks, and calculate course grade weightage.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm hover:bg-primary-container transition-all shadow-sm"
        >
          <span className="material-symbols-outlined text-base">add</span>
          <span>New Assignment</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 p-1.5 rounded-xl bg-surface-container-low max-w-fit overflow-x-auto">
        {['all', 'pending', 'in_progress', 'completed'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-3.5 py-1.5 rounded-lg font-title-sm text-xs capitalize transition-all ${
              filter === tab
                ? 'bg-surface-container-lowest text-on-surface font-bold shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Assignments List */}
      {loading ? (
        <div className="py-12 flex justify-center text-on-surface-variant font-body-md">
          Loading coursework assignments...
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-8 rounded-2xl bg-surface-container-low text-center flex flex-col items-center gap-2">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant">checklist</span>
          <p className="font-title-sm text-on-surface">No assignments match this filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="p-space-md rounded-xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col justify-between gap-3 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleStatus(item)}
                    className={`w-6 h-6 rounded flex items-center justify-center transition-all mt-0.5 ${
                      item.status === 'completed'
                        ? 'bg-secondary text-on-secondary'
                        : 'border-2 border-outline hover:border-primary'
                    }`}
                  >
                    {item.status === 'completed' && (
                      <span className="material-symbols-outlined text-sm font-bold">check</span>
                    )}
                  </button>

                  <div className="flex flex-col">
                    <span
                      className={`font-title-sm text-on-surface font-semibold ${
                        item.status === 'completed' ? 'line-through text-on-surface-variant' : ''
                      }`}
                    >
                      {item.title}
                    </span>
                    <span className="font-body-sm text-on-surface-variant text-xs mt-0.5">
                      {item.course_code || 'General'} • Due: {item.due_date ? new Date(item.due_date).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>

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
              </div>

              {item.description && (
                <p className="font-body-sm text-on-surface-variant/80 text-xs pl-9">
                  {item.description}
                </p>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-surface-container-low pl-9 text-xs text-on-surface-variant">
                <span>Weight: {item.weight_percentage}%</span>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="p-1 rounded text-error hover:bg-error-container/20 transition-colors"
                  title="Delete Assignment"
                >
                  <span className="material-symbols-outlined text-sm">delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Assignment Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-2xl p-6 border border-surface-container">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container">
              <h2 className="font-title-md font-bold text-on-surface">Add New Assignment</h2>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <form onSubmit={handleCreate} className="flex flex-col gap-4 mt-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Assignment Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Distributed Consensus Mock"
                  className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Course</label>
                  <select
                    value={newCourseId}
                    onChange={(e) => setNewCourseId(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  >
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
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Due Date</label>
                  <input
                    type="date"
                    value={newDueDate}
                    onChange={(e) => setNewDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Grade Weight (%)</label>
                  <input
                    type="number"
                    value={newWeight}
                    onChange={(e) => setNewWeight(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Description / Notes</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  rows="2"
                  placeholder="Requirements, rubric guidelines..."
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
                  {creating ? 'Saving...' : 'Save Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
