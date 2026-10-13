"""
Wikipedia Search Provider for ঞ (Nya) Search.
Queries Assamese (as.wikipedia.org) and English (en.wikipedia.org) MediaWiki APIs
for open, lawful encyclopedic knowledge.
"""

import httpx
import re
import html
import hashlib
from typing import List, Dict, Any
from urllib.parse import quote
from datetime import datetime, timezone
from search.providers.base import BaseSearchProvider


class WikipediaProvider(BaseSearchProvider):
    @property
    def provider_name(self) -> str:
        return "wikipedia"

    def __init__(self, timeout_seconds: float = 4.0):
        self.timeout = timeout_seconds
        self.headers = {
            "User-Agent": "NyaSearchEngine/1.0 (Regional Assamese-first search engine; contact: admin@nya-search.local)",
            "Accept": "application/json",
        }

    async def search(
        self,
        query: str,
        detected_language: str,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        offset = max(0, (page - 1) * page_size)

        # Decide languages to query based on detected script
        langs_to_query = []
        if detected_language == "as_native":
            langs_to_query = ["as", "en"]
        elif detected_language in ("as_romanized", "mixed"):
            langs_to_query = ["as", "en"]
        else:
            langs_to_query = ["en", "as"]

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            for lang in langs_to_query:
                try:
                    search_query = query
                    if lang == "as" and not any(0x0980 <= ord(c) <= 0x09FF for c in query):
                        # Transliterate Latin romanized query to Assamese script if possible
                        from nlp.transliteration import ROMANIZED_DICTIONARY
                        lower_q = query.lower().strip()
                        if lower_q in ROMANIZED_DICTIONARY:
                            search_query = ROMANIZED_DICTIONARY[lower_q]

                    url = f"https://{lang}.wikipedia.org/w/api.php"
                    params = {
                        "action": "query",
                        "list": "search",
                        "srsearch": search_query,
                        "format": "json",
                        "utf8": "1",
                        "sroffset": offset,
                        "srlimit": min(page_size, 10),
                    }
                    resp = await client.get(url, params=params)
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    search_items = data.get("query", {}).get("search", [])

                    for item in search_items:
                        title = html.unescape(item.get("title", "")).strip()
                        raw_snippet = item.get("snippet", "")
                        clean_snippet = html.unescape(re.sub(r"<[^>]+>", " ", raw_snippet)).strip()
                        clean_snippet = re.sub(r"\s+", " ", clean_snippet)
                        page_id = item.get("pageid", 0)

                        if not title:
                            continue

                        canonical_url = f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                        content_hash = hashlib.sha256(f"{title}:{clean_snippet}".encode("utf-8")).hexdigest()

                        # Wikipedia returns revision timestamps of edits, NOT original news publication dates
                        raw_ts = item.get("timestamp")
                        rev_date = None
                        if raw_ts:
                            try:
                                rev_date = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                            except Exception:
                                rev_date = None

                        crawled_time = datetime.now(timezone.utc)

                        results.append({
                            "id": f"wiki_{lang}_{page_id}",
                            "url": canonical_url,
                            "canonical_url": canonical_url,
                            "title": title,
                            "body_text": f"{title}. {clean_snippet}",
                            "snippet": clean_snippet,
                            "language": lang,
                            "content_hash": content_hash,
                            "published_date": None,
                            "published_at": None,
                            "updated_at": rev_date,
                            "crawled_at": crawled_time,
                            "is_news": False,
                            "source_name": "অসমীয়া ৱিকিপিডিয়া" if lang == "as" else "Wikipedia (English)",
                            "source_domain": f"{lang}.wikipedia.org",
                            "is_authoritative": False,
                        })

                except Exception:
                    # Wikipedia query failed or timed out; continue gracefully
                    continue

        return results
