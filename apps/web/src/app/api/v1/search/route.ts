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
    id: "kaziranga-national-park",
    title: "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান আৰু এশিঙীয়া গঁড় (Kaziranga National Park & One-Horned Rhino)",
    url: "https://forest.assam.gov.in/portlet-innerpage/kaziranga-national-park",
    display_url: "forest.assam.gov.in › kaziranga-national-park",
    snippet:
      "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান বিশ্ব ঐতিহ্য ক্ষেত্ৰ আৰু ই পৃথিৱীৰ বিখ্যাত এশিঙীয়া গঁড়ৰ প্ৰধান আৱাসভূমি। এই উদ্যানখন গোলাঘাট আৰু নগাঁও জিলাত অৱস্থিত।",
    language: "as",
    published_date: "2024-01-15",
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
    published_date: "2024-04-14",
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
    published_date: "2024-02-01",
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
    published_date: "2024-03-10",
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
    published_date: "2024-01-20",
    score: 0.92,
    source_name: "Sankardeva Research Foundation",
    source_domain: "sankardeva.com",
    is_authoritative: true,
  },
];

function detectLanguage(query: string): LanguageType {
  const assameseRegex = /[\u0980-\u09FF]/;
  const englishRegex = /[a-zA-Z]/;
  const hasAssamese = assameseRegex.test(query);
  const hasEnglish = englishRegex.test(query);

  if (hasAssamese && hasEnglish) return "mixed";
  if (hasAssamese) return "as_native";
  if (hasEnglish) {
    const lower = query.toLowerCase();
    const assamPhonetic = [
      "axom", "asom", "bihu", "kaziranga", "guwahati", "gauhati", "namaskar",
      "bhal", "khobor", "sankardev", "lachit", "brahmaputra", "jorhat", "silchar"
    ];
    if (assamPhonetic.some((term) => lower.includes(term))) {
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

    return items.map((item: any) => ({
      id: `wiki-${item.pageid}`,
      title: item.title,
      url: `https://${wikiLang}.wikipedia.org/wiki/${encodeURIComponent(item.title.replace(/ /g, "_"))}`,
      display_url: `${wikiLang}.wikipedia.org › wiki › ${item.title.replace(/ /g, "_")}`,
      snippet: item.snippet ? item.snippet.replace(/<[^>]+>/g, "") : "",
      language: wikiLang === "as" ? "as" : "en",
      published_date: new Date().toISOString().split("T")[0],
      score: 0.88,
      source_name: wikiLang === "as" ? "অসমীয়া ৱিকিপিডিয়া (Wikipedia)" : "Wikipedia, the free encyclopedia",
      source_domain: `${wikiLang}.wikipedia.org`,
      is_authoritative: true,
    }));
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

    if (data.AbstractText && data.AbstractURL) {
      try {
        const domain = new URL(data.AbstractURL).hostname;
        results.push({
          id: `ddg-abstract-${data.Heading || "main"}`,
          title: data.Heading || query,
          url: data.AbstractURL,
          display_url: `${domain} › ${data.Heading || "info"}`,
          snippet: data.AbstractText,
          language: "en",
          score: 0.90,
          source_name: data.AbstractSource || domain,
          source_domain: domain,
          is_authoritative: true,
        });
      } catch {}
    }

    if (Array.isArray(data.RelatedTopics)) {
      for (const topic of data.RelatedTopics.slice(0, 4)) {
        if (topic.Text && topic.FirstURL) {
          try {
            const domain = new URL(topic.FirstURL).hostname;
            results.push({
              id: `ddg-related-${crypto.createHash("md5").update(topic.FirstURL).digest("hex").slice(0, 8)}`,
              title: topic.Text.split(" - ")[0] || topic.Text.slice(0, 60),
              url: topic.FirstURL,
              display_url: `${domain} › info`,
              snippet: topic.Text,
              language: "en",
              score: 0.82,
              source_name: domain,
              source_domain: domain,
              is_authoritative: false,
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
  const modelName = process.env.AI_MODEL_NAME || "gemini-flash-lite-latest";

  const citations: CitationItem[] = evidenceDocs.map((doc, idx) => ({
    citation_index: idx + 1,
    document_id: doc.id,
    title: doc.title,
    url: doc.url,
    source_name: doc.source_name,
    source_domain: doc.source_domain,
    snippet: doc.snippet,
  }));

  const evidenceText = evidenceDocs
    .map(
      (doc, idx) =>
        `[${idx + 1}] Title: ${doc.title}\nDomain: ${doc.source_domain}\nContent: ${doc.snippet}`
    )
    .join("\n\n");

  const systemInstruction = `You are ঞ (Nya) AI, an evidence-grounded search answer assistant.
Rules:
1. Answer the query strictly using the provided Evidence Sources.
2. Every factual statement MUST cite its source using bracketed numbers like [1], [2].
3. Never fabricate information or cite indices not present in the evidence.
4. If the query is in Assamese or about Assam, write the response in fluent Assamese (অসমীয়া) script. If in English, write in concise English.
5. Keep the answer direct, objective, and under 3-4 sentences.`;

  const prompt = `Evidence Sources:\n${evidenceText}\n\nUser Query: ${query}\n\nGround-truth answer with citations:`;

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: `${systemInstruction}\n\n${prompt}` }] }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 500,
        },
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    const durationMs = Date.now() - startTime;

    if (res.status === 429) {
      return {
        answer: "The upstream AI model reached its request quota limit. Organic results remain available below.",
        status: "rate_limited",
        citations: [],
        latency_ms: durationMs,
        confidence: 0.0,
        model_name: modelName,
        request_id: requestId,
        error_code: "RESOURCE_EXHAUSTED",
        retry_after_seconds: 3600,
      };
    }

    if (!res.ok) {
      return {
        answer: "Inference service temporarily unavailable. Organic web results remain available.",
        status: "provider_unavailable",
        citations: [],
        latency_ms: durationMs,
        confidence: 0.0,
        model_name: modelName,
        request_id: requestId,
        error_code: `HTTP_${res.status}`,
      };
    }

    const data = await res.json();
    const answerText = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim();

    if (!answerText) {
      return {
        answer: "No answer could be generated from available evidence.",
        status: "insufficient_evidence",
        citations: [],
        latency_ms: durationMs,
        confidence: 0.0,
        model_name: modelName,
        request_id: requestId,
      };
    }

    // Filter citations to only those actually cited in the generated answer
    const citedIndices = new Set(
      Array.from(answerText.matchAll(/\[(\d+)\]/g)).map((m: any) => parseInt(m[1], 10))
    );
    const activeCitations = citations.filter((c) => citedIndices.has(c.citation_index));

    return {
      answer: answerText,
      status: "grounded",
      citations: activeCitations.length > 0 ? activeCitations : citations.slice(0, 2),
      latency_ms: durationMs,
      confidence: 0.95,
      model_name: modelName,
      request_id: requestId,
      disclaimer: "AI-generated summary strictly grounded in retrieved organic sources.",
    };
  } catch (err: any) {
    const durationMs = Date.now() - startTime;
    const isTimeout = err?.name === "AbortError";
    return {
      answer: isTimeout ? "AI inference timed out." : "AI service error.",
      status: isTimeout ? "timeout" : "provider_unavailable",
      citations: [],
      latency_ms: durationMs,
      confidence: 0.0,
      model_name: modelName,
      request_id: requestId,
      error_code: isTimeout ? "TIMEOUT" : "EXCEPTION",
    };
  }
}

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams;
  const q = (searchParams.get("q") || "").trim();
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10);
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
  const detectedLanguage = detectLanguage(q);

  // Match regional knowledge
  const lowerQ = q.toLowerCase();
  const matchedRegional = REGIONAL_KNOWLEDGE_BASE.filter(
    (doc) =>
      doc.title.toLowerCase().includes(lowerQ) ||
      doc.snippet.toLowerCase().includes(lowerQ) ||
      lowerQ.split(/\s+/).some((token) => doc.title.toLowerCase().includes(token))
  );

  // Concurrently fetch external live candidates
  const [wikiResults, ddgResults] = await Promise.all([
    fetchWikipediaCandidates(q, detectedLanguage),
    fetchDuckDuckGoCandidates(q),
  ]);

  // Combine and deduplicate candidates by URL
  const seenUrls = new Set<string>();
  const combined: SearchResultItem[] = [];

  for (const item of [...matchedRegional, ...wikiResults, ...ddgResults]) {
    if (!seenUrls.has(item.url)) {
      seenUrls.add(item.url);
      combined.push(item);
    }
  }

  const totalResults = combined.length;
  const startIndex = (page - 1) * pageSize;
  const pagedResults = combined.slice(startIndex, startIndex + pageSize);

  // Grounded AI answer (top 4 evidence documents)
  let aiAnswer: AIAnswer | undefined;
  if (enableAi && combined.length > 0) {
    aiAnswer = await generateGroundedAIAnswer(q, combined.slice(0, 4), detectedLanguage);
  }

  const responsePayload: SearchResponse = {
    query: q,
    normalized_query: q,
    detected_language: detectedLanguage,
    total_results: totalResults,
    page: page,
    page_size: pageSize,
    latency_ms: Date.now() - startTime,
    results: pagedResults,
    ai_answer: aiAnswer,
    related_queries: [
      `${q} Assam`,
      `${q} overview`,
      `অসমীয়া ${q}`,
    ],
  };

  return NextResponse.json(responsePayload);
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const q = body.query || "";
    const page = body.page || 1;
    const pageSize = body.page_size || 10;
    const enableAi = body.enable_ai !== false;

    // Delegate to GET handler logic with URL params
    const url = new URL(req.url);
    url.searchParams.set("q", q);
    url.searchParams.set("page", page.toString());
    url.searchParams.set("page_size", pageSize.toString());
    url.searchParams.set("enable_ai", enableAi.toString());

    const getReq = new NextRequest(url.toString(), { method: "GET" });
    return GET(getReq);
  } catch {
    return NextResponse.json({ detail: "Invalid JSON request body." }, { status: 400 });
  }
}
