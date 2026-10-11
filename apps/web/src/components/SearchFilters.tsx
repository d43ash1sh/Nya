"use client";

import React from "react";
import { LanguageType, DateFilter, SafeSearchLevel } from "@/types/contracts";
import { Calendar, Shield, Sparkles } from "lucide-react";

interface SearchFiltersProps {
  language: LanguageType;
  dateFilter: DateFilter;
  safeSearch: SafeSearchLevel;
  enableAi: boolean;
  onFilterChange: (filters: {
    language?: LanguageType;
    dateFilter?: DateFilter;
    safeSearch?: SafeSearchLevel;
    enableAi?: boolean;
  }) => void;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  language,
  dateFilter,
  safeSearch,
  enableAi,
  onFilterChange,
}) => {
  return (
    <div className="flex items-center gap-3 py-3 overflow-x-auto text-xs text-slate-600 dark:text-slate-300 border-b border-slate-200 dark:border-slate-800/80 mb-6 scrollbar-none transition-colors duration-150">
      {/* Language filter */}
      <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-900/60 p-1 rounded-xl border border-slate-200 dark:border-slate-800">
        <button
          type="button"
          onClick={() => onFilterChange({ language: "all" as LanguageType })}
          className={`px-3 py-1 rounded-lg font-medium transition-colors ${
            language === "all"
              ? "bg-white dark:bg-slate-800 text-teal-700 dark:text-nya-teal shadow-sm"
              : "hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          All Languages
        </button>
        <button
          type="button"
          onClick={() => onFilterChange({ language: "as_native" as LanguageType })}
          className={`px-3 py-1 rounded-lg font-medium transition-colors ${
            language === "as_native"
              ? "bg-white dark:bg-slate-800 text-teal-700 dark:text-nya-teal shadow-sm"
              : "hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          অসমীয়া (Assamese)
        </button>
        <button
          type="button"
          onClick={() => onFilterChange({ language: "en" as LanguageType })}
          className={`px-3 py-1 rounded-lg font-medium transition-colors ${
            language === "en"
              ? "bg-white dark:bg-slate-800 text-teal-700 dark:text-nya-teal shadow-sm"
              : "hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          English
        </button>
      </div>

      {/* Date Filter Dropdown */}
      <div className="relative inline-flex items-center bg-slate-100 dark:bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800">
        <Calendar className="w-3.5 h-3.5 mr-1.5 text-slate-400 dark:text-nya-slate" />
        <select
          value={dateFilter}
          onChange={(e) => onFilterChange({ dateFilter: e.target.value as DateFilter })}
          aria-label="Filter results by publication date"
          className="bg-transparent border-0 text-slate-700 dark:text-slate-300 text-xs focus:ring-0 focus:outline-none cursor-pointer pr-1"
        >
          <option value="all" className="bg-white dark:bg-slate-900">Any Time</option>
          <option value="past_24h" className="bg-white dark:bg-slate-900">Past 24 Hours</option>
          <option value="past_week" className="bg-white dark:bg-slate-900">Past Week</option>
          <option value="past_month" className="bg-white dark:bg-slate-900">Past Month</option>
          <option value="past_year" className="bg-white dark:bg-slate-900">Past Year</option>
        </select>
      </div>

      {/* Safe Search Toggle */}
      <div className="relative inline-flex items-center bg-slate-100 dark:bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800">
        <Shield className="w-3.5 h-3.5 mr-1.5 text-slate-400 dark:text-nya-slate" />
        <select
          value={safeSearch}
          onChange={(e) => onFilterChange({ safeSearch: e.target.value as SafeSearchLevel })}
          aria-label="Filter safe search mode"
          className="bg-transparent border-0 text-slate-700 dark:text-slate-300 text-xs focus:ring-0 focus:outline-none cursor-pointer pr-1"
        >
          <option value="moderate" className="bg-white dark:bg-slate-900">SafeSearch: Moderate</option>
          <option value="strict" className="bg-white dark:bg-slate-900">SafeSearch: Strict</option>
          <option value="off" className="bg-white dark:bg-slate-900">SafeSearch: Off</option>
        </select>
      </div>

      {/* AI Toggle */}
      <button
        type="button"
        onClick={() => onFilterChange({ enableAi: !enableAi })}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border transition-all ${
          enableAi
            ? "bg-teal-50 dark:bg-teal-950/60 border-teal-300 dark:border-nya-teal/50 text-teal-700 dark:text-nya-teal font-medium"
            : "bg-slate-100 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        }`}
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span>AI Answer: {enableAi ? "On" : "Off"}</span>
      </button>
    </div>
  );
};
