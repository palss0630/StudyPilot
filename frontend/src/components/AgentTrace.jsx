import React, { useState } from 'react';
import {
  ListChecks,
  Wrench,
  Search,
  BookOpen,
  Calculator,
  CloudSun,
  Clock,
  FileText,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

function getToolIcon(name) {
  if (name.includes('search')) return <Search className="w-3.5 h-3.5 text-sky-400" />;
  if (name.includes('wiki')) return <BookOpen className="w-3.5 h-3.5 text-amber-400" />;
  if (name.includes('calc')) return <Calculator className="w-3.5 h-3.5 text-emerald-400" />;
  if (name.includes('weather')) return <CloudSun className="w-3.5 h-3.5 text-blue-400" />;
  if (name.includes('clock') || name.includes('time')) return <Clock className="w-3.5 h-3.5 text-purple-400" />;
  return <Wrench className="w-3.5 h-3.5 text-indigo-400" />;
}

export default function AgentTrace({ events = [], isStreaming = false }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedResults, setExpandedResults] = useState({});

  if (!events || events.length === 0) return null;

  // Extract Plan
  const planEvent = events.find((e) => e.type === 'plan_created');
  const plan = planEvent?.plan;

  // Extract Steps & Tool calls
  const steps = plan?.steps || [];
  const toolCalls = events.filter((e) => e.type === 'tool_called' || e.type === 'tool_result');
  const reflection = events.find((e) => e.type === 'reflection')?.result;

  const toggleResult = (idx) => {
    setExpandedResults((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="my-4 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md overflow-hidden text-xs shadow-xl">
      {/* Header bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3.5 bg-slate-900/90 hover:bg-slate-800/60 transition-colors text-left"
      >
        <div className="flex items-center gap-2 text-slate-200 font-semibold">
          <div className="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <span>Autonomous Agent Reasoning Trace</span>
          {isStreaming && (
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 font-normal text-[11px] border border-brand-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-ping" />
              Thinking & Executing...
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[11px]">
            {events.length} event{events.length === 1 ? '' : 's'}
          </span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded body */}
      {isExpanded && (
        <div className="p-4 space-y-4 border-t border-slate-800/80">
          {/* Plan Section */}
          {steps.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                <ListChecks className="w-3.5 h-3.5 text-brand-400" />
                Strategic Plan
              </div>
              <div className="grid gap-1.5 pl-2">
                {steps.map((st, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2 p-2 rounded-xl bg-slate-800/40 border border-slate-800/80 text-slate-300"
                  >
                    <span className="w-4 h-4 rounded-full bg-slate-700/80 text-[10px] flex items-center justify-center shrink-0 font-bold text-slate-200 mt-0.5">
                      {st.step || idx + 1}
                    </span>
                    <div className="flex-1">
                      <div className="font-medium text-slate-200">{st.description}</div>
                      {st.tools_needed && st.tools_needed.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {st.tools_needed.map((t, tidx) => (
                            <span
                              key={tidx}
                              className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700/60 text-slate-400 font-mono text-[10px]"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tool Invocations Section */}
          {toolCalls.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                <Wrench className="w-3.5 h-3.5 text-amber-400" />
                Tool Executions
              </div>
              <div className="space-y-1.5 pl-2">
                {events.map((ev, idx) => {
                  if (ev.type === 'tool_called') {
                    const argsStr =
                      typeof ev.args === 'string' ? ev.args : JSON.stringify(ev.args || {});
                    return (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1"
                      >
                        <div className="flex items-center gap-1.5 text-indigo-300 font-bold">
                          {getToolIcon(ev.name || '')}
                          <span>{ev.name}()</span>
                        </div>
                        <div className="text-slate-400 truncate pl-5">args: {argsStr}</div>
                      </div>
                    );
                  }
                  if (ev.type === 'tool_result') {
                    const resStr = String(ev.result || '');
                    const isLong = resStr.length > 120;
                    const isShown = expandedResults[idx];
                    return (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800 text-slate-300 space-y-1 pl-6"
                      >
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">
                          Result output:
                        </div>
                        <div className="text-slate-300 whitespace-pre-wrap font-mono text-[11px]">
                          {isLong && !isShown ? resStr.slice(0, 120) + '...' : resStr}
                        </div>
                        {isLong && (
                          <button
                            onClick={() => toggleResult(idx)}
                            className="text-brand-400 hover:text-brand-300 text-[10px] font-sans font-medium"
                          >
                            {isShown ? 'Show less' : 'Show full output'}
                          </button>
                        )}
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          )}

          {/* Reflection Section */}
          {reflection && (
            <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-800/40 flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold text-slate-200">
                  Self-Reflection Critique: {reflection.ok ? 'Verified Grounded' : 'Revision Applied'}
                </div>
                <div className="text-slate-400 text-[11px] mt-0.5">
                  Verified answers against external tool observations and factual consistency.
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
