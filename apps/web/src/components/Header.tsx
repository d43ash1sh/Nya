"use client";

import React from "react";
import Link from "next/link";
import { BrandMark } from "./BrandMark";
import { SearchBox } from "./SearchBox";
import { ThemeToggle } from "./ThemeToggle";

interface HeaderProps {
  initialQuery?: string;
  onSearch?: (query: string) => void;
  showSearchBox?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  initialQuery = "",
  onSearch,
  showSearchBox = true,
}) => {
  return (
    <header className="sticky top-0 z-30 w-full bg-white/90 dark:bg-nya-indigo/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800/80 px-4 sm:px-8 py-3 transition-colors duration-150">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2 group flex-shrink-0" aria-label="Nya Home">
          <BrandMark size="sm" showText={true} />
        </Link>

        {/* Search input in header */}
        {showSearchBox && (
          <div className="flex-1 max-w-2xl mx-auto">
            <SearchBox initialQuery={initialQuery} onSearch={onSearch} size="default" />
          </div>
        )}

        {/* Theme Toggle */}
        <div className="flex items-center flex-shrink-0">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
