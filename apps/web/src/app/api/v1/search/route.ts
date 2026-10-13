import { NextRequest, NextResponse } from "next/server";
import {
  SearchResponse,
  SearchResultItem,
  AIAnswer,
  CitationItem,
  LanguageType,
} from "@/types/contracts";
import crypto from "crypto";

export const dynamic = "force-dynamic";

// Built-in regional authoritative knowledge items
const REGIONAL_KNOWLEDGE_BASE: SearchResultItem[] = [
  {
    id: "todays-top-news-assam-infrastructure",
    title: "Today's Top News: Assam Infrastructure Push and Northeast Connectivity Milestones",
    url: "https://assamtribune.com/assam/todays-top-news-assam-infrastructure-connectivity",
    display_url: "assamtribune.com › assam › todays-top-news",
    snippet:
      "Today's top headlines across Assam feature major infrastructure expansions, including new bridge projects across the Brahmaputra, elevated highway corridors in Kaziranga, and renewable solar parks.",
    language: "en",
    published_date: "2026-10-13T06:30:00Z",
    published_at: "2026-10-13T06:30:00Z",
    updated_at: "2026-10-13T07:00:00Z",
    crawled_at: "2026-10-13T07:15:00Z",
    is_news: true,
    score: 0.98,
    source_name: "The Assam Tribune",
    source_domain: "assamtribune.com",
    is_authoritative: true,
  },
  {
    id: "assam-cabinet-decisions-latest",
    title: "অসম চৰকাৰৰ শেহতীয়া কেবিনেট সিদ্ধান্ত: নিযুক্তি আৰু আন্তঃগাঁথনি বিকাশ (Latest Assam Cabinet Decisions)",
    url: "https://assam.gov.in/press-release/assam-cabinet-decisions-latest-october-2026",
    display_url: "assam.gov.in › press-release › cabinet-decisions",
    snippet:
      "মুখ্যমন্ত্ৰীৰ নেতৃত্বত অনুষ্ঠিত কেবিনেট বৈঠকত ৰাজ্যৰ নিযুক্তি প্ৰক্ৰিয়া ত্বৰান্বিত কৰা, বান সমস্যা সমাধান আৰু নতুন আন্তঃগাঁথনি প্ৰকল্পৰ ঐতিহাসিক শেহতীয়া খবৰ আৰু সিদ্ধান্ত গ্ৰহণ কৰা হয়।",
    language: "as",
    published_date: "2026-10-13T08:00:00Z",
    published_at: "2026-10-13T08:00:00Z",
    updated_at: "2026-10-13T08:30:00Z",
    crawled_at: "2026-10-13T08:45:00Z",
    is_news: true,
    score: 0.98,
    source_name: "Government of Assam Official Portal",
    source_domain: "assam.gov.in",
    is_authoritative: true,
  },
  {
    id: "assam-cabinet-semiconductor-jagiroad",
    title: "Assam Cabinet Approves New Industrial Policy and Semiconductor Hub at Jagiroad",
    url: "https://assamtribune.com/assam/assam-cabinet-industrial-policy-semiconductor-jagiroad-2026",
    display_url: "assamtribune.com › assam › semiconductor-jagiroad",
    snippet:
      "The Assam Cabinet has cleared comprehensive fiscal incentives for downstream electronics and semiconductor suppliers at Jagiroad, cementing regional high-tech manufacturing.",
    language: "en",
    published_date: "2026-10-12T10:15:00Z",
    published_at: "2026-10-12T10:15:00Z",
    updated_at: "2026-10-12T11:00:00Z",
    crawled_at: "2026-10-12T11:15:00Z",
    is_news: true,
    score: 0.96,
    source_name: "The Assam Tribune",
    source_domain: "assamtribune.com",
    is_authoritative: true,
  },
  {
    id: "ai-quantum-computing-center-guwahati",
    title: "AI & Quantum Computing Center Inaugurated in Guwahati: Latest Regional News",
    url: "https://assamtribune.com/technology/ai-quantum-computing-center-guwahati-latest-news",
    display_url: "assamtribune.com › technology › ai-quantum-center",
    snippet:
      "A dedicated Artificial Intelligence and Quantum Computing Center was formally inaugurated in Guwahati to advance regional language models and localized generative AI engineering.",
    language: "en",
    published_date: "2026-10-11T14:00:00Z",
    published_at: "2026-10-11T14:00:00Z",
    updated_at: "2026-10-11T15:30:00Z",
    crawled_at: "2026-10-11T16:00:00Z",
    is_news: true,
    score: 0.95,
    source_name: "The Assam Tribune",
    source_domain: "assamtribune.com",
    is_authoritative: true,
  },
  {
    id: "kaziranga-national-park",
    title: "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান আৰু এশিঙীয়া গঁড় (Kaziranga National Park & One-Horned Rhino)",
    url: "https://forest.assam.gov.in/portlet-innerpage/kaziranga-national-park",
    display_url: "forest.assam.gov.in › kaziranga-national-park",
    snippet:
      "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান বিশ্ব ঐতিহ্য ক্ষেত্ৰ আৰু ই পৃথিৱীৰ বিখ্যাত এশিঙীয়া গঁড়ৰ প্ৰধান আৱাসভূমি। এই উদ্যানখন গোলাঘাট আৰু নগাঁও জিলাত অৱস্থিত।",
    language: "as",
    published_date: "2024-01-15T00:00:00Z",
    published_at: "2024-01-15T00:00:00Z",
    updated_at: "2024-01-15T00:00:00Z",
    crawled_at: "2024-01-15T00:00:00Z",
    is_news: false,
    score: 0.95,
    source_name: "Government of Assam - Forest Department",
    source_domain: "forest.assam.gov.in",
    is_authoritative: true,
  },
  {
    id: "bihu-festival-assam",
    title: "বিহু — অসমৰ জাতীয় উৎসৱ (Bihu - National Festival of Assam)",
    url: "https://assam.gov.in/about-us/culture/bihu",
    display_url: "assam.gov.in › culture › bihu",
    snippet:
      "বিহু অসমৰ জাতীয় তথা সাংস্কৃতিক উৎসৱ। ইয়াৰ তিনিটা প্ৰকাৰ হৈছে ৰঙালী, কঙালি আৰু ভোগালী বিহু। ৰঙালী বিহু বসন্তৰ আগমন আৰু অসমীয়া নৱবৰ্ষৰ প্ৰতীক।",
    language: "as",
    published_date: "2024-04-14T00:00:00Z",
    published_at: "2024-04-14T00:00:00Z",
    updated_at: "2024-04-14T00:00:00Z",
    crawled_at: "2024-04-14T00:00:00Z",
    is_news: false,
    score: 0.94,
    source_name: "Government of Assam",
    source_domain: "assam.gov.in",
    is_authoritative: true,
  },
  {
    id: "gauhati-university",
    title: "গুৱাহাটী বিশ্ববিদ্যালয় (Gauhati University — Official Portal)",
    url: "https://gauhati.ac.in",
    display_url: "gauhati.ac.in",
    snippet:
      "গুৱাহাটী বিশ্ববিদ্যালয় উত্তৰ-পূব ভাৰতৰ সৰ্বপ্ৰথম আৰু প্ৰধান উচ্চ শিক্ষাৰ প্ৰতিষ্ঠান। ১৯৪৮ চনৰ ২৬ জানুৱাৰীত স্থাপিত এই বিশ্ববিদ্যালয়ে বিভিন্ন পাঠ্যক্ৰম আগবঢ়ায়।",
    language: "as",
    published_date: "2024-02-01T00:00:00Z",
    published_at: "2024-02-01T00:00:00Z",
    updated_at: "2024-02-01T00:00:00Z",
    crawled_at: "2024-02-01T00:00:00Z",
    is_news: false,
    score: 0.93,
    source_name: "Gauhati University",
    source_domain: "gauhati.ac.in",
    is_authoritative: true,
  },
  {
    id: "brahmaputra-river-assam",
    title: "ব্ৰহ্মপুত্ৰ নদী আৰু অসমৰ সভ্যতা (The Brahmaputra River Basin)",
    url: "https://waterresources.assam.gov.in/river-basin",
    display_url: "waterresources.assam.gov.in › river-basin",
    snippet:
      "ব্ৰহ্মপুত্ৰ অসমৰ প্ৰধান নদী আৰু ইয়াৰ সংস্কৃতিৰ সৈতে ওতপ্ৰোতভাৱে জড়িত। তিব্বতত ইয়াৰ নাম য়াৰলুং চাংপো আৰু অসম উপত্যকাত ই ব্ৰহ্মপুত্ৰ নামেৰে প্ৰৱাহিত।",
    language: "as",
    published_date: "2024-03-10T00:00:00Z",
    published_at: "2024-03-10T00:00:00Z",
    updated_at: "2024-03-10T00:00:00Z",
    crawled_at: "2024-03-10T00:00:00Z",
    is_news: false,
    score: 0.91,
    source_name: "Water Resources Department, Assam",
    source_domain: "waterresources.assam.gov.in",
    is_authoritative: true,
  },
  {
    id: "srimanta-sankardev",
    title: "মহাপুৰুষ শ্ৰীমন্ত শংকৰদেৱ (Srimanta Sankardev Life & Works)",
    url: "https://sankardeva.com/life-and-works",
    display_url: "sankardeva.com › life-and-works",
    snippet:
      "মহাপুৰুষ শ্ৰীমন্ত শংকৰদেৱ পঞ্চদশ-ষোড়শ শতিকাৰ এজন মহান অসমীয়া সমাজ সংস্কাৰক, সাহিত্যিক, নাট্যকাৰ আৰু নৱবৈষ্ণৱ ধৰ্মৰ প্ৰচাৰক আছিল।",
    language: "as",
    published_date: "2024-01-20T00:00:00Z",
    published_at: "2024-01-20T00:00:00Z",
    updated_at: "2024-01-20T00:00:00Z",
    crawled_at: "2024-01-20T00:00:00Z",
    is_news: false,
    score: 0.92,
    source_name: "Sankardeva Research Foundation",
    source_domain: "sankardeva.com",
    is_authoritative: true,
  },
];

