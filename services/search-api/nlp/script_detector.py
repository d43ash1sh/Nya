"""
Script and Language Detector for ঞ (Nya) Search.
Categorizes queries into:
- as_native (Assamese script)
- as_romanized (Latin script with Assamese vocabulary)
- en (English)
- mixed (Combination of Assamese and Latin)
"""

import re
from typing import Tuple
from nlp.assamese_normalizer import ASSAMESE_UNICODE_RANGE
from nlp.transliteration import ROMANIZED_DICTIONARY


class ScriptDetector:
    """Detects script and language characteristics of search queries."""

    def __init__(self):
        self.assamese_re = ASSAMESE_UNICODE_RANGE
        self.latin_re = re.compile(r"[a-zA-Z]")

    def detect(self, query: str) -> str:
        """
        Returns one of: 'as_native', 'as_romanized', 'en', 'mixed'.
        """
        if not query or not query.strip():
            return "en"

        has_assamese = bool(self.assamese_re.search(query))
        has_latin = bool(self.latin_re.search(query))

        if has_assamese and has_latin:
            return "mixed"

        if has_assamese:
            return "as_native"

        # If it's Latin, check whether it matches Romanized Assamese vocabulary
        words = [w.lower().strip() for w in re.findall(r"\w+", query)]
        if not words:
            return "en"

        assamese_matches = sum(1 for w in words if w in ROMANIZED_DICTIONARY)
        if assamese_matches > 0:
            return "as_romanized"

        return "en"

    def analyze_query_composition(self, query: str) -> dict:
        """Detailed breakdown of script characteristics."""
        total_chars = len(query.strip())
        if total_chars == 0:
            return {"primary": "en", "assamese_ratio": 0.0, "latin_ratio": 0.0}

        assamese_count = len(self.assamese_re.findall(query))
        latin_count = len(self.latin_re.findall(query))

        return {
            "primary": self.detect(query),
            "assamese_chars": assamese_count,
            "latin_chars": latin_count,
            "assamese_ratio": assamese_count / total_chars,
            "latin_ratio": latin_count / total_chars,
        }
