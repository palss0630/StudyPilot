import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Menu,
  Send,
  Sparkles,
  Bot,
  User,
  Bookmark,
  Layers,
  HelpCircle,
  Copy,
  Check,
  Compass,
  ArrowUpRight,
  ExternalLink,
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import AgentTrace from './components/AgentTrace';
import FlashcardsModal from './components/FlashcardsModal';
import QuizModal from './components/QuizModal';
import {
  fetchSessions,
  fetchSession,
  deleteSession,
  fetchNotes,
  saveNote,
  deleteNote,
  fetchQuizzes,
  saveQuizResult,
  generateFlashcards,
  generateQuiz,
  streamAgentExecution,
} from './api';

const EXAMPLE_PROMPTS = [
  'Teach me about black holes and quiz me on the event horizon',
  'Compare solar vs wind energy and calculate payback for 50000 cost & 5000/yr savings',
  'Explain how neural networks learn via backpropagation and gradient descent',
  'What is the current weather in London and top 3 science museums to visit?',
];

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputGoal, setInputGoal] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentTraceEvents, setCurrentTraceEvents] = useState([]);

  // Study Tools modals
  const [notes, setNotes] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [flashcardData, setFlashcardData] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [studyTopic, setStudyTopic] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
    loadNotes();
    loadQuizzes();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentTraceEvents]);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data || []);
    } catch (err) {
      console.error('Failed to load sessions', err);
    }
  };

  const loadNotes = async () => {
    try {
      const data = await fetchNotes();
      setNotes(data || []);
    } catch (err) {
      console.error('Failed to load notes', err);
    }
  };

  const loadQuizzes = async () => {
    try {
      const data = await fetchQuizzes();
      setQuizzes(data || []);
    } catch (err) {
      console.error('Failed to load quizzes', err);
    }
  };

  const handleSelectSession = async (id) => {
    try {
      setActiveSessionId(id);
      const data = await fetchSession(id);
      setMessages(data.messages || []);
      setCurrentTraceEvents([]);
    } catch (err) {
      console.error('Failed to load session details', err);
    }
  };

  const handleNewSession = () => {
    setActiveSessionId(null);
    setMessages([]);
    setCurrentTraceEvents([]);
  };

  const handleDeleteSession = async (id) => {
    await deleteSession(id);
    if (activeSessionId === id) handleNewSession();
    loadSessions();
  };

  const handleDeleteNote = async (id) => {
    await deleteNote(id);
    loadNotes();
  };

  const handleSaveNote = async (content) => {
    const title = content.slice(0, 40).replace(/[#*]/g, '').trim() || 'Study Note';
    await saveNote(title, content);
    loadNotes();
  };

  const handleCreateFlashcards = async (content) => {
    const topic = content.slice(0, 30).replace(/[#*]/g, '').trim() || 'Topic';
    setStudyTopic(topic);
    try {
      const res = await generateFlashcards(topic, content);
      setFlashcardData(res.flashcards || []);
    } catch (err) {
      alert('Could not generate flashcards: ' + err.message);
    }
  };

  const handleCreateQuiz = async (content) => {
    const topic = content.slice(0, 30).replace(/[#*]/g, '').trim() || 'Topic';
    setStudyTopic(topic);
    try {
      const res = await generateQuiz(topic, content, 5);
      setQuizData(res.questions || []);
    } catch (err) {
      alert('Could not generate quiz: ' + err.message);
    }
  };

  const handleSaveQuizScore = async (result) => {
    await saveQuizResult(result.topic, result.score, result.total, activeSessionId);
    loadQuizzes();
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleSendMessage = (e) => {
    e?.preventDefault();
    const query = inputGoal.trim();
    if (!query || isStreaming) return;

    setInputGoal('');
    setIsStreaming(true);
    setCurrentTraceEvents([]);

    // Optimistically add user message
    const userMsg = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMsg]);

    let assistantAnswer = '';
    let accumulatedSources = [];

    streamAgentExecution(
      query,
      activeSessionId,
      (event) => {
        if (event.type === 'session_init') {
          setActiveSessionId(event.data.session_id);
          loadSessions();
        } else if (event.type === 'agent_event') {
          const evData = event.data;
          setCurrentTraceEvents((prev) => [...prev, evData]);

          if (evData.type === 'final_answer') {
            assistantAnswer = evData.answer;
            accumulatedSources = evData.sources || [];
          } else if (evData.type === 'error' || evData.type === 'guardrail_blocked') {
            assistantAnswer = evData.message || 'Request was halted.';
          }
        }
      },
      (err) => {
        setIsStreaming(false);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `**Error:** Could not complete request (${err.message})`,
            trace: currentTraceEvents,
          },
        ]);
      },
      () => {
        setIsStreaming(false);
        if (assistantAnswer) {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: assistantAnswer,
              sources: accumulatedSources,
              trace: [...currentTraceEvents],
            },
          ]);
          setCurrentTraceEvents([]);
          loadSessions();
        }
      }
    );
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Sidebar with permanent toggle */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(false)}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        notes={notes}
        onDeleteNote={handleDeleteNote}
        quizzes={quizzes}
      />

      {/* Main Chat Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-slate-950 relative">
        {/* Top Navbar */}
        <header className="h-14 border-b border-slate-800/80 px-4 flex items-center justify-between shrink-0 bg-slate-950/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            {/* Permanent sidebar toggle button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors flex items-center justify-center border border-slate-800"
              title={sidebarOpen ? 'Collapse sidebar' : 'Open sidebar'}
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-tight text-white">StudyPilot</span>
              <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
                / {activeSessionId ? 'Active Session' : 'New Research Workspace'}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Agent Ready
            </span>
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6 max-w-4xl w-full mx-auto">
          {messages.length === 0 && !isStreaming ? (
            <div className="flex flex-col items-center justify-center min-h-[70vh] text-center space-y-6 max-w-lg mx-auto">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-xl shadow-brand-500/20">
                <Sparkles className="w-7 h-7" />
              </div>
              <div className="space-y-2">
                <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
                  What would you like to study today?
                </h2>
                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                  StudyPilot uses autonomous tool planning, web searches, safe calculation, and
                  self-critique to research any topic and build interactive study aids.
                </p>
              </div>

              {/* Suggestions */}
              <div className="grid gap-2 w-full text-left pt-2">
                {EXAMPLE_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setInputGoal(p);
                    }}
                    className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-brand-500/50 hover:bg-slate-850 text-xs text-slate-300 flex items-center justify-between transition-all group"
                  >
                    <span className="truncate pr-2">{p}</span>
                    <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-brand-400 transition-colors shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 sm:gap-4 ${
                    m.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {m.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 sm:p-5 text-sm ${
                      m.role === 'user'
                        ? 'bg-brand-600 text-white shadow-md'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 shadow-xl'
                    }`}
                  >
                    {/* Render saved trace if present */}
                    {m.trace && m.trace.length > 0 && (
                      <AgentTrace events={m.trace} isStreaming={false} />
                    )}

                    <div className="prose prose-invert prose-sm max-w-none break-words">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                    </div>

                    {/* Sources citations */}
                    {m.sources && m.sources.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-slate-800/80 text-xs text-slate-400 space-y-1">
                        <div className="font-semibold text-slate-300 flex items-center gap-1">
                          <ExternalLink className="w-3.5 h-3.5" /> Sources Cited:
                        </div>
                        <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                          {m.sources.map((src, sidx) => (
                            <li key={sidx} className="truncate">
                              {src.startsWith('http') ? (
                                <a
                                  href={src}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-brand-400 hover:underline"
                                >
                                  {src}
                                </a>
                              ) : (
                                src
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action buttons for assistant answers */}
                    {m.role === 'assistant' && (
                      <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap items-center gap-2 text-xs">
                        <button
                          onClick={() => handleSaveNote(m.content)}
                          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                        >
                          <Bookmark className="w-3.5 h-3.5" />
                          Save Note
                        </button>
                        <button
                          onClick={() => handleCreateFlashcards(m.content)}
                          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                        >
                          <Layers className="w-3.5 h-3.5" />
                          Flashcards
                        </button>
                        <button
                          onClick={() => handleCreateQuiz(m.content)}
                          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/60 border border-indigo-800/50 text-indigo-300 transition-colors font-medium"
                        >
                          <HelpCircle className="w-3.5 h-3.5" />
                          Quiz Me
                        </button>
                        <button
                          onClick={() => handleCopy(m.content, idx)}
                          className="p-1 text-slate-400 hover:text-white rounded ml-auto transition-colors"
                          title="Copy response"
                        >
                          {copiedIndex === idx ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    )}
                  </div>

                  {m.role === 'user' && (
                    <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {/* Streaming active trace indicator */}
              {isStreaming && (
                <div className="flex gap-3 sm:gap-4 justify-start">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="max-w-[85%] sm:max-w-[78%] w-full">
                    <AgentTrace events={currentTraceEvents} isStreaming={true} />
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/90 backdrop-blur-md shrink-0">
          <form
            onSubmit={handleSendMessage}
            className="max-w-4xl mx-auto flex items-center gap-2 rounded-2xl bg-slate-900 border border-slate-800 p-2 shadow-xl focus-within:border-brand-500/60 transition-colors"
          >
            <input
              type="text"
              value={inputGoal}
              onChange={(e) => setInputGoal(e.target.value)}
              placeholder="Ask a study topic, math problem, or research goal..."
              className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
              disabled={isStreaming}
            />
            <button
              type="submit"
              disabled={!inputGoal.trim() || isStreaming}
              className="p-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white hover:from-brand-500 hover:to-indigo-500 disabled:opacity-40 transition-all shadow-md shadow-brand-500/20 active:scale-95"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </main>

      {/* Interactive Flashcards Modal */}
      <FlashcardsModal
        isOpen={Boolean(flashcardData)}
        onClose={() => setFlashcardData(null)}
        flashcards={flashcardData}
        topic={studyTopic}
      />

      {/* Interactive Quiz Modal */}
      <QuizModal
        isOpen={Boolean(quizData)}
        onClose={() => setQuizData(null)}
        questions={quizData}
        topic={studyTopic}
        onSaveScore={handleSaveQuizScore}
      />
    </div>
  );
}
