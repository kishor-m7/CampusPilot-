import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, profile, metrics }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: 'dashboard', badge: null },
    { id: 'ai-assistant', label: 'AI Assistant', icon: 'auto_awesome', badge: 'AI', badgeColor: 'bg-primary text-on-primary' },
    { id: 'assignments', label: 'Assignments', icon: 'checklist', badge: metrics?.pending_assignments_count ? `${metrics.pending_assignments_count} due` : null, badgeColor: 'bg-surface-container-high text-on-surface-variant' },
    { id: 'exams', label: 'Exams', icon: 'school', badge: metrics?.upcoming_exams_count ? `${metrics.upcoming_exams_count}` : null, badgeColor: 'bg-error text-on-error' },
    { id: 'study-planner', label: 'Study Planner', icon: 'calendar_today', badge: null },
    { id: 'reminders', label: 'Reminders', icon: 'notifications_active', badge: null },
    { id: 'progress', label: 'Progress', icon: 'trending_up', badge: null },
    { id: 'settings', label: 'Settings', icon: 'tune', badge: null },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-50 flex flex-col justify-between">
      <div className="flex flex-col">
        {/* Brand header */}
        <div className="h-16 flex items-center justify-between px-space-md border-b border-surface-container-low">
          <div className="flex items-center gap-space-sm cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-on-primary shadow-sm">
              <span className="material-symbols-outlined text-lg leading-none">school</span>
            </div>
            <span className="font-title-md text-title-md text-on-surface font-bold tracking-tight">CampusPilot</span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold">
            Alexa+
          </span>
        </div>

        {/* Navigation list */}
        <nav className="flex flex-col gap-1 px-space-sm mt-space-sm">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center justify-between px-space-md py-2.5 rounded-lg transition-all group text-left ${
                  isActive
                    ? 'bg-primary-container text-on-primary font-title-sm shadow-sm'
                    : 'text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface'
                }`}
              >
                <div className="flex items-center gap-space-md">
                  <span
                    className={`material-symbols-outlined text-lg leading-none ${
                      isActive ? 'text-on-primary' : item.id === 'ai-assistant' ? 'text-surface-tint' : ''
                    }`}
                  >
                    {item.icon}
                  </span>
                  <span className="font-body-md text-body-md">{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`px-1.5 py-0.5 rounded-full font-label-sm text-[11px] font-semibold leading-none ${
                      item.badgeColor || 'bg-surface-container text-on-surface-variant'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Student user profile pill */}
      <div className="p-space-sm mb-space-sm border-t border-surface-container-low">
        <div
          onClick={() => setActiveTab('settings')}
          className="flex items-center gap-space-sm p-space-sm rounded-xl bg-surface-container-low hover:bg-surface-container-high transition-colors cursor-pointer"
        >
          <div className="relative flex-shrink-0">
            <div className="w-9 h-9 rounded-full bg-primary-fixed text-primary flex items-center justify-center font-bold text-sm shadow-sm">
              {profile?.full_name ? profile.full_name.charAt(0) : 'K'}
            </div>
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-secondary ring-2 ring-surface-container-lowest"></span>
          </div>
          <div className="flex flex-col min-w-0 flex-1">
            <span className="font-title-sm text-title-sm text-on-surface truncate">
              {profile?.full_name || 'Kishor'}
            </span>
            <span className="font-body-sm text-body-sm text-on-surface-variant truncate">
              {profile?.major || 'B.Tech CS'} • {profile?.semester || 'Sem 6'}
            </span>
          </div>
          <span className="material-symbols-outlined text-on-surface-variant text-base">unfold_more</span>
        </div>
      </div>
    </aside>
  );
}
