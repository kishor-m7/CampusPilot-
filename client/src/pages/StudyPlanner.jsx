import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function StudyPlanner() {
  const [sessions, setSessions] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [syncing, setSyncing] = useState(false);

  // New session state
  const [title, setTitle] = useState('');
  const [courseId, setCourseId] = useState('');
  const [sessionType, setSessionType] = useState('deep_work');
  const [startTime, setStartTime] = useState('');
  const [duration, setDuration] = useState(60);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sess, crs] = await Promise.all([api.getStudySessions(), api.getCourses()]);
      setSessions(sess);
      setCourses(crs);
      if (crs.length > 0) setCourseId(crs[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (session) => {
    try {
      const updated = await api.updateStudySession(session.id, { completed: !session.completed });
      setSessions((prev) => prev.map((s) => (s.id === session.id ? updated : s)));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleSyncAlexa = async () => {
    try {
      setSyncing(true);
      const res = await api.syncPlanToAlexa('Daily Schedule');
      alert(`Synced ${res.synced_items_count} study sessions to Alexa!\n\n"${res.announcement_text}"`);
    } catch (err) {
      alert(`Alexa Sync error: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const start = startTime ? new Date(startTime).toISOString() : new Date().toISOString();
    const end = new Date(new Date(start).getTime() + duration * 60000).toISOString();

    try {
      setCreating(true);
      const created = await api.createStudySession({
        title,
        course_id: courseId,
        session_type: sessionType,
        start_time: start,
        end_time: end,
        duration_minutes: parseInt(duration),
        completed: false,
        alexa_synced: false
      });
      setSessions((prev) => [...prev, created]);
      setShowAddModal(false);
      setTitle('');
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const getSessionColor = (type) => {
    switch (type) {
      case 'lecture': return 'bg-primary-fixed text-primary';
      case 'deep_work': return 'bg-primary-container text-on-primary';
      case 'revision': return 'bg-tertiary-fixed text-on-tertiary-fixed';
      case 'lab': return 'bg-secondary-container text-on-secondary-container';
      default: return 'bg-surface-container-high text-on-surface';
    }
  };

  return (
    <div className="flex flex-col gap-space-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Study Planner & Timetable</h1>
          <p className="font-body-md text-on-surface-variant">
            Time-blocking schedule, academic lectures, and Alexa-synchronized focus blocks.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSyncAlexa}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-surface-container-high text-on-surface hover:bg-surface-container-highest transition-all font-title-sm shadow-sm"
          >
            <span className="material-symbols-outlined text-base text-primary">speaker</span>
            <span>{syncing ? 'Syncing...' : 'Sync to Alexa Routine'}</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm hover:bg-primary-container transition-all shadow-sm"
          >
            <span className="material-symbols-outlined text-base">add</span>
            <span>Add Session</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-12 flex justify-center text-on-surface-variant font-body-md">
          Loading schedule blocks...
        </div>
      ) : sessions.length === 0 ? (
        <div className="p-8 rounded-2xl bg-surface-container-low text-center flex flex-col items-center gap-2">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant">calendar_today</span>
          <p className="font-title-sm text-on-surface">No study sessions scheduled yet.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="p-space-md rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                <button
                  onClick={() => handleToggleComplete(s)}
                  className={`w-6 h-6 rounded flex items-center justify-center transition-all mt-1 ${
                    s.completed ? 'bg-secondary text-on-secondary' : 'border-2 border-outline hover:border-primary'
                  }`}
                >
                  {s.completed && <span className="material-symbols-outlined text-sm font-bold">check</span>}
                </button>

                <div className="flex flex-col min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface font-label-sm text-xs font-bold">
                      {s.course_code || 'STUDY'}
                    </span>
                    <h3 className={`font-title-sm font-bold text-on-surface ${s.completed ? 'line-through text-on-surface-variant' : ''}`}>
                      {s.title}
                    </h3>
                  </div>

                  <p className="font-body-sm text-on-surface-variant text-xs mt-1">
                    {new Date(s.start_time).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })} • {new Date(s.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} – {new Date(s.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} ({s.duration_minutes}m)
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase font-label-sm ${getSessionColor(s.session_type)}`}>
                  {s.session_type.replace('_', ' ')}
                </span>
                {s.alexa_synced && (
                  <span className="p-1 rounded text-primary" title="Synced to Alexa Morning Briefing">
                    <span className="material-symbols-outlined text-base">speaker</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Session Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-2xl p-6 border border-surface-container">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container">
              <h2 className="font-title-md font-bold text-on-surface">Schedule Study / Timetable Block</h2>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <form onSubmit={handleCreate} className="flex flex-col gap-4 mt-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Session Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Deep Work: Buddy Memory Allocator"
                  className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Course</label>
                  <select
                    value={courseId}
                    onChange={(e) => setCourseId(e.target.value)}
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
                  <label className="block text-xs font-semibold text-on-surface mb-1">Session Type</label>
                  <select
                    value={sessionType}
                    onChange={(e) => setSessionType(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  >
                    <option value="deep_work">Deep Work</option>
                    <option value="lecture">Lecture / Class</option>
                    <option value="revision">Revision / Drill</option>
                    <option value="lab">Lab Session</option>
                    <option value="group_study">Group Study</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Start Time</label>
                  <input
                    type="datetime-local"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>
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
                  {creating ? 'Saving...' : 'Add Session'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
