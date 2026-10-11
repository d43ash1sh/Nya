"use client";

import React from "react";
import { SearchX, HelpCircle, ArrowRight } from "lucide-react";

interface EmptyStateProps {
  query: string;
  emptyNotice?: string | null;
  transliterationSuggestion?: string | null;
  onSuggestionClick?: (suggestion: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  query,
  emptyNotice,
  transliterationSuggestion,
  onSuggestionClick,
}) => {
  return (
    <div className="rounded-2xl bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 p-8 sm:p-12 text-center max-w-2xl mx-auto my-8 shadow-sm dark:shadow-none transition-colors duration-150">
      <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800/80 text-teal-600 dark:text-nya-teal flex items-center justify-center mx-auto mb-5 border border-slate-200 dark:border-slate-700">
        <SearchX className="w-8 h-8" />
      </div>

      <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mb-2">
        ফলাফল পোৱা নগ'ল (No results found)
      </h2>

      <p className="text-sm text-slate-600 dark:text-slate-300 mb-6 leading-relaxed">
        {emptyNotice || `We couldn't find any indexed documents matching "${query}".`}
      </p>

      {/* Suggestion if transliteration available */}
      {transliterationSuggestion && (
        <div className="mb-6 p-4 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800/40 text-left flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 dark:text-slate-400 block mb-0.5">অসমীয়া লিপিৰে বিচাৰিব নেকি? (Did you mean):</span>
            <span className="font-semibold text-teal-700 dark:text-nya-teal text-base">{transliterationSuggestion}</span>
          </div>
          {onSuggestionClick && (
            <button
              type="button"
              onClick={() => onSuggestionClick(transliterationSuggestion)}
              className="px-4 py-2 rounded-xl bg-teal-500 dark:bg-nya-teal text-slate-950 dark:text-nya-indigo text-xs font-semibold hover:bg-teal-400 dark:hover:bg-teal-300 transition-colors flex items-center gap-1.5"
            >
              <span>Search</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Recovery advice */}
      <div className="text-left bg-slate-50 dark:bg-slate-900/60 rounded-xl p-5 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-600 dark:text-slate-300">
        <div className="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-200 mb-2">
          <HelpCircle className="w-4 h-4 text-teal-600 dark:text-nya-teal" />
          <span>Search Suggestions:</span>
        </div>
        <ul className="space-y-1.5 text-slate-500 dark:text-slate-400 list-disc list-inside">
          <li>Check the spelling of your query terms.</li>
          <li>Try searching in native Assamese script (অসমীয়া লিপি).</li>
          <li>Use broader keywords or synonyms (e.g. "অসম" instead of specific administrative ward).</li>
          <li>Nya indexes permitted, lawful regional sources. Some arbitrary sites may not be indexed.</li>
        </ul>
      </div>
    </div>
  );
};