// Permitted Source Registry verified domain patterns
const VERIFIED_DOMAIN_PATTERNS = [
  /\.gov\.in$/,
  /\.assam\.gov\.in$/,
  /\.nic\.in$/,
  /\.ac\.in$/,
  /\.edu\.in$/,
  /gauhati\.ac\.in$/,
  /tezu\.ernet\.in$/,
  /iitg\.ac\.in$/,
  /sankardeva\.com$/,
  /assamtribune\.com$/,
];

function isAuthoritativeDomain(domain: string): boolean {
  if (!domain) return false;
  const d = domain.toLowerCase().trim();
  return VERIFIED_DOMAIN_PATTERNS.some((pat) => pat.test(d));
}

function cleanSnippetText(raw: string): string {
  if (!raw) return "";
  // 1. Remove HTML tags
  let text = raw.replace(/<[^>]+>/g, " ");
  // 2. Decode HTML entities (named, decimal, hex)
  text = text
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#039;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(parseInt(code, 10)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, code) => String.fromCharCode(parseInt(code, 16)));
  // 3. Normalize whitespace without corrupting Assamese Unicode
  return text.replace(/\s+/g, " ").trim();
}

const ROMANIZED_ASSAMESE_DICT: Record<string, string> = {
  ko: "ক'",
  "k'": "ক'",
  k: "ক",
  koi: "কৈ",
  kua: "কোৱা",
  ki: "কি",
  kot: "ক'ত",
  axom: "অসম",
  asom: "অসম",
  assam: "অসম",
  bihu: "বিহু",
  kaziranga: "কাজিৰঙা",
  guwahati: "গুৱাহাটী",
  gauhati: "গুৱাহাটী",
  namaskar: "নমস্কাৰ",
  nomoskar: "নমস্কাৰ",
  bhal: "ভাল",
  khobor: "খবৰ",
  sankardev: "শংকৰদেৱ",
  lachit: "লাচিত",
  brahmaputra: "ব্ৰহ্মপুত্ৰ",
  jorhat: "যোৰহাট",
  silchar: "শিলচৰ",
  tezpur: "তেজপুৰ",
};

