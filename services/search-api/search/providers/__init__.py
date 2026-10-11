"""
Search Providers package for ঞ (Nya) Search.
"""

from search.providers.base import BaseSearchProvider
from search.providers.wikipedia import WikipediaProvider
from search.providers.duckduckgo import DuckDuckGoProvider

__all__ = ["BaseSearchProvider", "WikipediaProvider", "DuckDuckGoProvider"]
