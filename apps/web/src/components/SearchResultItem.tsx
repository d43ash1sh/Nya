"use client";

import React from "react";
import { SearchResultItem as SearchResultItemType } from "@/types/contracts";
import { ExternalLink, CheckCircle, Calendar, Globe } from "lucide-react";

interface SearchResultItemProps {
  result: SearchResultItemType;
  index: number;
}

export const SearchResultItem: React.FC<SearchResultItemProps> = ({ result, index }) => {
  const pubDateRaw = result.published_at || result.published_date;
  const updDateRaw = result.updated_at;

  const formatDateWithTimezone = (dateStr?: string | null) => {
    if (!dateStr) return null;
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return null;
      const hasTime = dateStr.includes("T") || dateStr.includes(":");
      const options: Intl.DateTimeFormatOptions = {
        year: "numeric",
        month: "short",
        day: "numeric",
        timeZone: "Asia/Kolkata",
      };
      if (hasTime) {
        options.hour = "2-digit";
        options.minute = "2-digit";
        options.timeZoneName = "short";
      }
      return new Intl.DateTimeFormat("en-IN", options).format(d);
    } catch {
      return null;
    }
  };

  const formattedPublished = formatDateWithTimezone(pubDateRaw);
  const formattedUpdated = formatDateWithTimezone(updDateRaw);

  return (
    <article
      aria-labelledby={`result-title-${result.id}`}
      className="group relative rounded-xl p-4 sm:p-5 bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700/80 transition-all duration-200 hover:shadow-md dark:hover:shadow-lg"
    >
      {/* Source metadata header */}
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-nya-slate mb-1.5 flex-wrap">
        <div className="flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5 text-teal-600 dark:text-nya-teal/80" />
          <span className="font-semibold text-slate-800 dark:text-slate-300">{result.source_name || result.source_domain}</span>
        </div>

        {result.is_news && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-50 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800/50">
            News
          </span>
        )}

        {result.is_authoritative && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50">
            <CheckCircle className="w-3 h-3" />
            <span>Verified Source</span>
          </span>
        )}

        <span className="text-slate-400 dark:text-slate-600">•</span>
        <span className="truncate max-w-[240px] text-slate-500 dark:text-slate-400">{result.display_url}</span>

        {formattedPublished ? (
          <>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span
              className="inline-flex items-center gap-1 text-emerald-700 dark:text-emerald-400 font-medium"
              title={`Verified publication date (IST / UTC: ${pubDateRaw})`}
            >
              <Calendar className="w-3 h-3" />
              <span>Published: {formattedPublished}</span>
            </span>
          </>
        ) : formattedUpdated ? (
          <>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span
              className="inline-flex items-center gap-1 text-slate-500 dark:text-slate-400"
              title={`Last revised/updated timestamp (IST / UTC: ${updDateRaw})`}
            >
              <Calendar className="w-3 h-3 text-slate-400" />
              <span>Updated: {formattedUpdated}</span>
            </span>
          </>
        ) : (
          <>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-slate-400 dark:text-slate-500 text-[11px]" title="No verified publication timestamp">
              Undated
            </span>
          </>
        )}

        <span className="ml-auto text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800/60 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50">
          {result.language === "as" ? "অসমীয়া" : result.language === "en" ? "English" : "Multilingual"}
        </span>
      </div>

      {/* Result title link */}
      <h2 id={`result-title-${result.id}`} className="text-lg sm:text-xl font-semibold mb-2">
        <a
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-cyan-400 group-hover:text-teal-600 dark:group-hover:text-nya-teal transition-colors flex items-baseline gap-1.5 hover:underline"
        >
          <span>{result.title}</span>
          <ExternalLink className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition-opacity flex-shrink-0" />
        </a>
      </h2>

      {/* Snippet body */}
      <p className="text-sm text-slate-700 dark:text-slate-300/90 leading-relaxed font-normal">
        {result.snippet}
      </p>
    </article>
  );
};
