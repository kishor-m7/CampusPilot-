import React, { useState, useEffect } from 'react';
import { api } from './api';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Overview from './pages/Overview';
import AiAssistant from './pages/AiAssistant';
import Assignments from './pages/Assignments';
import Exams from './pages/Exams';
import StudyPlanner from './pages/StudyPlanner';
import Reminders from './pages/Reminders';
import Progress from './pages/Progress';
import Settings from './pages/Settings';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [profile, setProfile] = useState(null);
  const [health, setHealth] = useState(null);
  const [overviewData, setOverviewData] = useState(null);
  const [initialPrompt, setInitialPrompt] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [h, p, o] = await Promise.allSettled([
        api.getHealth(),
        api.getProfile(),
        api.getOverview()
      ]);
      if (h.status === 'fulfilled') setHealth(h.value);
      if (p.status === 'fulfilled') setProfile(p.value);
      if (o.status === 'fulfilled') setOverviewData(o.value);
    } catch (err) {
      console.warn('Initial data load:', err);
    }
  };

  const handleTriggerPrompt = (prompt) => {
    setInitialPrompt(prompt);
    setActiveTab('ai-assistant');
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview onNavigate={setActiveTab} onTriggerPrompt={handleTriggerPrompt} />;
      case 'ai-assistant':
        return <AiAssistant initialPrompt={initialPrompt} />;
      case 'assignments':
        return <Assignments />;
      case 'exams':
        return <Exams />;
      case 'study-planner':
        return <StudyPlanner />;
      case 'reminders':
        return <Reminders />;
      case 'progress':
        return <Progress />;
      case 'settings':
        return <Settings onProfileUpdated={(updated) => setProfile(updated)} />;
      default:
        return <Overview onNavigate={setActiveTab} onTriggerPrompt={handleTriggerPrompt} />;
    }
  };

  return (
    <div className="bg-background min-h-screen text-on-surface antialiased font-body-md">
      {/* Sidebar navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          if (tab !== 'ai-assistant') setInitialPrompt('');
          setActiveTab(tab);
        }}
        profile={profile}
        metrics={overviewData?.metrics}
      />

      {/* Main Content Area */}
      <div className="pl-64">
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onQuickAsk={() => setActiveTab('ai-assistant')}
          profile={profile}
          health={health}
        />

        {/* Dynamic Page Container */}
        <main className="relative pt-16 w-full min-h-screen bg-background">
          <div className="flex flex-col w-full p-space-md lg:p-space-xl">
            {renderActivePage()}
          </div>
        </main>
      </div>
    </div>
  );
}
