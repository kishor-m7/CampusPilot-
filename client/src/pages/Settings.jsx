import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Settings({ onProfileUpdated }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [major, setMajor] = useState('');
  const [semester, setSemester] = useState('');
  const [targetGpa, setTargetGpa] = useState(3.90);
  const [weeklyTargetHours, setWeeklyTargetHours] = useState(24.0);
  const [responseStyle, setResponseStyle] = useState('concise');
  const [syllabusParsing, setSyllabusParsing] = useState(true);
  const [voiceConfirmations, setVoiceConfirmations] = useState(true);
  const [alexaSync, setAlexaSync] = useState(true);

  // LMS toggles
  const [canvasSynced, setCanvasSynced] = useState(true);
  const [gClassroomSynced, setGClassroomSynced] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const res = await api.getProfile();
      setProfile(res);
      setFullName(res.full_name || '');
      setEmail(res.email || '');
      setMajor(res.major || '');
      setSemester(res.semester || '');
      setTargetGpa(res.target_gpa || 3.90);
      setWeeklyTargetHours(res.weekly_target_hours || 24.0);
      setResponseStyle(res.ai_preferences?.response_style || 'concise');
      setSyllabusParsing(res.ai_preferences?.syllabus_parsing ?? true);
      setVoiceConfirmations(res.ai_preferences?.voice_confirmations ?? true);
      setAlexaSync(res.alexa_sync_enabled ?? true);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      const updated = await api.updateProfile({
        full_name: fullName,
        email,
        major,
        semester,
        target_gpa: parseFloat(targetGpa),
        weekly_target_hours: parseFloat(weeklyTargetHours),
        ai_preferences: {
          response_style: responseStyle,
          syllabus_parsing: syllabusParsing,
          voice_confirmations: voiceConfirmations
        },
        alexa_sync_enabled: alexaSync
      });
      setProfile(updated);
      if (onProfileUpdated) onProfileUpdated(updated);
      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 4000);
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="py-12 flex justify-center text-on-surface-variant">Loading preferences...</div>;
  }

  return (
    <div className="flex flex-col gap-space-lg max-w-4xl">
      <div>
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Settings & Preferences</h1>
        <p className="font-body-md text-on-surface-variant">
          Configure your academic profile, AI assistant response parameters, and connected LMS feeds.
        </p>
      </div>

      {savedNotice && (
        <div className="p-3.5 rounded-xl bg-secondary-container text-on-secondary-container font-title-sm text-sm flex items-center gap-2 animate-in fade-in">
          <span className="material-symbols-outlined text-base">check_circle</span>
          <span>Profile & AI preferences saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="flex flex-col gap-space-lg">
        {/* Academic Profile Section */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-4">
          <h2 className="font-title-md font-bold text-on-surface border-b border-surface-container-low pb-2">
            Student Academic Identity
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">University Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Degree / Major</label>
              <input
                type="text"
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Current Semester</label>
              <input
                type="text"
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Target GPA</label>
              <input
                type="number"
                step="0.01"
                value={targetGpa}
                onChange={(e) => setTargetGpa(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Weekly Target Study Hours</label>
              <input
                type="number"
                step="0.5"
                value={weeklyTargetHours}
                onChange={(e) => setWeeklyTargetHours(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              />
            </div>
          </div>
        </div>

        {/* AI & Alexa Copilot Configuration */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-4">
          <h2 className="font-title-md font-bold text-on-surface border-b border-surface-container-low pb-2">
            AI Assistant & Alexa Behaviors
          </h2>

          <div className="flex flex-col gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface mb-1">Response Style</label>
              <select
                value={responseStyle}
                onChange={(e) => setResponseStyle(e.target.value)}
                className="w-full sm:w-64 px-3 py-2 rounded-lg bg-surface-container-low border border-surface-container text-sm"
              >
                <option value="concise">Concise & High-Yield (Recommended for Alexa)</option>
                <option value="detailed">In-depth Editorial with Academic Explanations</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-surface-container-low">
              <div>
                <span className="font-title-sm text-sm font-semibold text-on-surface block">
                  Automatic Syllabus & Rubric Ingestion
                </span>
                <span className="font-body-sm text-xs text-on-surface-variant">
                  Allow CampusPilot to parse course units for high-yield exam topics
                </span>
              </div>
              <input
                type="checkbox"
                checked={syllabusParsing}
                onChange={(e) => setSyllabusParsing(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-surface-container-low">
              <div>
                <span className="font-title-sm text-sm font-semibold text-on-surface block">
                  Voice Confirmation Safety Gate
                </span>
                <span className="font-body-sm text-xs text-on-surface-variant">
                  Require explicit confirmation before rescheduling or deleting study slots
                </span>
              </div>
              <input
                type="checkbox"
                checked={voiceConfirmations}
                onChange={(e) => setVoiceConfirmations(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-surface-container-low">
              <div>
                <span className="font-title-sm text-sm font-semibold text-on-surface block">
                  Alexa Morning Routine Auto-Sync
                </span>
                <span className="font-body-sm text-xs text-on-surface-variant">
                  Push daily study plan to paired Echo / Alexa app on morning alarm
                </span>
              </div>
              <input
                type="checkbox"
                checked={alexaSync}
                onChange={(e) => setAlexaSync(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>
          </div>
        </div>

        {/* LMS Integrations */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-4">
          <h2 className="font-title-md font-bold text-on-surface border-b border-surface-container-low pb-2">
            Connected Learning Management Systems (LMS)
          </h2>

          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-surface-container-low">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-error-container text-on-error-container flex items-center justify-center font-bold text-sm">
                  C
                </div>
                <div>
                  <span className="font-title-sm text-sm font-semibold text-on-surface block">Canvas LMS</span>
                  <span className="font-body-sm text-xs text-secondary font-medium">Connected • 4 courses synced</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setCanvasSynced(!canvasSynced)}
                className={`px-3 py-1 rounded-lg text-xs font-title-sm ${
                  canvasSynced ? 'bg-secondary text-on-secondary' : 'bg-surface-container text-on-surface-variant'
                }`}
              >
                {canvasSynced ? 'Connected' : 'Connect'}
              </button>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-surface-container-low">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-primary-fixed text-primary flex items-center justify-center font-bold text-sm">
                  G
                </div>
                <div>
                  <span className="font-title-sm text-sm font-semibold text-on-surface block">Google Classroom</span>
                  <span className="font-body-sm text-xs text-on-surface-variant">Sync syllabus slides & calendar</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setGClassroomSynced(!gClassroomSynced)}
                className={`px-3 py-1 rounded-lg text-xs font-title-sm ${
                  gClassroomSynced ? 'bg-secondary text-on-secondary' : 'bg-surface-container text-on-surface-variant'
                }`}
              >
                {gClassroomSynced ? 'Connected' : 'Connect'}
              </button>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm shadow-sm hover:bg-primary-container transition-all disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save All Preferences'}
          </button>
        </div>
      </form>
    </div>
  );
}
