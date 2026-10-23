import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';

export default function AiAssistant({ initialPrompt }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState(initialPrompt || '');
  const [loading, setLoading] = useState(false);
  const [executingTool, setExecutingTool] = useState(null);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(false);

  const streamEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    loadChatHistory();
    checkSpeechSupport();
  }, []);

  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
    }
  }, [initialPrompt]);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkSpeechSupport = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setVoiceSupported(true);
      const recog = new SpeechRecognition();
      recog.continuous = false;
      recog.interimResults = false;
      recog.lang = 'en-US';

      recog.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };

      recog.onerror = () => setIsListening(false);
      recog.onend = () => setIsListening(false);
      recognitionRef.current = recog;
    }
  };

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory();
      setMessages(history);
    } catch (err) {
      console.warn('Failed to load chat history:', err);
    }
  };

  const speakText = (text) => {
    if (!speechEnabled || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    // Strip markdown characters for clean voice reading
    const clean = text.replace(/[*_#`\[\]]/g, '');
    const utter = new SpeechSynthesisUtterance(clean.substring(0, 300));
    utter.rate = 1.05;
    window.speechSynthesis.speak(utter);
  };

  const handleSend = async (customMessage = null, actionType = null) => {
    const msgToSend = customMessage || input;
    if (!msgToSend.trim() || loading) return;

    setInput('');
    const tempUserMsg = {
      id: `tmp-${Date.now()}`,
      role: 'user',
      content: msgToSend,
      action_type: actionType,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);
    setExecutingTool('Discovering MCP tools...');

    try {
      const res = await api.sendChatMessage(msgToSend, actionType);
      setMessages((prev) => [...prev, res]);
      speakText(res.content);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `Error connecting to CampusPilot Assistant: ${err.message}. Your offline records remain safe in your dashboard.`,
        metadata: { error: true },
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      setExecutingTool(null);
    }
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-5xl mx-auto bg-surface-container-lowest rounded-2xl shadow-sm border border-surface-container-low overflow-hidden">
      {/* Workspace Header */}
      <div className="p-space-md bg-surface-container-low border-b border-surface-container flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-on-primary shadow-sm shrink-0">
            <span className="material-symbols-outlined text-lg">auto_awesome</span>
          </div>
          <div>
            <h2 className="font-title-md text-on-surface font-bold">CampusPilot AI Assistant</h2>
            <p className="font-body-sm text-on-surface-variant">
              Powered by Google Gemini & Python Model Context Protocol (MCP) Server
            </p>
          </div>
        </div>

        {/* Speech output & status controls */}
        <div className="flex items-center gap-2">
          {window.speechSynthesis && (
            <button
              onClick={() => {
                setSpeechEnabled(!speechEnabled);
                if (speechEnabled) window.speechSynthesis.cancel();
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full font-label-sm text-xs transition-colors ${
                speechEnabled
                  ? 'bg-secondary text-on-secondary font-bold'
                  : 'bg-surface-container text-on-surface-variant hover:text-on-surface'
              }`}
              title="Toggle text-to-speech for AI answers"
            >
              <span className="material-symbols-outlined text-sm">
                {speechEnabled ? 'volume_up' : 'volume_off'}
              </span>
              <span>{speechEnabled ? 'Voice Output ON' : 'Voice Output OFF'}</span>
            </button>
          )}

          <span className="px-2.5 py-1 rounded-full bg-surface-container-lowest text-on-surface font-code-inline text-xs shadow-sm flex items-center gap-1.5 border border-surface-container">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            MCP Tools Live
          </span>
        </div>
      </div>

      {/* Scrollable Conversation Stream */}
      <div className="flex-1 p-space-md lg:p-space-lg overflow-y-auto flex flex-col gap-space-lg">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          const tools = m.metadata?.tools_executed || [];
          const citations = m.metadata?.citations || [];

          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 w-full ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary shadow-sm shrink-0 mt-1">
                  <span className="material-symbols-outlined text-sm">auto_awesome</span>
                </div>
              )}

              <div className={`flex flex-col gap-1 max-w-[85%] sm:max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
                <div className="flex items-center gap-2">
                  <span className="font-title-sm text-xs text-on-surface font-semibold">
                    {isUser ? 'You' : 'CampusPilot Copilot'}
                  </span>
                  <span className="font-body-sm text-[11px] text-on-surface-variant">
                    {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>

                {/* Visible Tool Execution Indicator if MCP tools were called */}
                {!isUser && tools.length > 0 && (
                  <div className="mb-1 p-2.5 rounded-lg bg-surface-container-low border border-surface-container flex items-center gap-2 text-xs text-on-surface-variant flex-wrap">
                    <span className="material-symbols-outlined text-sm text-primary">data_object</span>
                    <span className="font-semibold text-on-surface">MCP Tools Executed:</span>
                    {tools.map((t) => (
                      <span key={t} className="px-2 py-0.5 rounded bg-primary-fixed text-primary font-code-inline font-bold">
                        {t}()
                      </span>
                    ))}
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`p-space-md rounded-2xl leading-relaxed whitespace-pre-wrap ${
                    isUser
                      ? 'bg-primary text-on-primary rounded-tr-none shadow-md font-body-md'
                      : 'bg-surface-container-low text-on-surface rounded-tl-none shadow-sm font-body-md border border-surface-container'
                  }`}
                >
                  {m.content}
                </div>

                {/* Citations footer if available */}
                {!isUser && citations.length > 0 && (
                  <div className="flex items-center gap-1.5 mt-0.5 text-xs text-on-surface-variant">
                    <span className="material-symbols-outlined text-xs">verified</span>
                    <span>Sources: {citations.join(', ')}</span>
                  </div>
                )}

                {/* Action button if present */}
                {!isUser && m.action_type === 'plan_day' && (
                  <button
                    onClick={() => api.syncPlanToAlexa('Study Block Routine').then(() => alert('Synced study plan to your connected Alexa devices!'))}
                    className="mt-1 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary text-on-secondary font-title-sm text-xs shadow-sm hover:opacity-90 transition-opacity"
                  >
                    <span className="material-symbols-outlined text-sm">speaker</span>
                    <span>Sync This Plan to Alexa Devices</span>
                  </button>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-full bg-primary-fixed text-primary flex items-center justify-center font-bold text-xs shadow-sm shrink-0 mt-1">
                  U
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Indicator with Animated MCP Tool Activity */}
        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary shadow-sm shrink-0 mt-1 animate-pulse">
              <span className="material-symbols-outlined text-sm">auto_awesome</span>
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-surface-container-low text-on-surface shadow-sm border border-surface-container flex flex-col gap-2 max-w-md">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                <span className="font-title-sm text-xs font-semibold text-primary">Gemini Reasoning & Tool Execution</span>
              </div>
              <p className="font-body-sm text-xs text-on-surface-variant">
                Interrogating CampusPilot MCP server to retrieve live student assignments, calendar, and timetable...
              </p>
            </div>
          </div>
        )}

        <div ref={streamEndRef} />
      </div>

      {/* Suggested Starter Chips */}
      <div className="px-space-md py-2 bg-surface-container-lowest border-t border-surface-container-low flex items-center gap-2 overflow-x-auto">
        <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider shrink-0">Try:</span>
        <button
          onClick={() => handleSend('What pending assignments and deliverables do I have?')}
          className="px-2.5 py-1 rounded-full bg-surface-container hover:bg-primary-fixed hover:text-primary text-on-surface font-body-sm text-xs transition-colors shrink-0"
        >
          Pending Assignments
        </button>
        <button
          onClick={() => handleSend('What is on my timetable for today?')}
          className="px-2.5 py-1 rounded-full bg-surface-container hover:bg-primary-fixed hover:text-primary text-on-surface font-body-sm text-xs transition-colors shrink-0"
        >
          Today's Timetable
        </button>
        <button
          onClick={() => handleSend('Remind me to study Operating Systems buddy allocator tonight at 8 PM')}
          className="px-2.5 py-1 rounded-full bg-surface-container hover:bg-primary-fixed hover:text-primary text-on-surface font-body-sm text-xs transition-colors shrink-0"
        >
          Set Study Reminder
        </button>
        <button
          onClick={() => handleSend('Search learning resources for Zero Trust architecture')}
          className="px-2.5 py-1 rounded-full bg-surface-container hover:bg-primary-fixed hover:text-primary text-on-surface font-body-sm text-xs transition-colors shrink-0"
        >
          Search Learning Resources
        </button>
      </div>

      {/* Prompt Dock */}
      <div className="p-space-md bg-surface-container-low border-t border-surface-container flex items-center gap-2">
        {voiceSupported && (
          <button
            onClick={toggleVoiceInput}
            className={`p-2.5 rounded-xl transition-all shadow-sm ${
              isListening
                ? 'bg-error text-on-error animate-pulse'
                : 'bg-surface-container-lowest text-on-surface-variant hover:text-primary hover:bg-surface-container-high'
            }`}
            title={isListening ? 'Listening... click to stop' : 'Click to speak via Web Speech API'}
          >
            <span className="material-symbols-outlined text-xl">mic</span>
          </button>
        )}

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isListening ? 'Listening to speech...' : 'Ask CampusPilot about tasks, timetable, study plans, or reminders...'}
          className="flex-1 px-4 py-2.5 rounded-xl bg-surface-container-lowest text-on-surface placeholder:text-on-surface-variant/60 border border-surface-container focus:outline-none focus:ring-2 focus:ring-primary shadow-inner font-body-md"
        />

        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="px-5 py-2.5 rounded-xl bg-primary text-on-primary font-title-sm hover:bg-primary-container transition-all shadow-sm disabled:opacity-40 flex items-center gap-1.5"
        >
          <span>Send</span>
          <span className="material-symbols-outlined text-base">send</span>
        </button>
      </div>
    </div>
  );
}
