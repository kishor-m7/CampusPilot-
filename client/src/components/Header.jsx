import React from 'react';

export default function Header({ activeTab, setActiveTab, onQuickAsk, profile, health }) {
  const getBreadcrumb = () => {
    switch (activeTab) {
      case 'overview': return 'Command Center';
      case 'ai-assistant': return 'Alexa+ Copilot Workspace';
      case 'assignments': return 'Assignments & Deliverables';
      case 'exams': return 'Exam Countdown & Syllabi';
      case 'study-planner': return 'Timetable & Focus Blocks';
      case 'reminders': return 'Reminders & Notifications';
      case 'progress': return 'Academic Velocity & GPA';
      case 'settings': return 'Preferences & Integrations';
      default: return 'Workspace';
    }
  };

  return (
    <header className="fixed top-0 left-64 right-0 h-16 bg-surface/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-40 px-space-lg flex items-center justify-between border-b border-surface-container-low">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-on-surface-variant font-body-sm text-body-sm">
        <span className="text-on-surface font-title-sm text-title-sm">CampusPilot</span>
        <span className="material-symbols-outlined text-sm leading-none">chevron_right</span>
        <span className="text-on-surface-variant font-label-md text-label-md uppercase tracking-wider font-semibold">
          {getBreadcrumb()}
        </span>
      </div>

      {/* Action utilities */}
      <div className="flex items-center gap-space-md">
        {/* DB Connection indicator */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container-low text-on-surface-variant text-xs">
          <span className={`w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-secondary animate-pulse' : 'bg-tertiary'}`}></span>
          <span className="font-medium font-code-inline">
            {health?.database?.type === 'supabase_postgresql' ? 'Supabase Cloud' : 'SQLite Local Dev'}
          </span>
        </div>

        {/* Quick Ask AI button */}
        <button
          onClick={onQuickAsk || (() => setActiveTab('ai-assistant'))}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-fixed text-primary hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-all shadow-sm active:scale-95"
          type="button"
        >
          <span className="material-symbols-outlined text-sm leading-none">auto_awesome</span>
          <span className="font-label-md text-label-md font-semibold">Quick Ask</span>
        </button>

        {/* Reminders shortcut */}
        <button
          onClick={() => setActiveTab('reminders')}
          className="relative p-2 rounded-xl text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors"
          type="button"
          title="Reminders"
        >
          <span className="material-symbols-outlined text-xl leading-none">notifications</span>
          <span className="absolute top-1.5 right-1.5 min-w-[16px] h-4 px-1 rounded-full bg-error text-on-error font-label-sm text-[10px] flex items-center justify-center font-bold">
            3
          </span>
        </button>

        {/* Profile Avatar */}
        <div
          onClick={() => setActiveTab('settings')}
          className="flex items-center gap-2 pl-2 cursor-pointer"
        >
          <div className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-xs shadow-sm">
            {profile?.full_name ? profile.full_name.charAt(0) : 'K'}
          </div>
          <span className="material-symbols-outlined text-on-surface-variant text-base hidden sm:block">
            arrow_drop_down
          </span>
        </div>
      </div>
    </header>
  );
}
