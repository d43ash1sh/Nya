"""
Query Processor for ঞ (Nya) Search.
Combines normalization, script classification, transliteration suggestion,
and multi-script query expansion.
"""

from typing import Dict, Any, List
from nlp.assamese_normalizer import AssameseNormalizer
from nlp.script_detector import ScriptDetector
from nlp.transliteration import AssameseTransliterationEngine


class ProcessedQuery:
    def __init__(
        self,
        raw_query: str,
        normalized_query: str,
        detected_language: str,
        transliterated_query: str,
        search_terms: List[str],
        transliteration_suggestion: str | None = None,
        spelling_suggestion: str | None = None,
    ):
        self.raw_query = raw_query
        self.normalized_query = normalized_query
        self.detected_language = detected_language
        self.transliterated_query = transliterated_query
        self.search_terms = search_terms
        self.transliteration_suggestion = transliteration_suggestion
        self.spelling_suggestion = spelling_suggestion


class QueryProcessor:
    def __init__(self):
        self.normalizer = AssameseNormalizer()
        self.detector = ScriptDetector()
        self.transliteration_engine = AssameseTransliterationEngine()

    def process(self, query: str) -> ProcessedQuery:
        """Process a raw user query into structured search parameters."""
        raw = query.strip()
        normalized = self.normalizer.normalize(raw)
        detected_lang = self.detector.detect(normalized)

        transliteration_suggestion = None
        transliterated_query, was_transliterated = self.transliteration_engine.transliterate_query(normalized)

        if was_transliterated and detected_lang == "as_romanized":
            transliteration_suggestion = transliterated_query

        # Extract search terms and perform cross-script expansion
        terms = self.normalizer.tokenize(normalized)
        expanded_terms = list(terms)

        for term in terms:
            expansions = self.transliteration_engine.get_query_expansion_terms(term)
            for exp in expansions:
                if exp not in expanded_terms:
                    expanded_terms.append(exp)

        return ProcessedQuery(
            raw_query=raw,
            normalized_query=normalized,
            detected_language=detected_lang,
            transliterated_query=transliterated_query,
            search_terms=expanded_terms,
            transliteration_suggestion=transliteration_suggestion,
        )
