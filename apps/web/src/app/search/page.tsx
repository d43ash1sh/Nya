"use client";

import React, { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Header } from "../../components/Header";
import { SearchResultItem } from "../../components/SearchResultItem";
import { AIAnswerPanel } from "../../components/AIAnswerPanel";
import { SearchFilters } from "../../components/SearchFilters";
import { EmptyState } from "../../components/EmptyState";
import { FeedbackModal } from "../../components/FeedbackModal";
import { fetchSearch } from "../../lib/api";
import {
  SearchResponse,
  LanguageType,
  DateFilter,
  SafeSearchLevel,
  SortOption,
} from "@/types/contracts";
import { AlertCircle, RefreshCw, ArrowRight, ChevronLeft, ChevronRight, Sparkles, Clock, ArrowUpDown } from "lucide-react";

function SearchResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const query = searchParams.get("q") || "";
  const pageParam = parseInt(searchParams.get("page") || "1", 10);
  const [page, setPage] = useState(isNaN(pageParam) || pageParam < 1 ? 1 : pageParam);

  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters state (Newest first is the default order)
  const [language, setLanguage] = useState<LanguageType>("all");
  const [dateFilter, setDateFilter] = useState<DateFilter>("all");
  const [safeSearch, setSafeSearch] = useState<SafeSearchLevel>("moderate");
  const [sort, setSort] = useState<SortOption>(
    (searchParams.get("sort") as SortOption) === "relevance" ? "relevance" : "newest"
  );
  const [enableAi, setEnableAi] = useState(true);

  const abortControllerRef = useRef<AbortController | null>(null);

  const executeSearch = useCallback(
    async (
      q: string,
      p: number,
      lang: LanguageType,
      date: DateFilter,
      safe: SafeSearchLevel,
      sortOrder: SortOption,
      ai: boolean
    ) => {
      if (!q.trim()) {
        setData(null);
        setLoading(false);
        return;
      }

      // Abort in-flight requests to prevent race conditions
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        const res = await fetchSearch({
          query: q,
          page: p,
          pageSize: 10,
          language: lang,
          dateFilter: date,
          safeSearch: safe,
          sort: sortOrder,
          enableAi: ai,
          signal: controller.signal,
        });
        setData(res);
      } catch (err: any) {
        if (err.name === "AbortError") {
          return;
        }
        console.error("Search failed:", err);
        setError(
          err.message || "Could not connect to Nya Search API. Please ensure the backend is running."
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    executeSearch(query, page, language, dateFilter, safeSearch, sort, enableAi);
  }, [query, page, language, dateFilter, safeSearch, sort, enableAi, executeSearch]);

  const handleFilterChange = (newFilters: {
    language?: LanguageType;
    dateFilter?: DateFilter;
    safeSearch?: SafeSearchLevel;
    sort?: SortOption;
    enableAi?: boolean;
  }) => {
    setPage(1);
    if (newFilters.language !== undefined) setLanguage(newFilters.language);
    if (newFilters.dateFilter !== undefined) setDateFilter(newFilters.dateFilter);
    if (newFilters.safeSearch !== undefined) setSafeSearch(newFilters.safeSearch);
    if (newFilters.sort !== undefined) setSort(newFilters.sort);
    if (newFilters.enableAi !== undefined) setEnableAi(newFilters.enableAi);
  };

  const handleSearchSubmit = (newQuery: string) => {
    setPage(1);
    router.push(`/search?q=${encodeURIComponent(newQuery)}`);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    router.push(`/search?q=${encodeURIComponent(query)}&page=${newPage}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const totalPages = data ? Math.max(1, Math.ceil(data.total_results / (data.page_size || 10))) : 1;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-nya-indigo text-slate-900 dark:text-nya-white transition-colors duration-150">
      <Header initialQuery={query} onSearch={handleSearchSubmit} />

      <main className="max-w-5xl w-full mx-auto px-4 sm:px-8 py-6 flex-1">
        {/* Working Search Filters */}
        <SearchFilters
          language={language}
          dateFilter={dateFilter}
          safeSearch={safeSearch}
          sort={sort}
          enableAi={enableAi}
          onFilterChange={handleFilterChange}
        />

        {/* Professional Loading State Skeletons */}
        {loading && (
          <div className="space-y-6 pt-2" aria-busy="true" aria-label="Loading search results">
            {/* Branded loading indicator */}
            <div className="flex items-center gap-3 py-3 px-4 rounded-xl bg-teal-50 dark:bg-slate-800/60 border border-teal-200 dark:border-teal-500/20 text-teal-800 dark:text-nya-teal text-xs font-medium animate-pulse">
              <span className="font-bold text-base text-[#5CE1D0] bg-slate-900 rounded-lg px-2 py-0.5">ঞ</span>
              <span>Searching multi-source index and synthesizing grounded results…</span>
            </div>

            {enableAi && (
              <div className="rounded-2xl bg-teal-50/50 dark:bg-slate-800/60 border border-teal-100 dark:border-slate-700/50 p-6 mb-8 animate-pulse">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-5 h-5 rounded-lg bg-teal-200 dark:bg-slate-700"></div>
                  <div className="h-4 bg-teal-200 dark:bg-slate-700 rounded w-1/4"></div>
                </div>
                <div className="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-full mb-2.5"></div>
                <div className="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-4/5 mb-2.5"></div>
                <div className="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-2/3"></div>
              </div>
            )}

            {[1, 2, 3].map((n) => (
              <div key={n} className="rounded-xl p-5 bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800/60 animate-pulse shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-4 h-4 rounded-full bg-slate-200 dark:bg-slate-700"></div>
                  <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
                </div>
                <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-3/5 mb-3"></div>
                <div className="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-full mb-2"></div>
                <div className="h-3.5 bg-slate-200 dark:bg-slate-700 rounded w-4/5"></div>
              </div>
            ))}
          </div>
        )}

        {/* Error / Network Failure State */}
        {!loading && error && (
          <div className="rounded-2xl p-6 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-slate-800 dark:text-slate-200 my-6 shadow-sm">
            <div className="flex items-center gap-3 mb-2 text-rose-600 dark:text-rose-400 font-semibold">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>Search Service Disconnected</span>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">{error}</p>
            <button
              type="button"
              onClick={() => executeSearch(query, page, language, dateFilter, safeSearch, sort, enableAi)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 text-xs font-semibold text-white transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Search</span>
            </button>
          </div>
        )}

        {/* Search Results Display */}
        {!loading && !error && data && (
          <div>
            {/* Transliteration / Spelling Suggestion Banner */}
            {data.transliteration_suggestion && (
              <div className="flex items-center gap-2 text-sm mb-5 p-3.5 rounded-xl bg-teal-50 dark:bg-teal-950/50 border border-teal-200 dark:border-teal-800/50 text-slate-800 dark:text-slate-200 shadow-sm">
                <span className="text-slate-600 dark:text-slate-400">অসমীয়া লিপিৰে বিচাৰক (Did you mean):</span>
                <button
                  type="button"
                  onClick={() => handleSearchSubmit(data.transliteration_suggestion!)}
                  className="font-bold text-teal-700 dark:text-nya-teal hover:underline text-base"
                >
                  {data.transliteration_suggestion}
                </button>
              </div>
            )}

            {/* Freshness limitation notice if time-sensitive intent detected but no fresh verified results exist */}
            {data.freshness_notice && (
              <div className="flex items-start gap-3 p-4 mb-5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-slate-800 dark:text-slate-200 shadow-sm text-xs">
                <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="font-semibold text-amber-800 dark:text-amber-300">
                    Freshness Notice
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {data.freshness_notice}
                  </p>
                </div>
              </div>
            )}

            {/* Results count & latency */}
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-nya-slate mb-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span>
                  Found {data.total_results} results ({data.latency_ms} ms)
                  {totalPages > 1 && ` • Page ${page} of ${totalPages}`}
                </span>
                {data.sort && (
                  <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 font-medium text-slate-600 dark:text-slate-300">
                    Sorted: {data.sort === "newest" ? "Newest first" : "Relevance"}
                  </span>
                )}
                {data.is_time_sensitive_query && (
                  <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800/50 text-blue-700 dark:text-blue-300 font-medium">
                    Time-sensitive query
                  </span>
                )}
              </div>
              <FeedbackModal query={query} />
            </div>

            {/* AI Grounded Answer Section (Page 1 only for clarity) */}
            {enableAi && page === 1 && data.ai_answer && (
              <AIAnswerPanel aiAnswer={data.ai_answer} />
            )}

            {/* Organic Ranked Search Results */}
            {data.results && data.results.length > 0 ? (
              <section aria-label="Web search results" className="space-y-4">
                <h3 className="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold mb-2">
                  Ranked Web Results
                </h3>
                {data.results.map((res, idx) => (
                  <SearchResultItem key={res.id} result={res} index={idx} />
                ))}

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <nav
                    aria-label="Search results pagination"
                    className="flex items-center justify-center gap-2 pt-8 pb-4 mt-6 border-t border-slate-200 dark:border-slate-800"
                  >
                    <button
                      type="button"
                      disabled={page <= 1}
                      onClick={() => handlePageChange(page - 1)}
                      className="inline-flex items-center gap-1 px-3.5 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:border-teal-500 dark:hover:border-nya-teal disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>Previous</span>
                    </button>

                    <div className="flex items-center gap-1.5 px-3 text-xs font-medium text-slate-600 dark:text-slate-400">
                      <span>Page {page} of {totalPages}</span>
                    </div>

                    <button
                      type="button"
                      disabled={page >= totalPages}
                      onClick={() => handlePageChange(page + 1)}
                      className="inline-flex items-center gap-1 px-3.5 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:border-teal-500 dark:hover:border-nya-teal disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
                    >
                      <span>Next</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </nav>
                )}
              </section>
            ) : (
              <EmptyState
                query={query}
                emptyNotice={data.empty_index_notice}
                transliterationSuggestion={data.transliteration_suggestion}
                onSuggestionClick={handleSearchSubmit}
              />
            )}

            {/* Related Queries */}
            {data.related_queries && data.related_queries.length > 0 && (
              <div className="mt-12 pt-6 border-t border-slate-200 dark:border-slate-800">
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                  সম্পৰ্কিত সন্ধান (Related Searches)
                </h4>
                <div className="flex flex-wrap gap-2">
                  {data.related_queries.map((relQ, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSearchSubmit(relQ)}
                      className="px-3.5 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-teal-500/50 dark:hover:border-nya-teal/40 text-xs text-slate-700 dark:text-slate-300 hover:text-teal-700 dark:hover:text-nya-teal transition-all flex items-center gap-1.5 shadow-sm"
                    >
                      <span>{relQ}</span>
                      <ArrowRight className="w-3 h-3 opacity-60" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 py-4 px-4 sm:px-8 mt-auto text-xs text-slate-500 dark:text-nya-slate transition-colors duration-150">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 ঞ (Nya) Search</span>
          <div className="flex items-center gap-1.5">
            <span>made by</span>
            <a
              href="https://github.com/saikiabigratom-design"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-900 dark:text-slate-200 hover:text-teal-600 dark:hover:text-nya-teal font-medium underline underline-offset-4 decoration-teal-500/40 hover:decoration-teal-500 transition-colors"
            >
              Bigratom Saikia
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-nya-indigo text-slate-900 dark:text-nya-white">
          <Header initialQuery="" showSearchBox={true} />
          <div className="max-w-5xl w-full mx-auto px-4 sm:px-8 py-12 flex-1 flex items-center justify-center text-slate-400 text-sm">
            Loading ঞ Search...
          </div>
          <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 py-4 px-4 sm:px-8 mt-auto text-xs text-slate-500 dark:text-nya-slate">
            <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
              <span>© 2026 ঞ (Nya) Search</span>
              <div className="flex items-center gap-1.5">
                <span>made by</span>
                <a
                  href="https://github.com/saikiabigratom-design"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-900 dark:text-slate-200 hover:text-teal-600 dark:hover:text-nya-teal font-medium underline underline-offset-4 decoration-teal-500/40 hover:decoration-teal-500 transition-colors"
                >
                  Bigratom Saikia
                </a>
              </div>
            </div>
          </footer>
        </div>
      }
    >
      <SearchResultsContent />
    </Suspense>
  );
}
