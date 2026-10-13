"""
DuckDuckGo Web Search Provider for ঞ (Nya) Search.
Retrieves live open web results with privacy-conscious zero user tracking.
"""

import httpx
import re
import html
import hashlib
from urllib.parse import urlparse, parse_qs, unquote
from typing import List, Dict, Any
from datetime import datetime, timezone
from search.providers.base import BaseSearchProvider


class DuckDuckGoProvider(BaseSearchProvider):
    @property
    def provider_name(self) -> str:
        return "duckduckgo"

    def __init__(self, timeout_seconds: float = 4.5):
        self.timeout = timeout_seconds
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,as;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.item_pattern = re.compile(
            r"<a\s+[^>]*?href=['\"]([^'\"]+)['\"][^>]*?class=['\"]result-link['\"][^>]*>(.*?)</a>.*?"
            r"<td\s+class=['\"]result-snippet['\"][^>]*>(.*?)</td>",
            re.DOTALL
        )
        # Authoritative domains strictly aligned with Permitted Source Registry
        self.authoritative_suffixes = (
            ".gov.in", ".assam.gov.in", ".nic.in", ".ac.in", ".edu.in", ".ernet.in"
        )
        self.authoritative_domains = {
            "assam.gov.in", "assamtribune.com", "gauhati.ac.in", "tezu.ernet.in",
            "iitg.ac.in", "sankardeva.com", "kalakshetra.assam.gov.in", "dheassam.gov.in",
        }

    def _clean_url(self, raw_url: str) -> str:
        """Unwrap DuckDuckGo redirect URLs if present."""
        if "uddg=" in raw_url:
            parsed = urlparse(raw_url)
            qs = parse_qs(parsed.query)
            if "uddg" in qs and qs["uddg"]:
                return unquote(qs["uddg"][0])
        if raw_url.startswith("//"):
            return "https:" + raw_url
        return raw_url

    def _is_authoritative(self, domain: str) -> bool:
        domain_lower = domain.lower()
        if any(domain_lower.endswith(sfx) for sfx in self.authoritative_suffixes):
            return True
        for auth in self.authoritative_domains:
            if auth in domain_lower:
                return True
        return False

    async def search(
        self,
        query: str,
        detected_language: str,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        offset = max(0, (page - 1) * page_size)

        payload = {"q": query}
        if offset > 0:
            payload["s"] = str(offset)
            payload["dc"] = str(offset + 1)

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.post("https://lite.duckduckgo.com/lite/", data=payload)
                if resp.status_code != 200:
                    return []

                matches = self.item_pattern.findall(resp.text)
                for raw_link, raw_title, raw_snippet in matches:
                    clean_url = self._clean_url(raw_link)
                    clean_title = html.unescape(re.sub(r"<[^>]+>", "", raw_title)).strip()
                    clean_snippet = html.unescape(re.sub(r"<[^>]+>", "", raw_snippet)).strip()

                    if not clean_title or not clean_url:
                        continue

                    parsed_domain = urlparse(clean_url).netloc.lower()
                    if parsed_domain.startswith("www."):
                        parsed_domain = parsed_domain[4:]

                    # Ignore self-referential DDG links or internal navigations
                    if "duckduckgo.com" in parsed_domain:
                        continue

                    # Determine publisher display name
                    source_name = parsed_domain.split(".")[0].capitalize()
                    if "pratidintime" in parsed_domain:
                        source_name = "Pratidin Time"
                    elif "assamtribune" in parsed_domain:
                        source_name = "The Assam Tribune"
                    elif "timesofindia" in parsed_domain:
                        source_name = "Times of India"
                    elif "thehindu" in parsed_domain:
                        source_name = "The Hindu"
                    elif "wikipedia" in parsed_domain:
                        source_name = "Wikipedia"

                    content_hash = hashlib.sha256(f"{clean_url}:{clean_title}".encode("utf-8")).hexdigest()
                    doc_id = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:16]

                    # Detect doc language
                    doc_lang = "en"
                    if any(ord(c) >= 0x0980 and ord(c) <= 0x09FF for c in clean_title + clean_snippet):
                        doc_lang = "as"

                    results.append({
                        "id": f"web_{doc_id}",
                        "url": clean_url,
                        "canonical_url": clean_url,
                        "title": clean_title,
                        "body_text": f"{clean_title}. {clean_snippet}",
                        "snippet": clean_snippet,
                        "language": doc_lang,
                        "content_hash": content_hash,
                        "published_date": None,
                        "source_name": source_name,
                        "source_domain": parsed_domain,
                        "is_authoritative": self._is_authoritative(parsed_domain),
                    })

                    if len(results) >= page_size:
                        break

        except Exception:
            # DuckDuckGo network failure or timeout; return empty list gracefully
            return []

        return results
