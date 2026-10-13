"""
Temporal and News Intent Classifier for ঞ (Nya) Search.
Detects time-sensitive and news-oriented search intent across:
- English
- Native Assamese (অসমীয়া)
- Romanized Assamese (Latin transliteration)
- Mixed language queries

Guards against misclassifying short ambiguous terms (e.g. 'ko', 'ba', 'ki')
or general educational/encyclopedic inquiries.
"""

import re
import unicodedata
from typing import Dict, Any, List, Set, Optional


class TemporalClassifier:
    def __init__(self):
        # 1. English temporal and news patterns (using word boundaries)
        self.en_temporal_words = {
            "today", "todays", "today's", "latest", "recent", "newest",
            "current", "breaking", "fresh", "now", "updates", "headlines",
            "yesterday", "tonight"
        }
        self.en_news_words = {
            "news", "headline", "headlines", "breaking", "bulletin",
            "report", "updates", "coverage"
        }

        # 2. Native Assamese temporal and news patterns
        self.as_temporal_words = {
            unicodedata.normalize("NFC", w) for w in {
                "শেহতীয়া", "নতুন", "আজি", "আজিৰ", "বৰ্তমান",
                "সম্প্ৰতি", "সদ্যহতে", "লাইভ", "ব্ৰেকিং", "কালি", "কালিৰ"
            }
        }
        self.as_news_words = {
            unicodedata.normalize("NFC", w) for w in {
                "খবৰ", "বাতৰি", "শীৰ্ষ খবৰ", "বুলেটিন", "সংবাদ", "শীৰ্ষ বাতৰি"
            }
        }

        # 3. Romanized Assamese temporal and news patterns
        self.romanized_temporal_words = {
            "xehotiya", "sehotia", "sehotiya", "notun", "aaji",
            "aji", "ajir", "bortoman", "somproti", "sodyohote"
        }
        self.romanized_news_words = {
            "khobor", "batori", "songbad", "khabor", "batori-khobor"
        }

        # Guard patterns for ambiguous short queries
        self.ambiguous_short_terms = {"ko", "k'", "k", "ba", "ki", "kot", "kua", "koi"}

    def is_ambiguous_short_query(self, query: str) -> bool:
        """Determines if query is an ambiguous short token that must not trigger news heuristics."""
        cleaned = query.strip().lower()
        return cleaned in self.ambiguous_short_terms or (len(cleaned) <= 3 and bool(re.match(r"^[a-zA-Z]{1,3}$", cleaned)))

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Analyzes search query for freshness urgency and news intent.
        Returns:
            - is_time_sensitive: bool
            - is_news_intent: bool
            - detected_markers: List[str]
            - core_topic: str
        """
        raw = unicodedata.normalize("NFC", query.strip())
        lower = raw.lower()

        # Guard: Short ambiguous queries are never news
        if not raw or self.is_ambiguous_short_query(raw):
            return {
                "is_time_sensitive": False,
                "is_news_intent": False,
                "detected_markers": [],
                "core_topic": raw,
            }

        # Tokenize preserving full Unicode Assamese and Latin words
        raw_tokens = re.findall(r"[\u0980-\u09FF\w']+", lower, re.UNICODE)
        tokens = [unicodedata.normalize("NFC", t) for t in raw_tokens if t]
        detected_markers: Set[str] = set()
        is_news = False
        is_temporal = False

        for token in tokens:
            # Check English
            if token in self.en_temporal_words:
                is_temporal = True
                detected_markers.add(token)
            if token in self.en_news_words:
                is_news = True
                is_temporal = True
                detected_markers.add(token)

            # Check Native Assamese
            if token in self.as_temporal_words:
                is_temporal = True
                detected_markers.add(token)
            if token in self.as_news_words:
                is_news = True
                is_temporal = True
                detected_markers.add(token)

            # Check Romanized Assamese
            if token in self.romanized_temporal_words:
                is_temporal = True
                detected_markers.add(token)
            if token in self.romanized_news_words:
                is_news = True
                is_temporal = True
                detected_markers.add(token)

        # Multi-word phrase checks
        if "today's news" in lower or "todays news" in lower:
            is_news = True
            is_temporal = True
            detected_markers.add("today's news")
        for as_phrase in ["শেহতীয়া খবৰ", "শেহতীয়া বাতৰি", "আজিৰ খবৰ", "আজিৰ বাতৰি"]:
            if unicodedata.normalize("NFC", as_phrase) in raw:
                is_news = True
                is_temporal = True
                detected_markers.add(as_phrase)

        # Derive core topic by removing detected markers
        core_tokens = [
            t for t in tokens
            if t not in self.en_temporal_words
            and t not in self.en_news_words
            and t not in self.as_temporal_words
            and t not in self.as_news_words
            and t not in self.romanized_temporal_words
            and t not in self.romanized_news_words
        ]
        core_topic = " ".join(core_tokens).strip() or raw

        return {
            "is_time_sensitive": is_temporal,
            "is_news_intent": is_news,
            "detected_markers": sorted(list(detected_markers)),
            "core_topic": core_topic,
        }
