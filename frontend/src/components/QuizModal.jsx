import React, { useState } from 'react';
import { X, HelpCircle, CheckCircle, XCircle, Trophy, RotateCcw } from 'lucide-react';

export default function QuizModal({
  isOpen,
  onClose,
  questions = [],
  topic = 'Study Quiz',
  onSaveScore,
}) {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  if (!isOpen || !questions || questions.length === 0) return null;

  const handleSelect = (qIdx, optLetter) => {
    if (isSubmitted) return;
    setSelectedAnswers((prev) => ({ ...prev, [qIdx]: optLetter }));
  };

  const calculateScore = () => {
    let score = 0;
    questions.forEach((q, idx) => {
      if (selectedAnswers[idx] === q.correct) {
        score++;
      }
    });
    return score;
  };

  const handleSubmit = () => {
    setIsSubmitted(true);
    const score = calculateScore();
    if (onSaveScore) {
      onSaveScore({ topic, score, total: questions.length });
    }
  };

  const handleReset = () => {
    setSelectedAnswers({});
    setIsSubmitted(false);
  };

  const finalScore = calculateScore();
  const percentage = Math.round((finalScore / questions.length) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-2xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-6 flex flex-col space-y-5 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 shrink-0">
          <div className="flex items-center gap-2 text-white font-bold text-base">
            <HelpCircle className="w-5 h-5 text-indigo-400" />
            <span>Interactive Quiz</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-normal">
              {topic}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Score banner when submitted */}
        {isSubmitted && (
          <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-900/40 to-indigo-900/40 border border-brand-500/30 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-brand-500/20 text-brand-300 flex items-center justify-center font-bold">
                <Trophy className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-semibold text-brand-300 uppercase tracking-wider">
                  Quiz Completed
                </div>
                <div className="text-base font-bold text-white">
                  Score: {finalScore} / {questions.length} ({percentage}%)
                </div>
              </div>
            </div>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Retake
            </button>
          </div>
        )}

        {/* Question List */}
        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {questions.map((q, qIdx) => {
            const userAnswer = selectedAnswers[qIdx];
            const isCorrect = userAnswer === q.correct;

            return (
              <div
                key={qIdx}
                className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/80 space-y-3"
              >
                <div className="font-semibold text-slate-100 text-sm flex items-start gap-2">
                  <span className="w-5 h-5 rounded-md bg-slate-800 text-xs text-brand-300 font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {qIdx + 1}
                  </span>
                  <span>{q.question}</span>
                </div>

                {/* Options */}
                <div className="grid gap-2">
                  {q.options.map((opt, oIdx) => {
                    const optLetter = opt.trim().charAt(0).toUpperCase();
                    const isSelected = userAnswer === optLetter;

                    let optionStyle =
                      'bg-slate-800/50 hover:bg-slate-800 text-slate-300 border-slate-700/60';
                    if (isSelected) {
                      optionStyle = 'bg-brand-500/20 text-brand-200 border-brand-500/60 font-medium';
                    }

                    if (isSubmitted) {
                      if (optLetter === q.correct) {
                        optionStyle = 'bg-emerald-500/20 text-emerald-200 border-emerald-500/60 font-medium';
                      } else if (isSelected && !isCorrect) {
                        optionStyle = 'bg-red-500/20 text-red-200 border-red-500/60 font-medium';
                      }
                    }

                    return (
                      <button
                        key={oIdx}
                        disabled={isSubmitted}
                        onClick={() => handleSelect(qIdx, optLetter)}
                        className={`text-left p-2.5 rounded-xl border text-xs flex items-center justify-between transition-all ${optionStyle}`}
                      >
                        <span>{opt}</span>
                        {isSubmitted && optLetter === q.correct && (
                          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                        )}
                        {isSubmitted && isSelected && !isCorrect && (
                          <XCircle className="w-4 h-4 text-red-400 shrink-0" />
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Explanation */}
                {isSubmitted && q.explanation && (
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-400 text-xs">
                    <span className="font-semibold text-slate-300">Explanation:</span> {q.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer Submit */}
        {!isSubmitted && (
          <div className="shrink-0 pt-2 flex items-center justify-between border-t border-slate-800">
            <div className="text-xs text-slate-400">
              Answered {Object.keys(selectedAnswers).length} of {questions.length}
            </div>
            <button
              onClick={handleSubmit}
              disabled={Object.keys(selectedAnswers).length === 0}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 text-white font-medium text-xs shadow-lg shadow-brand-500/20 transition-all"
            >
              Check Answers & Submit
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
