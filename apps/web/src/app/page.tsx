"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { BrandMark } from "../components/BrandMark";
import { SearchBox } from "../components/SearchBox";
import { ThemeToggle } from "../components/ThemeToggle";
import { Sparkles, RotateCw } from "lucide-react";

// Curated pool of 48 diverse multilingual suggestions
const SUGGESTION_POOL = [
  // Assamese Culture & Traditions
  { label: "ৰঙালী বিহু", query: "ৰঙালী বিহু অসমৰ জাতীয় উৎসৱ" },
  { label: "সত্ৰীয়া নৃত্য", query: "সত্ৰীয়া নৃত্যৰ ইতিহাস আৰু বৈশিষ্ট্য" },
  { label: "বৰগীত আৰু অংকীয়া নাট", query: "মহাপুৰুষ শ্ৰীমন্ত শংকৰদেৱৰ বৰগীত" },
  { label: "জিকিৰ আৰু জাৰী", query: "আজান ফকীৰৰ জিকিৰ আৰু জাৰী" },
  { label: "মুগা আৰু পাট ৰেচম", query: "অসমৰ সোণালী মুগা ৰেচম শিল্প" },
  { label: "বিহু গীতৰ পৰম্পৰা", query: "বিহু গীত আৰু সুৰৰ ঐতিহ্য" },

  // Assam Geography & Wildlife
  { label: "কাজিৰঙা গঁড়", query: "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান এশিঙীয়া গঁড়" },
  { label: "ব্ৰহ্মপুত্ৰ নদীৰ উৎপত্তি", query: "ব্ৰহ্মপুত্ৰ নদীৰ উৎপত্তি আৰু গতিপথ" },
  { label: "মাজুলী নদীদ্বীপ", query: "পৃথিৱীৰ সৰ্ববৃহৎ নদীদ্বীপ মাজুলী" },
  { label: "মানাহ ৰাষ্ট্ৰীয় উদ্যান", query: "মানাহ ৰাষ্ট্ৰীয় উদ্যান ইউনেস্কো ঐতিহ্য" },
  { label: "দিহিং পাটকাই বৰ্ষাৰণ্য", query: "দিহিং পাটকাই ৰাষ্ট্ৰীয় উদ্যান জৈৱ বৈচিত্ৰ্য" },
  { label: "উমানন্দ দ্বীপ", query: "পৃথিৱীৰ আটাইতকৈ ক্ষুদ্ৰ নদীদ্বীপ উমানন্দ" },

  // Education & Literature
  { label: "গুৱাহাটী বিশ্ববিদ্যালয়", query: "গুৱাহাটী বিশ্ববিদ্যালয় ইতিহাস আৰু পাঠ্যক্ৰম" },
  { label: "লক্ষ্মীনাথ বেজবৰুৱা", query: "ৰসৰাজ লক্ষ্মীনাথ বেজবৰুৱা সাহিত্য সম্ভাৰ" },
  { label: "ড° ভূপেন হাজৰিকা", query: "সুধাকণ্ঠ ড° ভূপেন হাজৰিকাৰ গীত আৰু জীৱন" },
  { label: "হেমকোষ অভিধান", query: "হেমচন্দ্ৰ বৰুৱাৰ হেমকোষ অভিধান" },
  { label: "তেজপুৰ বিশ্ববিদ্যালয়", query: "তেজপুৰ বিশ্ববিদ্যালয় গৱেষণা" },
  { label: "আনন্দৰাম ঢেকিয়াল ফুকন", query: "অসমীয়া ভাষা উন্নতি সাধিনী সভা" },

  // History & Heritage
  { label: "লাচিত বৰফুকন", query: "লাচিত বৰফুকন শৰাইঘাটৰ যুদ্ধ ১৬৭১" },
  { label: "চৰাইদেউ মৈদাম", query: "চৰাইদেউ মৈদাম ইউনেস্কো বিশ্ব ঐতিহ্য" },
  { label: "আহোম ৰাজবংশ", query: "আহোম ৰাজবংশৰ ৬০০ বছৰীয়া শাসন" },
  { label: "কাৰেং ঘৰ আৰু তলাতল ঘৰ", query: "ৰংপুৰৰ ঐতিহাসিক কাৰেং ঘৰ" },
  { label: "সূৰ্য পাহাৰ গোৱালপাৰা", query: "শ্ৰীশ্ৰী সূৰ্য পাহাৰ প্ৰত্নতাত্ত্বিক স্থান" },
  { label: "মণিৰাম দেৱান", query: "১৮৫৭ চনৰ স্বাধীনতা সংগ্ৰাম আৰু মণিৰাম দেৱান" },

  // Science, Technology & Programming
  { label: "Python programming", query: "Python programming language beginner tutorial" },
  { label: "Quantum computing", query: "Quantum computing principles and applications" },
  { label: "কৃত্ৰিম বুদ্ধিমত্তা", query: "কৃত্ৰিম বুদ্ধিমত্তা আৰু মেচিন লাৰ্নিং" },
  { label: "চন্দ্ৰযান-৩ অভিযান", query: "ইছৰো চন্দ্ৰযান-৩ চন্দ্ৰপৃষ্ঠত সফল অৱতৰণ" },
  { label: "Next.js Framework", query: "Next.js React full stack framework features" },
  { label: "নৱীকৰণযোগ্য শক্তি", query: "সৌৰশক্তি আৰু নৱীকৰণযোগ্য শক্তি প্ৰযুক্তি" },

  // General Knowledge & Governance
  { label: "ভাৰতৰ সংবিধান", query: "ভাৰতীয় সংবিধানৰ মৌলিক অধিকাৰ আৰু কৰ্তব্য" },
  { label: "অৰুণোদোদয় আঁচনি", query: "অৰুণোদোদয় ৩.০ আঁচনিৰ নিৰ্দেশনা" },
  { label: "Guwahati Smart City", query: "Guwahati Smart City infrastructure developments" },
  { label: "Assam Tea Industry", query: "History and economy of Assam tea industry" },
  { label: "Indian Space Research", query: "ISRO space missions and achievements" },
  { label: "বৰপেটা সত্ৰ", query: "বৰপেটা সত্ৰ মহাপুৰুষ মাধৱদেৱ" },

  // Romanized Assamese & Transliterated
  { label: "axom bhugol", query: "axom bhugol aru nodi" },
  { label: "bihu geet", query: "bihu geet porompora aru itihas" },
  { label: "kaziranga rhino", query: "kaziranga one horned rhinoceros conservation" },
  { label: "guwahati biswabidyalay", query: "guwahati biswabidyalay admission courses" },
  { label: "sualkuchi silk", query: "sualkuchi assam silk village handloom" },
  { label: "dhekiakhowa bornamghar", query: "dhekiakhowa bornamghar jorhat history" },

  // Mixed English-Assamese
  { label: "Assam Tourism Places", query: "Top tourist destinations and wildlife in Assam" },
  { label: "Brahmaputra Bridge", query: "Brahmaputra river bridges and connectivity" },
  { label: "IIT Guwahati Research", query: "IIT Guwahati technology and science breakthroughs" },
  { label: "Gauhati High Court", query: "Gauhati High Court judgments and history" },
  { label: "Deepor Beel Ramsar Site", query: "Deepor Beel wetland bird sanctuary Guwahati" },
  { label: "National Parks Assam", query: "Seven national parks of Assam biodiversity" },
];

