const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`API call to ${endpoint} failed:`, err.message);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => fetchJson('/health'),

  // Overview
  getOverview: () => fetchJson('/overview'),

  // Profile
  getProfile: () => fetchJson('/profile'),
  updateProfile: (data) => fetchJson('/profile', { method: 'PUT', body: JSON.stringify(data) }),

  // Courses
  getCourses: () => fetchJson('/courses'),
  createCourse: (data) => fetchJson('/courses', { method: 'POST', body: JSON.stringify(data) }),

  // Assignments
  getAssignments: (status) => fetchJson(status ? `/assignments?status=${status}` : '/assignments'),
  createAssignment: (data) => fetchJson('/assignments', { method: 'POST', body: JSON.stringify(data) }),
  updateAssignment: (id, data) => fetchJson(`/assignments/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteAssignment: (id) => fetchJson(`/assignments/${id}`, { method: 'DELETE' }),

  // Exams
  getExams: () => fetchJson('/exams'),
  createExam: (data) => fetchJson('/exams', { method: 'POST', body: JSON.stringify(data) }),
  updateExam: (id, data) => fetchJson(`/exams/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Study Sessions
  getStudySessions: () => fetchJson('/study-sessions'),
  createStudySession: (data) => fetchJson('/study-sessions', { method: 'POST', body: JSON.stringify(data) }),
  updateStudySession: (id, data) => fetchJson(`/study-sessions/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Timetable
  getTimetable: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchJson(query ? `/timetable?${query}` : '/timetable');
  },

  // Reminders
  getReminders: (status) => fetchJson(status ? `/reminders?status=${status}` : '/reminders'),
  createReminder: (data) => fetchJson('/reminders', { method: 'POST', body: JSON.stringify(data) }),
  updateReminder: (id, data) => fetchJson(`/reminders/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteReminder: (id) => fetchJson(`/reminders/${id}`, { method: 'DELETE' }),

  // Learning Resources
  searchResources: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchJson(query ? `/resources?${query}` : '/resources');
  },

  // AI Assistant
  getChatHistory: () => fetchJson('/assistant/history'),
  sendChatMessage: (message, action_type = null) => 
    fetchJson('/assistant/chat', { method: 'POST', body: JSON.stringify({ message, action_type }) }),

  // Alexa
  syncPlanToAlexa: (routine_name = "Morning Routine") => 
    fetchJson('/alexa/sync-plan', { method: 'POST', body: JSON.stringify({ routine_name }) }),
  getOralDrill: () => fetchJson('/alexa/oral-drill')
};
