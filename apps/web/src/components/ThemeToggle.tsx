"use client";

import React, { useEffect, useState } from "react";
import { useTheme, Theme } from "./ThemeProvider";
import { Sun, Moon, Laptop } from "lucide-react";

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = "" }) => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`w-[96px] h-8 rounded-full bg-slate-800/40 animate-pulse ${className}`} />
    );
  }

  const options: { value: Theme; label: string; icon: React.ReactNode }[] = [
    { value: "light", label: "Light", icon: <Sun className="w-3.5 h-3.5" /> },
    { value: "dark", label: "Dark", icon: <Moon className="w-3.5 h-3.5" /> },
    { value: "system", label: "System", icon: <Laptop className="w-3.5 h-3.5" /> },
  ];

  return (
    <div
      role="radiogroup"
      aria-label="Theme selection"
      className={`inline-flex items-center p-0.5 rounded-full bg-slate-200/80 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/70 shadow-sm backdrop-blur-sm transition-colors ${className}`}
    >
      {options.map((opt) => {
        const isActive = theme === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={isActive}
            aria-label={`${opt.label} theme`}
            title={`${opt.label} theme`}
            onClick={() => setTheme(opt.value)}
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-all ${
              isActive
                ? "bg-white dark:bg-slate-700 text-teal-600 dark:text-nya-teal shadow-sm font-semibold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
            }`}
          >
            {opt.icon}
            <span className="hidden sm:inline text-[11px]">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};
