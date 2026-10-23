import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Exams() {
  const [exams, setExams] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New exam form
  const [title, setTitle] = useState('');
  const [courseId, setCourseId] = useState('');
  const [examDate, setExamDate] = useState('');
  const [location, setLocation] = useState('');
  const [targetScore, setTargetScore] = useState(90);
  const [notes, setNotes] = useState('');
  const [unitsInput, setUnitsInput] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [exList, crs] = await Promise.all([api.getExams(), api.getCourses()]);
      setExams(exList);
      setCourses(crs);
      if (crs.length > 0) setCourseId(crs[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUnit = async (exam, unitIndex) => {
    const updatedUnits = exam.syllabus_units.map((u, i) =>
      i === unitIndex ? { ...u, covered: !u.covered } : u
    );

    try {
      const updated = await api.updateExam(exam.id, { syllabus_units: updatedUnits });
      setExams((prev) => prev.map((e) => (e.id === exam.id ? updated : e)));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const parsedUnits = unitsInput
      .split('\n')
      .map((u) => u.trim())
      .filter(Boolean)
      .map((name) => ({ name, covered: false }));

    try {
      setCreating(true);
      const created = await api.createExam({
        title,
        course_id: courseId,
        exam_date: examDate || new Date(Date.now() + 14 * 86400000).toISOString(),
        location,
        target_score: parseFloat(targetScore) || 90,
        notes,
        syllabus_units: parsedUnits
      });
      setExams((prev) => [...prev, created]);
      setShowAddModal(false);
      setTitle('');
      setNotes('');
      setUnitsInput('');
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="flex flex-col gap-space-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Exams & Revision Checklists</h1>
          <p className="font-body-md text-on-surface-variant">
            Track examination countdowns, target milestones, and syllabus unit readiness.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm hover:bg-primary-container transition-all shadow-sm"
        >
          <span className="material-symbols-outlined text-base">add</span>
          <span>Schedule Exam</span>
        </button>
      </div>

      {loading ? (
        <div className="py-12 flex justify-center text-on-surface-variant font-body-md">
          Loading exam schedules...
        </div>
      ) : exams.length === 0 ? (
        <div className="p-8 rounded-2xl bg-surface-container-low text-center flex flex-col items-center gap-2">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant">school</span>
          <p className="font-title-sm text-on-surface">No exams scheduled currently.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-space-lg">
          {exams.map((exam) => {
            const coveredCount = exam.syllabus_units.filter((u) => u.covered).length;
            const totalUnits = exam.syllabus_units.length;
            const prepPct = totalUnits > 0 ? Math.round((coveredCount / totalUnits) * 100) : 0;

            return (
              <div
                key={exam.id}
                className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-space-md"
              >
                {/* Header banner */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="px-2 py-0.5 rounded bg-surface-container-high text-on-surface font-label-sm text-xs font-bold">
                      {exam.course_code || 'EXAM'}
                    </span>
                    <h2 className="font-title-md font-bold text-on-surface mt-1">{exam.title}</h2>
                    <p className="font-body-sm text-on-surface-variant text-xs mt-0.5">
                      {new Date(exam.exam_date).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })} • {exam.location || 'Campus Hall'}
                    </p>
                  </div>

                  <span className="px-3 py-1 rounded-full bg-tertiary-fixed text-on-tertiary-fixed font-title-sm text-xs font-bold flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs">timelapse</span>
                    {exam.days_left !== undefined ? `${exam.days_left} Days Left` : 'Upcoming'}
                  </span>
                </div>

                {/* Preparation progress */}
                <div className="flex flex-col gap-1.5 p-3 rounded-xl bg-surface-container-low">
                  <div className="flex justify-between text-xs font-semibold">
                    <span>Syllabus Coverage ({coveredCount}/{totalUnits})</span>
                    <span>{prepPct}% Ready</span>
                  </div>
                  <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-secondary h-full rounded-full transition-all duration-300"
                      style={{ width: `${prepPct}%` }}
                    ></div>
                  </div>
                </div>

                {/* Syllabus unit checklist */}
                <div className="flex flex-col gap-2">
                  <span className="font-label-md text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                    Syllabus Units
                  </span>
                  {exam.syllabus_units.map((unit, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleToggleUnit(exam, idx)}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-low transition-colors cursor-pointer"
                    >
                      <button
                        className={`w-4 h-4 rounded flex items-center justify-center transition-all ${
                          unit.covered ? 'bg-secondary text-on-secondary' : 'border border-outline'
                        }`}
                      >
                        {unit.covered && <span className="material-symbols-outlined text-xs font-bold">check</span>}
                      </button>
                      <span className={`text-xs ${unit.covered ? 'line-through text-on-surface-variant' : 'text-on-surface font-medium'}`}>
                        {unit.name}
                      </span>
                    </div>
                  ))}
                </div>

                {exam.notes && (
                  <p className="text-xs text-on-surface-variant bg-surface-container-low p-2.5 rounded-lg border-l-2 border-primary">
                    <strong>Note:</strong> {exam.notes}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add Exam Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-2xl p-6 border border-surface-container">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container">
              <h2 className="font-title-md font-bold text-on-surface">Schedule Upcoming Exam</h2>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <form onSubmit={handleCreate} className="flex flex-col gap-4 mt-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Exam Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Midterm: System Security & Cryptography"
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
                  <label className="block text-xs font-semibold text-on-surface mb-1">Exam Date & Time</label>
                  <input
                    type="datetime-local"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Auditorium Hall B"
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-on-surface mb-1">Target Score (%)</label>
                  <input
                    type="number"
                    value={targetScore}
                    onChange={(e) => setTargetScore(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">
                  Syllabus Units (One per line)
                </label>
                <textarea
                  value={unitsInput}
                  onChange={(e) => setUnitsInput(e.target.value)}
                  rows="3"
                  placeholder="Public Key Cryptography & RSA&#10;Zero Trust Architecture&#10;Buffer Overflows & Exploit Chains"
                  className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm font-code-inline"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface mb-1">Special Instructions / Notes</label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Formula sheet permitted, bring scientific calculator..."
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
                  {creating ? 'Scheduling...' : 'Save Exam'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
