import React, { useState } from 'react';
import {
  MessageSquare,
  BookOpen,
  Trophy,
  Plus,
  Trash2,
  ChevronLeft,
  X,
  GraduationCap,
  Sparkles,
} from 'lucide-react';

export default function Sidebar({
  isOpen,
  onToggle,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  notes,
  onDeleteNote,
  quizzes,
}) {
  const [activeTab, setActiveTab] = useState('sessions'); // 'sessions' | 'notes' | 'quizzes'

  const handleSelect = (id) => {
    onSelectSession(id);
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      onToggle();
    }
  };

  const handleNew = () => {
    onNewSession();
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      onToggle();
    }
  };

  return (
    <aside
      className={`fixed lg:static top-0 left-0 z-40 h-full w-72 sm:w-80 max-w-[85vw] bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300 ease-in-out shadow-2xl lg:shadow-none ${
        isOpen
          ? 'translate-x-0 lg:w-80'
          : '-translate-x-full lg:w-0 lg:border-r-0 lg:overflow-hidden pointer-events-none lg:pointer-events-auto'
      }`}
    >
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight flex items-center gap-1.5">
              StudyPilot
              <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                Agent
              </span>
            </h1>
            <p className="text-xs text-slate-400">AI Study & Research Agent</p>
          </div>
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Close menu"
          aria-label="Close menu"
        >
          <X className="w-5 h-5 lg:hidden" />
          <ChevronLeft className="w-5 h-5 hidden lg:block" />
        </button>
      </div>

      {/* New Session Button */}
      <div className="p-3">
        <button
          onClick={handleNew}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white font-medium text-sm shadow-md shadow-brand-600/20 hover:from-brand-500 hover:to-indigo-500 transition-all active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          New Study Session
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 px-3 text-xs font-medium">
        <button
          onClick={() => setActiveTab('sessions')}
          className={`flex-1 py-2 flex items-center justify-center gap-1.5 border-b-2 transition-colors ${
            activeTab === 'sessions'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-300'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          Chats ({sessions.length})
        </button>
        <button
          onClick={() => setActiveTab('notes')}
          className={`flex-1 py-2 flex items-center justify-center gap-1.5 border-b-2 transition-colors ${
            activeTab === 'notes'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-300'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          Notes ({notes.length})
        </button>
        <button
          onClick={() => setActiveTab('quizzes')}
          className={`flex-1 py-2 flex items-center justify-center gap-1.5 border-b-2 transition-colors ${
            activeTab === 'quizzes'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-300'
          }`}
        >
          <Trophy className="w-3.5 h-3.5" />
          Quizzes ({quizzes.length})
        </button>
      </div>

      {/* Tab Content List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {activeTab === 'sessions' && (
          <>
            {sessions.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No past sessions yet. Start a study query!
              </div>
            ) : (
              sessions.map((s) => (
                <div
                  key={s.id}
                  onClick={() => handleSelect(s.id)}
                  className={`group flex items-center justify-between p-2.5 rounded-xl text-xs cursor-pointer transition-all ${
                    activeSessionId === s.id
                      ? 'bg-brand-500/15 text-brand-300 border border-brand-500/30'
                      : 'text-slate-300 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center gap-2 overflow-hidden pr-2">
                    <MessageSquare className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                    <span className="truncate font-medium">{s.title || 'Untitled Session'}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-400 rounded transition-opacity"
                    title="Delete session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </>
        )}

        {activeTab === 'notes' && (
          <>
            {notes.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No saved notes. Click "Save Note" on any agent response.
              </div>
            ) : (
              notes.map((n) => (
                <div
                  key={n.id}
                  className="p-3 bg-slate-800/40 border border-slate-700/50 rounded-xl space-y-1 text-xs"
                >
                  <div className="flex items-center justify-between font-semibold text-slate-200">
                    <span className="truncate">{n.title}</span>
                    <button
                      onClick={() => onDeleteNote(n.id)}
                      className="text-slate-400 hover:text-red-400 p-0.5 rounded transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-slate-400 line-clamp-2 text-[11px]">{n.content}</p>
                </div>
              ))
            )}
          </>
        )}

        {activeTab === 'quizzes' && (
          <>
            {quizzes.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No quiz results recorded yet.
              </div>
            ) : (
              quizzes.map((q) => {
                const pct = q.total > 0 ? Math.round((q.score / q.total) * 100) : 0;
                return (
                  <div
                    key={q.id}
                    className="p-2.5 bg-slate-800/40 border border-slate-700/50 rounded-xl flex items-center justify-between text-xs"
                  >
                    <div className="overflow-hidden pr-2">
                      <div className="font-medium text-slate-200 truncate">{q.topic}</div>
                      <div className="text-[10px] text-slate-400">{q.created_at?.slice(0, 10)}</div>
                    </div>
                    <div className="px-2 py-1 rounded-lg bg-brand-500/20 text-brand-300 font-bold text-[11px]">
                      {q.score}/{q.total} ({pct}%)
                    </div>
                  </div>
                );
              })
            )}
          </>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Autonomous Engine
        </span>
        <span className="text-slate-500 font-mono">v2.0</span>
      </div>
    </aside>
  );
}