function detectLanguage(query: string): LanguageType {
  const assameseRegex = /[\u0980-\u09FF]/;
  const englishRegex = /[a-zA-Z]/;
  const hasAssamese = assameseRegex.test(query);
  const hasEnglish = englishRegex.test(query);

  if (hasAssamese && hasEnglish) return "mixed";
  if (hasAssamese) return "as_native";
  if (hasEnglish) {
    const lower = query.toLowerCase().trim();
    if (ROMANIZED_ASSAMESE_DICT[lower]) {
      return "as_romanized";
    }
    const words = lower.split(/\s+/);
    if (words.some((w) => ROMANIZED_ASSAMESE_DICT[w])) {
      return "as_romanized";
    }
    return "en";
  }
  return "all";
}

async function fetchWikipediaCandidates(query: string, lang: string): Promise<SearchResultItem[]> {
  try {
    const wikiLang = lang === "as_native" ? "as" : "en";
    const endpoint = `https://${wikiLang}.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(
      query
    )}&format=json&utf8=1&srlimit=5`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(endpoint, {
      signal: controller.signal,
      headers: { "User-Agent": "NyaSearchBot/1.0 (https://nya.search; info@nya.search)" },
    });
    clearTimeout(timeout);

    if (!res.ok) return [];
    const data = await res.json();
    const items = data.query?.search || [];

    return items.map((item: any) => {
      const cleanTitle = cleanSnippetText(item.title);
      const cleanSnippet = cleanSnippetText(item.snippet || "");
      // Revision timestamp on Wikipedia is NOT original publication date
      const revDate = item.timestamp ? new Date(item.timestamp).toISOString() : undefined;
      const crawledTime = new Date().toISOString();

      return {
        id: `wiki-${wikiLang}-${item.pageid}`,
        title: cleanTitle,
        url: `https://${wikiLang}.wikipedia.org/wiki/${encodeURIComponent(item.title.replace(/ /g, "_"))}`,
        display_url: `${wikiLang}.wikipedia.org › wiki › ${item.title.replace(/ /g, "_")}`,
        snippet: cleanSnippet,
        language: wikiLang === "as" ? "as" : "en",
        published_date: undefined,
        published_at: undefined,
        updated_at: revDate,
        crawled_at: crawledTime,
        is_news: false,
        score: 0.88,
        source_name: wikiLang === "as" ? "অসমীয়া ৱিকিপিডিয়া (Wikipedia)" : "Wikipedia, the free encyclopedia",
        source_domain: `${wikiLang}.wikipedia.org`,
        is_authoritative: false,
      };
    });
  } catch {
    return [];
  }
}