export default function HomePage() {
  const [displayedSuggestions, setDisplayedSuggestions] = useState<typeof SUGGESTION_POOL>([]);
  const [isRotating, setIsRotating] = useState(false);

  // Pick 6 random suggestions without immediate duplicates
  const pickRandomSuggestions = (count: number = 6) => {
    const shuffled = [...SUGGESTION_POOL].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  };

  useEffect(() => {
    setDisplayedSuggestions(pickRandomSuggestions(6));
  }, []);

  const handleShuffle = () => {
    setIsRotating(true);
    setDisplayedSuggestions(pickRandomSuggestions(6));
    setTimeout(() => setIsRotating(false), 400);
  };

  return (
    <div className="flex-1 flex flex-col justify-between min-h-screen px-4 sm:px-8 py-6 relative overflow-hidden bg-slate-50 dark:bg-gradient-to-b dark:from-nya-indigo dark:via-nya-indigo dark:to-[#0b1324] transition-colors duration-150">
      {/* Decorative background glow (Dark mode) */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] rounded-full pointer-events-none opacity-10 dark:opacity-20 blur-[120px]"
        style={{
          background: "radial-gradient(circle, #5CE1D0 0%, #111D35 70%)",
        }}
      />

      {/* Top Navbar */}
      <header className="max-w-7xl w-full mx-auto flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <BrandMark size="sm" showText={true} />
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
        </div>
      </header>

      {/* Main Hero Container */}
      <main className="max-w-3xl w-full mx-auto my-auto py-12 flex flex-col items-center text-center z-10">
        {/* Eyebrow */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-slate-200/80 dark:bg-slate-800/60 border border-slate-300 dark:border-slate-700 text-xs font-medium text-teal-700 dark:text-nya-teal mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>A search engine built with language in mind</span>
        </div>

        {/* Brand visual & Typography */}
        <div className="mb-6">
          <BrandMark size="xl" className="justify-center mb-4" />
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-3">
            Search beyond language.
          </h1>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-xl mx-auto leading-relaxed">
            Find useful information across Assamese, English, and mixed-language searches.
            Nya brings ranked web results and source-grounded AI answers together, helping you explore information and inspect the evidence behind it.
          </p>
        </div>

        {/* Prominent Search Box */}
        <div className="w-full max-w-2xl mb-5">
          <SearchBox size="large" autoFocus={true} />
        </div>

        {/* Supporting Line */}
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-medium mb-6">
          Real sources. Clear answers. Your language.
        </p>

        {/* Query suggestion chips with dynamic shuffle */}
        <div className="flex items-center justify-center flex-wrap gap-2 max-w-2xl">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mr-1">
            <span>Try searching:</span>
            <button
              type="button"
              onClick={handleShuffle}
              title="নতুন পৰামৰ্শ (Shuffle suggestions)"
              aria-label="Shuffle search suggestions"
              className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 hover:text-teal-600 dark:hover:text-nya-teal transition-all focus:outline-none"
            >
              <RotateCw className={`w-3.5 h-3.5 transition-transform duration-300 ${isRotating ? "rotate-180" : ""}`} />
            </button>
          </div>

          {displayedSuggestions.map((item, idx) => (
            <Link
              key={idx}
              href={`/search?q=${encodeURIComponent(item.query)}`}
              className="text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/70 hover:border-teal-500/50 dark:hover:border-nya-teal/50 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 hover:text-teal-700 dark:hover:text-nya-teal transition-all shadow-sm"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl w-full mx-auto pt-8 pb-4 border-t border-slate-200 dark:border-slate-800/80 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-nya-slate gap-4 z-10">
        <div className="flex items-center gap-2">
          <span>© 2026 ঞ (Nya) Search</span>
          <span>•</span>
          <span>Search beyond language.</span>
        </div>
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
      </footer>
    </div>
  );
}
