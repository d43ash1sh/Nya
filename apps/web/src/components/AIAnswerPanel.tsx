"use client";

import React, { useState } from "react";
import { AIAnswer, CitationItem } from "@/types/contracts";
import { Sparkles, ChevronDown, ChevronUp, ExternalLink, ShieldCheck, AlertCircle } from "lucide-react";

interface AIAnswerPanelProps {
  aiAnswer?: AIAnswer | null;
}

export const AIAnswerPanel: React.FC<AIAnswerPanelProps> = ({ aiAnswer }) => {
  const [sourcesExpanded, setSourcesExpanded] = useState(false);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number | null>(null);

  if (!aiAnswer) return null;

  const isGrounded = aiAnswer.status === "grounded";
  const citations = aiAnswer.citations || [];

  // Parse inline citations [1], [2] to make them interactive buttons
  const renderInteractiveText = (text: string) => {
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citationNum = parseInt(match[1], 10);
        const hasSource = citations.some((c) => c.citation_index === citationNum);
        return (
          <button
            key={index}
            type="button"
            onClick={() => {
              setActiveCitationIndex(citationNum);
              setSourcesExpanded(true);
            }}
            title={hasSource ? `View source [${citationNum}]` : `Source [${citationNum}]`}
            aria-label={`Source citation ${citationNum}`}
            className="inline-flex items-center justify-center px-1.5 py-0.2 mx-0.5 text-xs font-semibold rounded bg-teal-100 dark:bg-nya-teal/20 text-teal-800 dark:text-nya-teal hover:bg-teal-200 dark:hover:bg-nya-teal/30 hover:underline border border-teal-300 dark:border-nya-teal/40 transition-colors align-baseline"
          >
            {citationNum}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <section
      aria-labelledby="ai-answer-heading"
      className="rounded-2xl bg-teal-50/60 dark:bg-slate-800/90 border border-teal-200 dark:border-teal-500/30 p-5 sm:p-6 mb-8 shadow-sm dark:shadow-xl relative overflow-hidden backdrop-blur-sm transition-colors duration-150"
    >
      {/* Top Banner Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-teal-100 dark:border-slate-700/60 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-teal-500/20 text-teal-700 dark:text-nya-teal">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 id="ai-answer-heading" className="text-sm sm:text-base font-bold text-slate-900 dark:text-nya-white">
              ঞ Grounded AI Answer
            </h2>
            <p className="text-xs text-slate-500 dark:text-nya-slate">
              Generated strictly from retrieved evidence with verifiable source citations
            </p>
          </div>
        </div>

        {isGrounded && citations.length > 0 && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-teal-100/80 dark:bg-teal-950/80 text-teal-800 dark:text-nya-teal border border-teal-300 dark:border-teal-800/40">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{citations.length} Verified {citations.length === 1 ? "Source" : "Sources"}</span>
          </div>
        )}
      </div>

      {/* Answer Body */}
      <div className="text-slate-800 dark:text-slate-100 text-sm sm:text-base leading-relaxed mb-4">
        {isGrounded ? (
          renderInteractiveText(aiAnswer.answer)
        ) : (
          <div className="flex items-start gap-3 p-3.5 rounded-xl bg-amber-50 dark:bg-slate-800/70 border border-amber-200 dark:border-slate-700 text-slate-800 dark:text-slate-300 text-sm">
            <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <p className="font-semibold text-slate-900 dark:text-slate-200">{aiAnswer.answer}</p>
                {aiAnswer.status === "rate_limited" && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800/60 font-medium">
                    Quota Limit Reached
                  </span>
                )}
                {aiAnswer.status === "insufficient_evidence" && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium">
                    Insufficient Evidence
                  </span>
                )}
              </div>
              {aiAnswer.disclaimer && (
                <p className="text-xs text-slate-600 dark:text-slate-400">{aiAnswer.disclaimer}</p>
              )}
              {aiAnswer.retry_after_seconds && (
                <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
                  Estimated provider quota reset window: ~{Math.ceil(aiAnswer.retry_after_seconds / 60)} minutes
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Expandable Sources Drawer */}
      {citations.length > 0 && (
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setSourcesExpanded(!sourcesExpanded)}
            className="flex items-center gap-2 text-xs font-semibold text-teal-700 dark:text-nya-teal hover:text-teal-900 dark:hover:text-teal-300 transition-colors focus:outline-none"
            aria-expanded={sourcesExpanded}
          >
            <span>{sourcesExpanded ? "Hide sources" : `View cited sources (${citations.length})`}</span>
            {sourcesExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {sourcesExpanded && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 pt-3 border-t border-teal-100 dark:border-slate-800 animate-fadeIn">
              {citations.map((c) => {
                const isSelected = activeCitationIndex === c.citation_index;
                return (
                  <div
                    key={c.document_id}
                    className={`rounded-xl p-3 border transition-all ${
                      isSelected
                        ? "bg-teal-50 dark:bg-teal-950/50 border-teal-400 dark:border-nya-teal"
                        : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-500 dark:bg-nya-teal text-white dark:text-nya-indigo font-bold text-xs flex-shrink-0">
                        {c.citation_index}
                      </span>
                      <span className="text-xs font-medium text-slate-500 dark:text-slate-400 truncate">
                        {c.source_domain}
                      </span>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-auto text-slate-400 hover:text-teal-600 dark:hover:text-nya-teal transition-colors"
                        title="Open source in new tab"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-slate-900 dark:text-slate-200 hover:text-blue-600 dark:hover:text-cyan-300 line-clamp-1 mb-1 block"
                    >
                      {c.title}
                    </a>
                    <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
                      {c.snippet}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Latency & Disclaimer footer */}
      <div className="mt-4 pt-3 border-t border-teal-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 dark:text-nya-slate flex-wrap gap-2">
        <span>{aiAnswer.disclaimer || "AI-generated response based strictly on cited evidence."}</span>
        <div className="flex items-center gap-2 text-[10px]">
          {aiAnswer.request_id && (
            <span className="font-mono text-slate-400 dark:text-slate-500">Ref: {aiAnswer.request_id}</span>
          )}
          {aiAnswer.model_name && (
            <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
              {aiAnswer.model_name}
            </span>
          )}
          {aiAnswer.latency_ms > 0 && <span>Inference: {aiAnswer.latency_ms}ms</span>}
        </div>
      </div>
    </section>
  );
};