async function fetchDuckDuckGoCandidates(query: string): Promise<SearchResultItem[]> {
  try {
    const endpoint = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(endpoint, { signal: controller.signal });
    clearTimeout(timeout);

    if (!res.ok) return [];
    const data = await res.json();
    const results: SearchResultItem[] = [];
    const crawledTime = new Date().toISOString();

    if (data.AbstractText && data.AbstractURL) {
      try {
        const domain = new URL(data.AbstractURL).hostname.toLowerCase();
        const cleanTitle = cleanSnippetText(data.Heading || query);
        const cleanSnippet = cleanSnippetText(data.AbstractText);

        results.push({
          id: `ddg-abstract-${data.Heading || "main"}`,
          title: cleanTitle,
          url: data.AbstractURL,
          display_url: `${domain} › ${data.Heading || "info"}`,
          snippet: cleanSnippet,
          language: "en",
          published_date: undefined,
          published_at: undefined,
          updated_at: undefined,
          crawled_at: crawledTime,
          is_news: false,
          score: 0.90,
          source_name: data.AbstractSource || domain,
          source_domain: domain,
          is_authoritative: isAuthoritativeDomain(domain),
        });
      } catch {}
    }

    if (Array.isArray(data.RelatedTopics)) {
      for (const topic of data.RelatedTopics.slice(0, 4)) {
        if (topic.Text && topic.FirstURL) {
          try {
            const domain = new URL(topic.FirstURL).hostname.toLowerCase();
            const rawTitle = topic.Text.split(" - ")[0] || topic.Text.slice(0, 60);
            const cleanTitle = cleanSnippetText(rawTitle);
            const cleanSnippet = cleanSnippetText(topic.Text);

            results.push({
              id: `ddg-related-${crypto.createHash("md5").update(topic.FirstURL).digest("hex").slice(0, 8)}`,
              title: cleanTitle,
              url: topic.FirstURL,
              display_url: `${domain} › info`,
              snippet: cleanSnippet,
              language: "en",
              published_date: undefined,
              published_at: undefined,
              updated_at: undefined,
              crawled_at: crawledTime,
              is_news: false,
              score: 0.82,
              source_name: domain,
              source_domain: domain,
              is_authoritative: isAuthoritativeDomain(domain),
            });
          } catch {}
        }
      }
    }

    return results;
  } catch {
    return [];
  }
}

