"""
Unit Tests for Multi-Signal Ranking and Domain Diversity Suppression.
"""

import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "search-api"))
sys.path.insert(0, str(root_dir))

from search.ranking import RankingEngine


def test_ranking_title_boost():
    ranker = RankingEngine()
    terms = ["বিহু"]
    normalized_q = "বিহু"

    doc_with_title_match = {
        "title": "ৰঙালী বিহু উৎসৱ",
        "body_text": "অসমৰ বসন্ত কালৰ উৎসৱ।",
        "language": "as",
        "source_domain": "example1.org",
    }
    doc_with_only_body_match = {
        "title": "অসমৰ লোকসংস্কৃতি",
        "body_text": "ইয়াত বিহু পালন কৰা হয়।",
        "language": "as",
        "source_domain": "example2.org",
    }

    score1 = ranker.score_document(doc_with_title_match, terms, normalized_q, "as_native")
    score2 = ranker.score_document(doc_with_only_body_match, terms, normalized_q, "as_native")

    assert score1 > score2


def test_domain_diversity_suppression():
    ranker = RankingEngine(domain_penalty_factor=0.5)
    terms = ["assam"]
    normalized_q = "assam"

    # Three identical relevance documents from domain A, and one from domain B
    docs = [
        {"id": "1", "title": "Assam News 1", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "2", "title": "Assam News 2", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "3", "title": "Assam News 3", "body_text": "assam", "source_domain": "dominantsite.com"},
        {"id": "4", "title": "Assam Overview", "body_text": "assam", "source_domain": "alternativesite.org"},
    ]

    reranked = ranker.rank_and_diversify(docs, terms, normalized_q, "en", max_results=4)

    # First from dominantsite gets full score, but subsequent ones get penalized
    # alternative site should rise ahead of repeated dominant site results
    domains = [d["source_domain"] for d in reranked]
    assert "alternativesite.org" in domains[:3]


def test_ranking_short_query_word_boundary():
    """Ensure short terms like 'ko' do NOT match inside words like 'Tokyo' or 'Korea'."""
    ranker = RankingEngine()
    terms = ["ko"]
    normalized_q = "ko"

    doc_substring_false_positive = {
        "title": "Tokyo Travel Guide & Tourism",
        "body_text": "Explore Tokyo city districts and culture.",
        "language": "en",
        "source_domain": "travel.org",
    }
    doc_exact_word_match = {
        "title": "Understanding KO in Boxing",
        "body_text": "A knockout (KO) occurs when a fighter cannot continue.",
        "language": "en",
        "source_domain": "boxing.org",
    }

    score_fp = ranker.score_document(doc_substring_false_positive, terms, normalized_q, "en")
    score_exact = ranker.score_document(doc_exact_word_match, terms, normalized_q, "en")

    assert score_fp == 0.0, "Substring 'ko' inside 'Tokyo' must not receive false positive points"
    assert score_exact > 0.0, "Exact word 'KO' should receive points"
    assert score_exact > score_fp


def test_ranking_newest_first_order():
    """Verify that sort_by='newest' places items in descending verified publication order."""
    ranker = RankingEngine()
    terms = ["news", "assam"]
    normalized_q = "news assam"

    docs = [
        {
            "id": "1",
            "title": "Assam News Today",
            "body_text": "Recent news from Assam on Oct 11.",
            "source_domain": "news1.com",
            "published_at": "2026-10-11T10:00:00Z",
            "is_news": True,
        },
        {
            "id": "2",
            "title": "Assam News Breaking",
            "body_text": "Recent news from Assam on Oct 13.",
            "source_domain": "news2.com",
            "published_at": "2026-10-13T10:00:00Z",
            "is_news": True,
        },
        {
            "id": "3",
            "title": "Assam News Yesterday",
            "body_text": "Recent news from Assam on Oct 12.",
            "source_domain": "news3.com",
            "published_at": "2026-10-12T10:00:00Z",
            "is_news": True,
        },
    ]

    reranked = ranker.rank_and_diversify(docs, terms, normalized_q, "en", sort_by="newest")
    ids = [d["id"] for d in reranked]
    assert ids == ["2", "3", "1"], "Should sort descending by publication date: Oct 13, Oct 12, Oct 11"


def test_ranking_undated_placed_last():
    """Verify that undated items (or items with only updated_at) are placed after verified published items."""
    ranker = RankingEngine()
    terms = ["assam", "news"]
    normalized_q = "assam news"

    docs = [
        {
            "id": "wiki-1",
            "title": "Assam News Wikipedia",
            "body_text": "Overview of news media in Assam.",
            "source_domain": "en.wikipedia.org",
            "published_at": None,
            "updated_at": "2026-10-13T12:00:00Z",  # Revision timestamp only
            "is_news": False,
        },
        {
            "id": "news-1",
            "title": "Assam Floods Relief Updates",
            "body_text": "Assam flood news update published Oct 11.",
            "source_domain": "assamtribune.com",
            "published_at": "2026-10-11T08:00:00Z",
            "is_news": True,
        },
        {
            "id": "undated-1",
            "title": "Assam General Info",
            "body_text": "Information about Assam news portal.",
            "source_domain": "portal.org",
            "published_at": None,
            "updated_at": None,
            "is_news": False,
        },
    ]

    reranked = ranker.rank_and_diversify(docs, terms, normalized_q, "en", sort_by="newest")
    # Verified news-1 MUST come before wiki-1 and undated-1
    assert reranked[0]["id"] == "news-1", "Verified publication date must rank before undated / revision-only items"


def test_news_intent_deprioritizes_wikipedia():
    """Verify that queries with news intent deprioritize Wikipedia and boost news sources."""
    ranker = RankingEngine()
    terms = ["news", "assam"]
    normalized_q = "latest assam news"

    doc_wiki = {
        "id": "wiki",
        "title": "The Assam News (newspaper)",
        "body_text": "The Assam News was a historical newspaper in Assam.",
        "source_domain": "en.wikipedia.org",
        "is_news": False,
    }
    doc_news = {
        "id": "news",
        "title": "Current Assam Development News",
        "body_text": "Assam cabinet approves new infrastructure.",
        "source_domain": "assamtribune.com",
        "is_news": True,
    }

    score_wiki = ranker.score_document(doc_wiki, terms, normalized_q, "en", is_news_query=True)
    score_news = ranker.score_document(doc_news, terms, normalized_q, "en", is_news_query=True)

    assert score_news > score_wiki, "News articles should significantly outscore Wikipedia when query is a news query"

