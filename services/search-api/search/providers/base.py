"""
Base Search Provider Interface for ঞ (Nya) Search.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseSearchProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        detected_language: str,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Execute search and return a list of standardized document dictionaries:
        {
            "id": str,
            "url": str,
            "canonical_url": str,
            "title": str,
            "body_text": str,
            "snippet": str,
            "language": str,
            "content_hash": str,
            "published_date": datetime or None,
            "source_name": str,
            "source_domain": str,
            "is_authoritative": bool,
        }
        """
        pass
