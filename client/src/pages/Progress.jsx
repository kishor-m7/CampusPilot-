import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function Progress() {
  const [profile, setProfile] = useState(null);
  const [courses, setCourses] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [prof, crs, over] = await Promise.all([
        api.getProfile(),
        api.getCourses(),
        api.getOverview()
      ]);
      setProfile(prof);
      setCourses(crs);
      setMetrics(over.metrics);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="py-12 flex justify-center text-on-surface-variant">Loading academic analytics...</div>;
  }

  const currentGpa = profile?.current_gpa || 3.78;
  const targetGpa = profile?.target_gpa || 3.90;
  const gpaPct = Math.min(100, Math.round((currentGpa / 4.0) * 100));

  return (
    <div className="flex flex-col gap-space-lg">
      <div>
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Academic Progress & Velocity</h1>
        <p className="font-body-md text-on-surface-variant">
          GPA modeling, course performance breakdowns, and weekly study velocity.
        </p>
      </div>

      {/* Top 3 Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
        {/* GPA Estimator Card */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-md text-xs font-bold text-on-surface-variant uppercase tracking-wider">
              Cumulative GPA
            </span>
            <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-xs font-bold">
              Top 8%
            </span>
          </div>

          <div className="my-4">
            <span className="text-4xl font-headline-xl font-bold text-on-surface">{currentGpa.toFixed(2)}</span>
            <span className="text-sm font-body-sm text-on-surface-variant ml-1">/ 4.00</span>
            <div className="w-full bg-surface-container h-2 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-primary-container h-full rounded-full transition-all duration-500"
                style={{ width: `${gpaPct}%` }}
              ></div>
            </div>
          </div>

          <p className="font-body-sm text-xs text-on-surface-variant">
            Target GPA: <strong>{targetGpa.toFixed(2)}</strong> (+{(targetGpa - currentGpa).toFixed(2)} to goal)
          </p>
        </div>

        {/* Weekly Study Hours */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-md text-xs font-bold text-on-surface-variant uppercase tracking-wider">
              Study Velocity
            </span>
            <span className="px-2 py-0.5 rounded-full bg-primary-fixed text-primary font-label-sm text-xs font-bold">
              {metrics?.study_target_percentage || 77}%
            </span>
          </div>

          <div className="my-4">
            <span className="text-4xl font-headline-xl font-bold text-on-surface">
              {metrics?.weekly_study_hours || 18.5}
            </span>
            <span className="text-sm font-body-sm text-on-surface-variant ml-1">hrs this week</span>
            <div className="w-full bg-surface-container h-2 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-secondary h-full rounded-full transition-all duration-500"
                style={{ width: `${metrics?.study_target_percentage || 77}%` }}
              ></div>
            </div>
          </div>

          <p className="font-body-sm text-xs text-on-surface-variant">
            Weekly target: <strong>{profile?.weekly_target_hours || 24} hrs</strong>
          </p>
        </div>

        {/* Task Velocity */}
        <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="font-label-md text-xs font-bold text-on-surface-variant uppercase tracking-wider">
              Task Velocity
            </span>
            <span className="px-2 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-xs font-bold">
              12 Day Streak 🔥
            </span>
          </div>

          <div className="my-4">
            <span className="text-4xl font-headline-xl font-bold text-on-surface">
              {metrics?.tasks_completed_count || 14}
            </span>
            <span className="text-sm font-body-sm text-on-surface-variant ml-1">deliverables completed</span>
          </div>

          <p className="font-body-sm text-xs text-on-surface-variant">
            Pacing ahead of semester baseline by 22%
          </p>
        </div>
      </div>

      {/* Courses Performance Table */}
      <div className="p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border border-surface-container-low flex flex-col gap-space-md">
        <h2 className="font-title-md font-bold text-on-surface">Enrolled Courses & Academic Standing</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-container-low text-on-surface-variant font-label-md text-xs uppercase tracking-wider">
              <tr>
                <th className="p-3 rounded-l-lg">Course Code</th>
                <th className="p-3">Course Name</th>
                <th className="p-3">Credits</th>
                <th className="p-3">Current Grade</th>
                <th className="p-3 rounded-r-lg">Standing</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container-low font-body-md">
              {courses.map((c) => (
                <tr key={c.id} className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="p-3 font-bold font-code-inline text-on-surface">{c.code}</td>
                  <td className="p-3 text-on-surface">{c.name}</td>
                  <td className="p-3 text-on-surface-variant">{c.credits} Credits</td>
                  <td className="p-3 font-semibold text-primary">{c.grade || 'A'}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-xs font-semibold">
                      On Track
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
