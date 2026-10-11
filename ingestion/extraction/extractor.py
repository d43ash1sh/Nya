"""
HTML Content and Metadata Extractor.
Extracts title, meta description, clean textual body, canonical URL,
and generates contextual search snippets.
"""

from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional


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

        # 4. Extract meta description
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        # 5. Extract body text
        text = soup.get_text(separator=" ", strip=True)
        # Normalize whitespace
        clean_body = re.sub(r"\s+", " ", text).strip()

        # 6. Generate snippet
        snippet = meta_desc if meta_desc else clean_body[:240] + ("..." if len(clean_body) > 240 else "")

        return {
            "title": title[:500],
            "body_text": clean_body,
            "snippet": snippet[:400],
            "canonical_url": canonical_url,
        }