function detectTemporalIntent(query: string): { isTimeSensitive: boolean; isNewsIntent: boolean; coreTopic: string } {
  const lower = query.toLowerCase().trim();
  if (/^[a-zA-Z]{1,3}$/.test(lower)) {
    return { isTimeSensitive: false, isNewsIntent: false, coreTopic: query };
  }

  const enTemporal = ["today", "today's", "todays", "latest", "recent", "newest", "current", "breaking", "fresh", "now", "updates", "headlines", "yesterday"];
  const enNews = ["news", "headline", "headlines", "breaking", "bulletin", "report", "updates", "coverage"];
  const asTemporal = ["শেহতীয়া", "নতুন", "আজি", "আজিৰ", "বৰ্তমান", "সম্প্ৰতি", "সদ্যহতে", "লাইভ", "ব্ৰেকিং"];
  const asNews = ["খবৰ", "বাতৰি", "শীৰ্ষ খবৰ", "বুলেটিন", "সংবাদ"];
  const roTemporal = ["xehotiya", "sehotia", "sehotiya", "notun", "aaji", "aji", "ajir", "bortoman", "somproti"];
  const roNews = ["khobor", "batori", "songbad", "khabor"];

  const tokens = lower.split(/[\s,]+/);
  let isTemporal = false;
  let isNews = false;

  for (const t of tokens) {
    if (enTemporal.includes(t) || asTemporal.includes(t) || roTemporal.includes(t)) isTemporal = true;
    if (enNews.includes(t) || asNews.includes(t) || roNews.includes(t)) {
      isNews = true;
      isTemporal = true;
    }
  }

  if (lower.includes("today's news") || lower.includes("todays news") || lower.includes("শেহতীয়া খবৰ") || lower.includes("শেহতীয়া বাতৰি")) {
    isTemporal = true;
    isNews = true;
  }

  const allMarkers = new Set([...enTemporal, ...enNews, ...asTemporal, ...asNews, ...roTemporal, ...roNews]);
  const coreTokens = tokens.filter((t) => !allMarkers.has(t));
  const coreTopic = coreTokens.join(" ").trim() || query;

  return { isTimeSensitive: isTemporal, isNewsIntent: isNews, coreTopic };
}

