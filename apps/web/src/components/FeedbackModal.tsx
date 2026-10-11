"use client";

import React, { useState } from "react";
import { submitFeedback } from "../lib/api";
import { ThumbsUp, ThumbsDown, MessageSquare, X, Check } from "lucide-react";

interface FeedbackModalProps {
  query: string;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({ query }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [feedbackType, setFeedbackType] = useState<"relevance" | "ai_quality" | "broken_link" | "privacy">("relevance");
  const [comment, setComment] = useState("");
  const [isPositive, setIsPositive] = useState<boolean | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await submitFeedback({
        query,
        feedback_type: feedbackType,
        is_positive: isPositive ?? undefined,
        comment: comment.trim() || undefined,
      });
      setSubmitted(true);
      setTimeout(() => {
        setIsOpen(false);
        setSubmitted(false);
        setComment("");
        setIsPositive(null);
      }, 2000);
    } catch (err) {
      console.error("Feedback submission error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-teal-600 dark:hover:text-nya-teal transition-colors py-2"
        aria-label="Send feedback"
      >
        <MessageSquare className="w-3.5 h-3.5" />
        <span>Feedback</span>
      </button>

      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="feedback-dialog-title"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
          <div className="bg-white dark:bg-nya-indigo border border-slate-200 dark:border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl relative transition-colors duration-150">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-700 dark:hover:text-white"
              aria-label="Close modal"
            >
              <X className="w-4 h-4" />
            </button>

            <h3 id="feedback-dialog-title" className="text-lg font-bold text-slate-900 dark:text-white mb-1">
              Help Improve Nya Search
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Your feedback is anonymized to protect search privacy. Raw queries are never logged.
            </p>

            {submitted ? (
              <div className="flex flex-col items-center justify-center py-6 text-center text-teal-600 dark:text-teal-400">
                <Check className="w-10 h-10 mb-2" />
                <p className="font-semibold text-sm">Thank you for your feedback!</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Thumbs selection */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setIsPositive(true)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl border text-xs font-medium transition-colors ${
                      isPositive === true
                        ? "bg-teal-50 dark:bg-teal-950/80 border-teal-500 dark:border-nya-teal text-teal-700 dark:text-nya-teal"
                        : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <ThumbsUp className="w-4 h-4" />
                    <span>Helpful</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsPositive(false)}
                    className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl border text-xs font-medium transition-colors ${
                      isPositive === false
                        ? "bg-rose-50 dark:bg-rose-950/80 border-rose-400 dark:border-rose-500 text-rose-600 dark:text-rose-400"
                        : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <ThumbsDown className="w-4 h-4" />
                    <span>Needs Improvement</span>
                  </button>
                </div>

                {/* Feedback category */}
                <div>
                  <label htmlFor="feedback-topic-select" className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1.5">
                    Feedback Topic
                  </label>
                  <select
                    id="feedback-topic-select"
                    value={feedbackType}
                    onChange={(e) => setFeedbackType(e.target.value as any)}
                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-teal-500 dark:focus:border-nya-teal"
                  >
                    <option value="relevance">Search Relevance</option>
                    <option value="ai_quality">AI Answer Accuracy & Citations</option>
                    <option value="broken_link">Broken or Inaccessible Link</option>
                    <option value="privacy">Privacy or Content Removal Request</option>
                  </select>
                </div>

                {/* Optional comment */}
                <div>
                  <label htmlFor="feedback-comments-textarea" className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1.5">
                    Comments (optional)
                  </label>
                  <textarea
                    id="feedback-comments-textarea"
                    rows={3}
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Tell us what can be improved..."
                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:border-teal-500 dark:focus:border-nya-teal resize-none"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="px-4 py-2 rounded-xl text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-5 py-2 rounded-xl bg-teal-500 dark:bg-nya-teal text-slate-950 dark:text-nya-indigo text-xs font-bold hover:bg-teal-400 dark:hover:bg-teal-300 transition-colors disabled:opacity-50"
                  >
                    {loading ? "Submitting..." : "Submit Feedback"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
};
