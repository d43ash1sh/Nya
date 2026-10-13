"""
HTML Content and Metadata Extractor.
Extracts title, meta description, clean textual body, canonical URL,
and generates contextual search snippets.
"""

from bs4 import BeautifulSoup
import re
import html
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class ContentExtractor:
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse HTML document and extract clean search metadata."""
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Strip script, style, navigation, header, footer elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
            element.decompose()

        # 2. Extract canonical URL
        canonical_tag = soup.find("link", rel=lambda val: val and "canonical" in val.lower())
        canonical_url = canonical_tag["href"].strip() if canonical_tag and canonical_tag.get("href") else url

        # 3. Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.h1:
            title = soup.h1.get_text().strip()
        else:
            title = url
        clean_title = html.unescape(title).strip()

        # 4. Extract meta description
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if desc_tag and desc_tag.get("content"):
            meta_desc = html.unescape(desc_tag["content"]).strip()

        # 5. Extract body text and normalize whitespace
        text = soup.get_text(separator=" ", strip=True)
        clean_body = html.unescape(re.sub(r"\s+", " ", text)).strip()

        # 6. Generate snippet
        snippet_raw = meta_desc if meta_desc else clean_body[:240] + ("..." if len(clean_body) > 240 else "")
        clean_snippet = html.unescape(snippet_raw).strip()

        # 7. Extract genuine publication date and update date from meta tags if present
        published_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
        crawled_at: datetime = datetime.now(timezone.utc) if "timezone" in globals() else datetime.utcnow()

        pub_meta = soup.find(
            "meta",
            attrs={
                "property": re.compile(r"article:published_time|og:published_time", re.I)
            },
        ) or soup.find(
            "meta",
            attrs={"name": re.compile(r"^(pubdate|publishdate|date|dc\.date|datePublished)$", re.I)},
        )

        if pub_meta and pub_meta.get("content"):
            raw_date = pub_meta["content"].strip()
            try:
                published_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            except Exception:
                published_at = None

        upd_meta = soup.find(
            "meta",
            attrs={
                "property": re.compile(r"article:modified_time|og:updated_time", re.I)
            },
        ) or soup.find(
            "meta",
            attrs={"name": re.compile(r"^(last-modified|datemodified|revision_date)$", re.I)},
        )

        if upd_meta and upd_meta.get("content"):
            raw_upd = upd_meta["content"].strip()
            try:
                updated_at = datetime.fromisoformat(raw_upd.replace("Z", "+00:00"))
            except Exception:
                updated_at = None

        return {
            "title": clean_title[:500],
            "body_text": clean_body,
            "snippet": clean_snippet[:400],
            "canonical_url": canonical_url,
            "published_at": published_at,
            "updated_at": updated_at,
            "crawled_at": crawled_at,
            "published_date": published_at,
        }