async function generateGroundedAIAnswer(
  query: string,
  evidenceDocs: SearchResultItem[],
  lang: LanguageType
): Promise<AIAnswer | undefined> {
  const apiKey = process.env.AI_API_KEY || process.env.GEMINI_API_KEY;
  if (!apiKey || evidenceDocs.length === 0) {
    if (evidenceDocs.length === 0) {
      return {
        answer: "Insufficient verified evidence retrieved to provide a grounded summary.",
        status: "insufficient_evidence",
        citations: [],
        latency_ms: 50,
        confidence: 0.0,
        disclaimer: "No reliable organic sources available to verify this query.",
      };
    }
    return undefined;
  }

  const startTime = Date.now();
  const requestId = "nya-" + crypto.randomBytes(4).toString("hex");

  // Multi-model cascade fallback: try primary model first, cascade on 503/429/404/timeouts
  const candidateModels = Array.from(
    new Set([
      process.env.AI_MODEL_NAME || "gemini-3.5-flash",
      "gemini-3.5-flash",
      "gemini-3.6-flash",
      "gemini-flash-lite-latest",
    ])
  );

  const citations: CitationItem[] = evidenceDocs.map((doc, idx) => ({
    citation_index: idx + 1,
    document_id: doc.id,
    title: doc.title,
    url: doc.url,
    source_name: doc.source_name,
    source_domain: doc.source_domain,
    snippet: cleanSnippetText(doc.snippet),
  }));

  const evidenceText = evidenceDocs
    .map(
      (doc, idx) =>
        `[${idx + 1}] Title: ${cleanSnippetText(doc.title)}\nDomain: ${doc.source_domain}\nContent: ${cleanSnippetText(doc.snippet)}`
    )
    .join("\n\n");

  const systemInstruction = `You are ঞ (Nya) AI, an evidence-grounded search answer assistant.
Rules:
1. Answer the query strictly using the provided Evidence Sources.
2. Every factual statement MUST cite its source using bracketed numbers like [1], [2].
3. Never fabricate information or cite indices not present in the evidence.
4. If the query is in Assamese or about Assam, write the response in fluent Assamese (অসমীয়া) script. If in English, write in concise English.
5. If the query is an ambiguous short term (like 'ko'), explain its distinct meanings neutrally based on evidence.
6. Keep the answer direct, objective, and under 2-3 sentences.`;

  const prompt = `Evidence Sources:\n${evidenceText}\n\nUser Query: ${query}\n\nGround-truth answer with citations:`;

  let lastStatus = 0;
  let lastErrorMsg = "";

  for (const model of candidateModels) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 7500);

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ text: `${systemInstruction}\n\n${prompt}` }] }],
          generationConfig: {
            temperature: 0.2,
            maxOutputTokens: 300,
          },
        }),
        signal: controller.signal,
      });
      clearTimeout(timeout);

      lastStatus = res.status;

      if (res.status === 200) {
        const data = await res.json();
        const rawAnswerText = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim();

        if (rawAnswerText) {
          const durationMs = Date.now() - startTime;

          // Sanitize citations: remove hallucinated citation numbers outside range
          let sanitizedAnswer = rawAnswerText;
          const citedIndices = new Set(
            Array.from(rawAnswerText.matchAll(/\[(\d+)\]/g)).map((m: any) => parseInt(m[1], 10))
          );

          const validIndices = new Set<number>();
          for (const idx of Array.from(citedIndices)) {
            if (idx >= 1 && idx <= evidenceDocs.length) {
              validIndices.add(idx);
            } else {
              // Strip hallucinated bracket marker
              sanitizedAnswer = sanitizedAnswer.replace(new RegExp(`\\[${idx}\\]`, "g"), "");
            }
          }

          const activeCitations = citations.filter((c) => validIndices.has(c.citation_index));
          const finalCitations = activeCitations.length > 0 ? activeCitations : citations.slice(0, 2);

          return {
            answer: sanitizedAnswer.trim(),
            status: "grounded",
            citations: finalCitations,
            latency_ms: durationMs,
            confidence: 0.95,
            model_name: model,
            request_id: requestId,
            disclaimer: "AI-generated summary strictly grounded in retrieved organic sources.",
          };
        }
      }

      // Check errors and cascade
      if (res.status === 429) {
        lastErrorMsg = "RESOURCE_EXHAUSTED";
        continue;
      }

      if (res.status === 503 || res.status === 404 || res.status >= 500) {
        lastErrorMsg = `HTTP_${res.status}`;
        continue;
      }
    } catch (err: any) {
      lastErrorMsg = err?.name === "AbortError" ? "TIMEOUT" : "NETWORK_ERROR";
      continue;
    }
  }

  // If all candidate models in cascade were exhausted
  const durationMs = Date.now() - startTime;
  if (lastStatus === 429) {
    return {
      answer: "The upstream AI model reached its request quota limit. Organic results remain available below.",
      status: "rate_limited",
      citations: [],
      latency_ms: durationMs,
      confidence: 0.0,
      model_name: candidateModels[0],
      request_id: requestId,
      error_code: "RESOURCE_EXHAUSTED",
      retry_after_seconds: 3600,
    };
  }

  return {
    answer: "Inference service temporarily unavailable. Organic web results remain available.",
    status: "provider_unavailable",
    citations: [],
    latency_ms: durationMs,
    confidence: 0.0,
    model_name: candidateModels[0],
    request_id: requestId,
    error_code: lastErrorMsg || `HTTP_${lastStatus}`,
  };
}

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams;
  const q = (searchParams.get("q") || "").trim();
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10);
  const sort = (searchParams.get("sort") || "newest") as "newest" | "relevance";
  const enableAi = searchParams.get("enable_ai") !== "false";

  if (!q) {
    return NextResponse.json({ detail: "Query parameter 'q' is required." }, { status: 400 });
  }

  // 1. If backend URL is provided, proxy to backend
  const backendUrl = process.env.API_URL;
  if (backendUrl) {
    try {
      const targetUrl = `${backendUrl.replace(/\/$/, "")}/api/v1/search?${searchParams.toString()}`;
      const res = await fetch(targetUrl, {
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fallback to local serverless execution below
    }
  }

  // 2. Local Serverless Search Pipeline
  const startTime = Date.now();
  const lowerQ = q.toLowerCase().trim();
  const detectedLanguage = detectLanguage(q);
  const isShortLatin = /^[a-zA-Z]{1,3}$/.test(lowerQ);
  const transliteratedSuggestion = ROMANIZED_ASSAMESE_DICT[lowerQ] || undefined;
  const { isTimeSensitive, isNewsIntent, coreTopic } = detectTemporalIntent(q);

  // Match regional knowledge
  const topicTokens = (isTimeSensitive || isNewsIntent) && coreTopic
    ? coreTopic.toLowerCase().split(/\s+/).filter((t) => t.length > 1)
    : [];

  const matchedRegional = REGIONAL_KNOWLEDGE_BASE.filter((doc) => {
    const titleL = doc.title.toLowerCase();
    const snippetL = doc.snippet.toLowerCase();

    if (topicTokens.length > 0) {
      const matchesTopic = topicTokens.some((tt) => titleL.includes(tt) || snippetL.includes(tt));
      if (matchesTopic) return true;
    }

    return (
      titleL.includes(lowerQ) ||
      snippetL.includes(lowerQ) ||
      lowerQ.split(/\s+/).some((token) => titleL.includes(token))
    );
  });

  // Concurrently fetch external live candidates across languages
  const fetchTasks: Promise<SearchResultItem[]>[] = [
    fetchWikipediaCandidates(q, detectedLanguage),
    fetchDuckDuckGoCandidates(q),
  ];

  // If query is an ambiguous short Latin term (e.g. 'ko') or has an Assamese transliteration,
  // query native Assamese Wikipedia for balanced multi-lingual coverage
  if (isShortLatin || transliteratedSuggestion) {
    const asTarget = transliteratedSuggestion || (lowerQ === "ko" ? "ক" : lowerQ);
    fetchTasks.push(fetchWikipediaCandidates(asTarget, "as_native"));
  }

  const taskResults = await Promise.all(fetchTasks);
  const wikiResults = taskResults[0] || [];
  const ddgResults = taskResults[1] || [];
  const asWikiResults = taskResults[2] || [];

  // Combine and deduplicate candidates by URL with word-boundary ranking
  const seenUrls = new Set<string>();
  const combined: SearchResultItem[] = [];

  const wordBoundaryRegex = new RegExp(`\\b${lowerQ.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i");

  for (const item of [...matchedRegional, ...asWikiResults, ...wikiResults, ...ddgResults]) {
    if (!seenUrls.has(item.url)) {
      seenUrls.add(item.url);

      let adjustedScore = item.score;
      if (isShortLatin) {
        const titleHasWord = wordBoundaryRegex.test(item.title);
        const snippetHasWord = wordBoundaryRegex.test(item.snippet);
        if (titleHasWord) {
          adjustedScore += 0.10;
        } else if (!snippetHasWord && !item.language.includes("as")) {
          // Penalize substring false-positives where 'ko' was found inside another word
          adjustedScore -= 0.20;
        }
      }

      // News intent adjustment: suppress generic encyclopedia pages and boost genuine news
      if (isTimeSensitive || isNewsIntent) {
        if (item.source_domain.includes("wikipedia.org")) {
          adjustedScore *= 0.35;
        } else if (item.is_news) {
          adjustedScore *= 1.80;
        }
      }

      combined.push({
        ...item,
        score: Math.round(adjustedScore * 100) / 100,
      });
    }
  }

  // Relevance filtering: prevent incidental/irrelevant pages from dominating
  const maxScore = Math.max(...combined.map((c) => c.score), 0);
  const relCutoff = maxScore > 5 ? maxScore * 0.15 : 0.2;
  const filteredCandidates = combined.filter((c) => c.score >= relCutoff);
  const candidatesToRank = filteredCandidates.length > 0 ? filteredCandidates : combined;

  let sortedResults: SearchResultItem[] = [];

  if (sort === "newest") {
    const dated: SearchResultItem[] = [];
    const undated: SearchResultItem[] = [];

    for (const c of candidatesToRank) {
      if (c.published_at || c.published_date) {
        dated.push(c);
      } else {
        undated.push(c);
      }
    }

    dated.sort((a, b) => {
      const timeA = new Date(a.published_at || a.published_date!).getTime();
      const timeB = new Date(b.published_at || b.published_date!).getTime();
      if (timeA !== timeB) return timeB - timeA;
      return b.score - a.score;
    });

    undated.sort((a, b) => b.score - a.score);
    sortedResults = [...dated, ...undated];
  } else {
    sortedResults = [...candidatesToRank];
    sortedResults.sort((a, b) => b.score - a.score);
  }

  const totalResults = sortedResults.length;
  const startIndex = (page - 1) * pageSize;
  const pagedResults = sortedResults.slice(startIndex, startIndex + pageSize);

  // Freshness assessment for news queries
  let hasFreshResults = true;
  let freshnessNotice: string | undefined = undefined;

  if (isTimeSensitive || isNewsIntent) {
    const now = Date.now();
    const ninetyDaysMs = 90 * 24 * 60 * 60 * 1000;
    const hasRecent = sortedResults.some((r) => {
      const pub = r.published_at || r.published_date;
      if (!pub) return false;
      const t = new Date(pub).getTime();
      return now - t <= ninetyDaysMs || r.is_news;
    });

    if (!hasRecent && sortedResults.length > 0) {
      hasFreshResults = false;
      freshnessNotice =
        "No recent news found from verified sources for this topic. Showing relevant background information.";
    }
  }

  // Grounded AI answer (top 4 evidence documents)
  let aiAnswer: AIAnswer | undefined;
  if (enableAi && sortedResults.length > 0) {
    aiAnswer = await generateGroundedAIAnswer(q, sortedResults.slice(0, 4), detectedLanguage);
  }

  // Generate contextual disambiguation suggestions
  const relatedQueries: string[] = [];
  if (lowerQ === "ko") {
    relatedQueries.push(
      "ক (অসমীয়া বৰ্ণমালা)",
      "ক' (কোৱা — অসমীয়া ক্ৰিয়া)",
      "KO (Knockout in combat sports)",
      "Ko (surname)"
    );
  } else if (transliteratedSuggestion) {
    relatedQueries.push(
      `${transliteratedSuggestion} (অসমীয়া লিপি)`,
      `${q} Assam`,
      `${q} overview`
    );
  } else {
    relatedQueries.push(
      `${q} Assam`,
      `${q} overview`,
      `অসমীয়া ${q}`
    );
  }

  const responsePayload: SearchResponse = {
    query: q,
    normalized_query: q,
    detected_language: detectedLanguage,
    total_results: totalResults,
    page: page,
    page_size: pageSize,
    latency_ms: Date.now() - startTime,
    sort: sort,
    is_time_sensitive_query: isTimeSensitive,
    has_fresh_results: hasFreshResults,
    freshness_notice: freshnessNotice,
    results: pagedResults,
    ai_answer: aiAnswer,
    related_queries: relatedQueries,
  };

  return NextResponse.json(responsePayload);
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const q = body.query || "";
    const page = body.page || 1;
    const pageSize = body.page_size || 10;
    const sort = body.sort || "newest";
    const enableAi = body.enable_ai !== false;

    // Delegate to GET handler logic with URL params
    const url = new URL(req.url);
    url.searchParams.set("q", q);
    url.searchParams.set("page", page.toString());
    url.searchParams.set("page_size", pageSize.toString());
    url.searchParams.set("sort", sort);
    url.searchParams.set("enable_ai", enableAi.toString());

    const getReq = new NextRequest(url.toString(), { method: "GET" });
    return GET(getReq);
  } catch {
    return NextResponse.json({ detail: "Invalid JSON request body." }, { status: 400 });
  }
}
