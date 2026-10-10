import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight, RotateCw, Layers } from 'lucide-react';

export default function FlashcardsModal({ isOpen, onClose, flashcards = [], topic = 'Study Topic' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  if (!isOpen || !flashcards || flashcards.length === 0) return null;

  const currentCard = flashcards[currentIndex];

  const handleNext = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % flashcards.length);
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-6 flex flex-col space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2 text-white font-bold text-base">
            <Layers className="w-5 h-5 text-brand-400" />
            <span>Interactive Flashcards</span>
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

        {/* Card Flip View */}
        <div
          onClick={() => setIsFlipped(!isFlipped)}
          className="cursor-pointer min-h-[220px] rounded-2xl bg-gradient-to-b from-slate-800/80 to-slate-800/30 border border-slate-700/60 p-8 flex flex-col items-center justify-center text-center transition-all duration-300 hover:border-brand-500/50 shadow-inner group relative"
        >
          <span className="absolute top-4 left-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
            {isFlipped ? 'Answer' : 'Question / Concept'}
          </span>
          <span className="absolute top-4 right-4 text-xs text-brand-400 flex items-center gap-1 group-hover:scale-105 transition-transform">
            <RotateCw className="w-3.5 h-3.5" />
            Click to Flip
          </span>

          <p className="text-base sm:text-lg font-medium text-slate-100 max-w-md leading-relaxed">
            {isFlipped ? currentCard.back : currentCard.front}
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-400 font-medium">
            Card {currentIndex + 1} of {flashcards.length}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrev}
              className="p-2.5 rounded-xl bg-slate-800 text-slate-200 hover:bg-slate-700 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleNext}
              className="p-2.5 rounded-xl bg-brand-600 text-white hover:bg-brand-500 transition-colors font-medium flex items-center gap-1 text-xs px-4"
            >
              Next Card
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
