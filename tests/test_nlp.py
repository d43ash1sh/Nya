"""
Unit Tests for Assamese NLP, Normalization, Transliteration, and Script Detection.
"""

import sys
from pathlib import Path
import pytest

# Ensure search-api is in path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "search-api"))
sys.path.insert(0, str(root_dir))

from nlp.assamese_normalizer import AssameseNormalizer
from nlp.transliteration import AssameseTransliterationEngine
from nlp.script_detector import ScriptDetector
from nlp.query_processor import QueryProcessor


def test_assamese_normalizer_nfc_and_whitespace():
    norm = AssameseNormalizer()
    raw = "  অসমৰ   ৰাজধানী  দিছপুৰ ।  "
    res = norm.normalize(raw)
    assert res == "অসমৰ ৰাজধানী দিছপুৰ"


def test_assamese_normalizer_bengali_ra_canonicalization():
    norm = AssameseNormalizer(canonicalize_bengali_script=True)
    # Bengali Ra U+09B0 should be canonicalized to Assamese Ra U+09F1
    text_with_bengali_ra = "ভারত"  # with U+09B0
    res = norm.normalize(text_with_bengali_ra)
    assert "\u09F1" in res  # Assamese Ra


def test_assamese_normalizer_tokens():
    norm = AssameseNormalizer()
    tokens = norm.tokenize("ৰঙালী বিহু 2026")
    assert "ৰঙালী" in tokens
    assert "বিহু" in tokens
    assert "2026" in tokens


def test_transliteration_dictionary_lookup():
    engine = AssameseTransliterationEngine()
    # Test high-frequency Romanized Assamese terms
    assert engine.transliterate_word("axom") == "অসম"
    assert engine.transliterate_word("asom") == "অসম"
    assert engine.transliterate_word("namaskar") == "নমস্কাৰ"
    assert engine.transliterate_word("bhal") == "ভাল"
    assert engine.transliterate_word("guwahati") == "গুৱাহাটী"
    assert engine.transliterate_word("kaziranga") == "কাজিৰঙা"


def test_transliteration_full_query():
    engine = AssameseTransliterationEngine()
    query, was_converted = engine.transliterate_query("axom batorikakhot")
    assert was_converted is True
    assert "অসম" in query


def test_script_detector():
    detector = ScriptDetector()
    assert detector.detect("অসমৰ ভূগোল") == "as_native"
    assert detector.detect("London weather forecast and news") == "en"
    assert detector.detect("axom tourism") == "as_romanized"
    assert detector.detect("অসম tourism") == "mixed"


def test_query_processor_flow():
    qp = QueryProcessor()
    processed = qp.process("axom kaziranga")
    assert processed.detected_language == "as_romanized"
    assert processed.transliteration_suggestion is not None
    assert "অসম" in processed.transliteration_suggestion
    assert "অসম" in processed.search_terms


def test_transliteration_ko():
    engine = AssameseTransliterationEngine()
    assert engine.transliterate_word("ko") == "ক'"
    assert engine.transliterate_word("k") == "ক"


def test_ambiguous_query_detection():
    detector = ScriptDetector()
    assert detector.is_ambiguous_query("ko") is True
    assert detector.is_ambiguous_query("ki") is True
    assert detector.is_ambiguous_query("kaziranga") is False
    assert detector.is_ambiguous_query("বিহু") is False
