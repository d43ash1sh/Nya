"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, X, ArrowRight } from "lucide-react";

interface SearchBoxProps {
  initialQuery?: string;
  onSearch?: (query: string) => void;
  autoFocus?: boolean;
  size?: "default" | "large";
  className?: string;
}

export const SearchBox: React.FC<SearchBoxProps> = ({
  initialQuery = "",
  onSearch,
  autoFocus = false,
  size = "default",
  className = "",
}) => {
  const [query, setQuery] = useState(initialQuery);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    if (onSearch) {
      onSearch(trimmed);
    } else {
      window.location.href = `/search?q=${encodeURIComponent(trimmed)}`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setQuery("");
    }
  };

  const isLarge = size === "large";

  return (
    <form
      onSubmit={handleSubmit}
      role="search"
      aria-label="Sitewide search"
      className={`relative w-full ${className}`}
    >
      <div
        className={`relative flex items-center w-full rounded-2xl bg-white dark:bg-slate-800/90 border border-slate-300 dark:border-slate-700/80 shadow-lg dark:shadow-2xl transition-all duration-200 focus-within:border-teal-500 dark:focus-within:border-nya-teal focus-within:ring-2 focus-within:ring-teal-500/20 dark:focus-within:ring-nya-teal/20 hover:border-slate-400 dark:hover:border-slate-600 ${
          isLarge ? "p-2 sm:p-2.5" : "p-1.5"
        }`}
      >
        <div className="pl-3 sm:pl-4 text-slate-400 dark:text-nya-slate flex items-center pointer-events-none">
          <Search className={`${isLarge ? "w-6 h-6 text-teal-600 dark:text-nya-teal" : "w-5 h-5 text-slate-400 dark:text-nya-slate"}`} />
        </div>

        <input
          ref={inputRef}
          type="search"
          name="q"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus={autoFocus}
          autoComplete="off"
          spellCheck="false"
          placeholder="Search in Assamese, English, or Romanized Assamese…"
          aria-label="Search query"
          className={`w-full bg-transparent border-0 px-3 sm:px-4 text-slate-900 dark:text-nya-white placeholder:text-slate-400 dark:placeholder:text-nya-slate/70 focus:outline-none focus:ring-0 [&::-webkit-search-cancel-button]:hidden [&::-webkit-search-decoration]:hidden ${
            isLarge ? "text-base sm:text-lg py-2" : "text-sm sm:text-base py-1.5"
          }`}
        />

        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              inputRef.current?.focus();
            }}
            aria-label="Clear search input"
            className="p-1.5 mr-1 text-slate-400 dark:text-nya-slate hover:text-slate-700 dark:hover:text-nya-white rounded-full hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="submit"
          disabled={!query.trim()}
          aria-label="Submit search"
          className={`flex items-center justify-center font-semibold rounded-xl transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed ${
            isLarge
              ? "px-5 sm:px-7 py-2.5 sm:py-3 bg-teal-500 hover:bg-teal-400 dark:bg-nya-teal dark:hover:bg-teal-300 text-slate-950 dark:text-nya-indigo shadow-md hover:shadow-teal-500/20 text-sm sm:text-base"
              : "px-4 py-2 bg-teal-500 hover:bg-teal-400 dark:bg-nya-teal dark:hover:bg-teal-300 text-slate-950 dark:text-nya-indigo text-xs sm:text-sm"
          }`}
        >
          <span>Search</span>
          {isLarge && <ArrowRight className="w-4 h-4 ml-1.5 hidden sm:inline" />}
        </button>
      </div>
    </form>
  );
};
