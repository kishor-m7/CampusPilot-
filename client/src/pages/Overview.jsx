import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Overview({ onNavigate, onTriggerPrompt }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [syncingAlexa, setSyncingAlexa] = useState(false);
  const [alexaNotice, setAlexaNotice] = useState(null);

  // Pomodoro timer state
  const [pomoSeconds, setPomoSeconds] = useState(25 * 60);
  const [pomoActive, setPomoActive] = useState(false);

  useEffect(() => {
    loadOverview();
  }, []);

  useEffect(() => {
    let timer = null;
    if (pomoActive && pomoSeconds > 0) {
      timer = setInterval(() => setPomoSeconds((s) => s - 1), 1000);
    } else if (pomoSeconds === 0) {
      setPomoActive(false);
      alert('Focus session complete! Take a 5-minute break.');
    }
    return () => clearInterval(timer);
  }, [pomoActive, pomoSeconds]);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getOverview();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSession = async (session) => {
    try {
      const updated = await api.updateStudySession(session.id, { completed: !session.completed });
      setData((prev) => ({
        ...prev,
        today_sessions: prev.today_sessions.map((s) => (s.id === session.id ? updated : s))
      }));
    } catch (err) {
      console.error(err);
    }
  };

  const handlePlanMyDay = async () => {
    try {
      setSyncingAlexa(true);
      const res = await api.syncPlanToAlexa('Morning Briefing');
      setAlexaNotice(res.announcement_text);
      setTimeout(() => setAlexaNotice(null), 8000);
    } catch (err) {
      alert(`Alexa Sync error: ${err.message}`);
    } finally {
      setSyncingAlexa(false);
    }
  };

  const formatPomoTime = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="font-body-md text-on-surface-variant">Connecting to CampusPilot Database...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-error-container text-on-error-container flex flex-col items-start gap-4 my-6">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-2xl text-error">error</span>
          <h2 className="font-title-md font-bold">Failed to connect to backend</h2>
        </div>
        <p className="font-body-md">{error}</p>
        <button
          onClick={loadOverview}
          className="px-4 py-2 rounded-lg bg-error text-on-error font-title-sm hover:opacity-90"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const metrics = data?.metrics || {};
  const sessions = data?.today_sessions || [];
  const assignments = data?.recent_assignments || [];
  const exams = data?.upcoming_exams || [];

  return (
    <div className="flex flex-col gap-space-xl">
      {/* Header Area */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
        <div className="flex flex-col">
          <div className="flex items-center gap-space-xs">
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
              Good day, {data?.student_name || 'Kishor'}
            </h1>
            <span className="text-2xl animate-bounce">👋</span>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant mt-0.5">
            Your unified academic command center & Alexa co-pilot.
          </p>
        </div>

        <div className="flex items-center gap-space-md self-start md:self-auto flex-wrap">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-container-low text-on-surface-variant font-label-md text-label-md">
            <span className="material-symbols-outlined text-sm leading-none text-surface-tint">calendar_month</span>
            <span>{data?.semester || 'Sem 6'} • Week 8</span>
          </div>

          <button
            onClick={handlePlanMyDay}
            disabled={syncingAlexa}
            className="group relative inline-flex items-center gap-2 px-space-md py-2.5 rounded-lg bg-primary-container text-on-primary font-title-sm text-title-sm shadow-sm hover:shadow-md hover:bg-primary transition-all duration-200 active:scale-[0.98] disabled:opacity-50"
            type="button"
          >
            <span className="material-symbols-outlined text-base leading-none transition-transform duration-300 group-hover:rotate-12">
              auto_awesome
            </span>
            <span>{syncingAlexa ? 'Syncing to Alexa...' : 'Plan My Day'}</span>
          </button>
        </div>
      </div>

      {/* Alexa Voice Sync Announcement Alert Banner */}
      {alexaNotice && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-primary to-primary-container text-on-primary shadow-lg flex items-start justify-between gap-4 animate-in fade-in duration-300">
          <div className="flex items-start gap-3">
            <span className="material-symbols-outlined text-2xl text-primary-fixed">speaker</span>
            <div>
              <span className="font-title-sm block text-primary-fixed font-bold uppercase tracking-wider text-xs">
                Alexa Copilot Synced
              </span>
              <p className="font-body-md mt-0.5">{alexaNotice}</p>
            </div>
          </div>
          <button onClick={() => setAlexaNotice(null)} className="p-1 hover:opacity-75">
            <span className="material-symbols-outlined text-sm">close</span>
          </button>
        </div>
      )}

      {/* Top Metric Summary Cards (4-column grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md">
        {/* Metric 1: Pending Assignments */}
        <div
          onClick={() => onNavigate('assignments')}
          className="flex flex-col justify-between p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer border border-surface-container-low"
        >
          <div className="flex items-start justify-between">
            <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-xl">assignment_late</span>
            </div>
            {metrics.urgent_assignments_count > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-label-sm text-label-sm font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-error"></span>
                {metrics.urgent_assignments_count} urgent
              </span>
            )}
          </div>
          <div className="mt-4">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block">
              Pending Assignments
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {metrics.pending_assignments_count} Tasks
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">Click to view deadlines</p>
          </div>
        </div>

        {/* Metric 2: Upcoming Exams */}
        <div
          onClick={() => onNavigate('exams')}
          className="flex flex-col justify-between p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer border border-surface-container-low"
        >
          <div className="flex items-start justify-between">
            <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center text-tertiary">
              <span className="material-symbols-outlined text-xl">school</span>
            </div>
            {metrics.next_exam_days_left !== null && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-label-sm font-semibold">
                <span className="material-symbols-outlined text-xs leading-none">timelapse</span>
                In {metrics.next_exam_days_left} days
              </span>
            )}
          </div>
          <div className="mt-4">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block">
              Upcoming Exams
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {metrics.upcoming_exams_count} Exams
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 truncate">
              {metrics.next_exam_title || 'None scheduled'}
            </p>
          </div>
        </div>

        {/* Metric 3: Study Hours */}
        <div
          onClick={() => onNavigate('progress')}
          className="flex flex-col justify-between p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer border border-surface-container-low"
        >
          <div className="flex items-start justify-between">
            <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center text-surface-tint">
              <span className="material-symbols-outlined text-xl">schedule</span>
            </div>
            <span className="font-label-sm text-label-sm px-2 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed font-semibold">
              {metrics.study_target_percentage}% target
            </span>
          </div>
          <div className="mt-4">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block">
              Study Hours This Week
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {metrics.weekly_study_hours} hrs
              </span>
            </div>
            <div className="w-full bg-surface-container h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-primary-container h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, metrics.study_target_percentage)}%` }}
              ></div>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1.5">
              Target: {metrics.weekly_target_hours} hrs
            </p>
          </div>
        </div>

        {/* Metric 4: Tasks Completed */}
        <div
          onClick={() => onNavigate('assignments')}
          className="flex flex-col justify-between p-space-md rounded-xl bg-surface-container-lowest shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer border border-surface-container-low"
        >
          <div className="flex items-start justify-between">
            <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center text-secondary">
              <span className="material-symbols-outlined text-xl">check_circle</span>
            </div>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-label-sm font-semibold">
              <span className="material-symbols-outlined text-xs leading-none">arrow_upward</span>
              Active Pace
            </span>
          </div>
          <div className="mt-4">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider block">
              Tasks Completed
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="font-headline-lg text-headline-lg text-on-surface font-bold">
                {metrics.tasks_completed_count} Done
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">Academic streak maintained</p>
          </div>
        </div>
      </div>

      {/* Split Grid: 8 cols left / 4 cols right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        {/* LEFT COLUMN: Academic Overview (8 Cols) */}
        <div className="lg:col-span-8 flex flex-col gap-space-lg min-w-0">
          {/* Section A: Today's Study Plan */}
          <div className="p-space-lg rounded-xl bg-surface-container-lowest shadow-sm flex flex-col border border-surface-container-low">
            <div className="flex items-center justify-between pb-space-sm mb-space-sm border-b border-surface-container-low">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-primary"></span>
                <h2 className="font-title-md text-title-md text-on-surface font-bold">Today's Study Plan</h2>
              </div>
              <button
                onClick={() => onNavigate('study-planner')}
                className="text-primary hover:underline font-title-sm text-sm"
              >
                View Full Planner
              </button>
            </div>

            <div className="flex flex-col gap-3">
              {sessions.length === 0 ? (
                <p className="text-on-surface-variant font-body-sm py-4 text-center">
                  No sessions scheduled for today. Click "Plan My Day" to generate an optimized routine.
                </p>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-3.5 rounded-lg bg-surface-container-low transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <button
                        onClick={() => handleToggleSession(session)}
                        className={`w-5 h-5 rounded flex items-center justify-center transition-all ${
                          session.completed
                            ? 'bg-secondary text-on-secondary'
                            : 'border-2 border-outline hover:border-primary'
                        }`}
                      >
                        {session.completed && (
                          <span className="material-symbols-outlined text-sm font-bold">check</span>
                        )}
                      </button>
                      <div className="flex flex-col min-w-0">
                        <span
                          className={`font-title-sm text-title-sm truncate ${
                            session.completed ? 'line-through text-on-surface-variant' : 'text-on-surface font-semibold'
                          }`}
                        >
                          {session.title}
                        </span>
                        <span className="font-body-sm text-body-sm text-on-surface-variant">
                          {session.course_code ? `${session.course_code} • ` : ''}
                          {session.duration_minutes} mins • {session.session_type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    {session.alexa_synced && (
                      <span
                        className="material-symbols-outlined text-sm text-primary"
                        title="Synced to Alexa device"
                      >
                        speaker
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Section B: Urgent Coursework Deliverables */}
          <div className="p-space-lg rounded-xl bg-surface-container-lowest shadow-sm flex flex-col border border-surface-container-low">
            <div className="flex items-center justify-between pb-space-sm mb-space-sm border-b border-surface-container-low">
              <h2 className="font-title-md text-title-md text-on-surface font-bold">Upcoming Assignments</h2>
              <button
                onClick={() => onNavigate('assignments')}
                className="text-primary hover:underline font-title-sm text-sm"
              >
                View All ({assignments.length})
              </button>
            </div>

            <div className="flex flex-col gap-3">
              {assignments.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-xl bg-surface-container-low flex items-center justify-between gap-3"
                >
                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface font-label-sm text-xs font-bold">
                        {item.course_code || 'CS'}
                      </span>
                      <span className="font-title-sm text-on-surface font-semibold truncate">{item.title}</span>
                    </div>
                    <span className="font-body-sm text-on-surface-variant mt-1">
                      Due: {item.due_date ? new Date(item.due_date).toLocaleDateString() : 'Upcoming'} • {item.weight_percentage}% of grade
                    </span>
                  </div>

                  <span
                    className={`px-2.5 py-1 rounded-full font-label-sm text-xs font-semibold uppercase ${
                      item.priority === 'urgent'
                        ? 'bg-error-container text-on-error-container'
                        : item.priority === 'medium'
                        ? 'bg-tertiary-container/30 text-tertiary'
                        : 'bg-secondary-container text-on-secondary-container'
                    }`}
                  >
                    {item.priority}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Pomodoro & Fast Copilot Triggers (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-space-lg">
          {/* Pomodoro Focus Timer Widget */}
          <div className="p-space-lg rounded-xl bg-surface-container-lowest shadow-sm flex flex-col gap-space-md border border-surface-container-low">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-xl">timer</span>
                <h3 className="font-title-md text-title-md text-on-surface font-bold">Focus Timer</h3>
              </div>
              <span className="font-label-sm text-label-sm px-2 py-0.5 rounded-full bg-primary-fixed text-primary font-semibold">
                Pomodoro
              </span>
            </div>

            <div className="flex flex-col items-center justify-center py-4 bg-surface-container-low rounded-xl">
              <span className="text-4xl font-headline-lg font-bold text-on-surface tracking-wider font-code-inline">
                {formatPomoTime(pomoSeconds)}
              </span>
              <span className="font-body-sm text-on-surface-variant mt-1">25-min Deep Focus Block</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPomoActive(!pomoActive)}
                className={`flex-1 py-2.5 rounded-lg font-title-sm text-center shadow-sm transition-all ${
                  pomoActive
                    ? 'bg-surface-container-high text-on-surface hover:bg-surface-container-highest'
                    : 'bg-primary text-on-primary hover:bg-primary-container'
                }`}
              >
                {pomoActive ? 'Pause' : 'Start Focus'}
              </button>
              <button
                onClick={() => {
                  setPomoActive(false);
                  setPomoSeconds(25 * 60);
                }}
                className="p-2.5 rounded-lg bg-surface-container-low text-on-surface-variant hover:text-on-surface"
                title="Reset Timer"
              >
                <span className="material-symbols-outlined text-lg leading-none">refresh</span>
              </button>
            </div>
          </div>

          {/* Alexa Copilot Prompt Shortcuts */}
          <div className="p-space-lg rounded-xl bg-gradient-to-br from-surface-container-low to-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-3">
            <div className="flex items-center gap-2 text-primary font-bold">
              <span className="material-symbols-outlined text-lg">auto_awesome</span>
              <h3 className="font-title-sm text-on-surface">Ask CampusPilot</h3>
            </div>
            <p className="font-body-sm text-on-surface-variant">One-click AI queries backed by real MCP tools:</p>

            <button
              onClick={() => onTriggerPrompt('What are my upcoming assignment deadlines and what should I work on first?')}
              className="text-left p-2.5 rounded-lg bg-surface-container-lowest hover:bg-primary/5 text-on-surface font-body-sm transition-colors border border-surface-container flex items-center justify-between group"
            >
              <span>"What should I study first?"</span>
              <span className="material-symbols-outlined text-xs text-primary group-hover:translate-x-1 transition-transform">
                arrow_forward
              </span>
            </button>

            <button
              onClick={() => onTriggerPrompt('Can you draft a 3-day revision plan for Cybersecurity before the midterm?')}
              className="text-left p-2.5 rounded-lg bg-surface-container-lowest hover:bg-primary/5 text-on-surface font-body-sm transition-colors border border-surface-container flex items-center justify-between group"
            >
              <span>"Draft 3-day revision plan"</span>
              <span className="material-symbols-outlined text-xs text-primary group-hover:translate-x-1 transition-transform">
                arrow_forward
              </span>
            </button>

            <button
              onClick={() => onTriggerPrompt('Give me a 3-question oral practice quiz for System Security.')}
              className="text-left p-2.5 rounded-lg bg-surface-container-lowest hover:bg-primary/5 text-on-surface font-body-sm transition-colors border border-surface-container flex items-center justify-between group"
            >
              <span>"Start oral practice drill"</span>
              <span className="material-symbols-outlined text-xs text-primary group-hover:translate-x-1 transition-transform">
                arrow_forward
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
