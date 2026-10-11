"""
Permitted Source Registry for ঞ (Nya) Search.
Manages source discovery, permissions, robots.txt metadata,
and regional authoritativeness.
"""

from typing import List, Dict, Any


SEED_SOURCES: List[Dict[str, Any]] = [
    {
        "domain": "assam.gov.in",
        "name": "Government of Assam Official Portal",
        "base_url": "https://assam.gov.in",
        "crawl_allowed": True,
        "robots_txt_url": "https://assam.gov.in/robots.txt",
        "license_info": "Open Government Data (OGD) India / Public Sector Information",
        "language_focus": "mixed",
        "rate_limit_delay": 2.0,
        "is_authoritative": True,
    },
    {
        "domain": "gauhati.ac.in",
        "name": "Gauhati University",
        "base_url": "https://gauhati.ac.in",
        "crawl_allowed": True,
        "robots_txt_url": "https://gauhati.ac.in/robots.txt",
        "license_info": "Educational Institutional Public Web",
        "language_focus": "mixed",
        "rate_limit_delay": 2.0,
        "is_authoritative": True,
    },
    {
        "domain": "assamtribune.com",
        "name": "The Assam Tribune",
        "base_url": "https://assamtribune.com",
        "crawl_allowed": True,
        "robots_txt_url": "https://assamtribune.com/robots.txt",
        "license_info": "News Publisher Public Metadata",
        "language_focus": "en",
        "rate_limit_delay": 3.0,
        "is_authoritative": True,
    },
    {
        "domain": "kaziranga.assam.gov.in",
        "name": "Kaziranga National Park & Tiger Reserve",
        "base_url": "https://kaziranga.assam.gov.in",
        "crawl_allowed": True,
        "robots_txt_url": "https://kaziranga.assam.gov.in/robots.txt",
        "license_info": "Forest Department Public Information",
        "language_focus": "mixed",
        "rate_limit_delay": 2.0,
        "is_authoritative": True,
    },
    {
        "domain": "as.wikipedia.org",
        "name": "অসমীয়া ৱিকিপিডিয়া (Assamese Wikipedia)",
        "base_url": "https://as.wikipedia.org",
        "crawl_allowed": True,
        "robots_txt_url": "https://as.wikipedia.org/robots.txt",
        "license_info": "Creative Commons Attribution-ShareAlike (CC BY-SA 4.0)",
        "language_focus": "as",
        "rate_limit_delay": 1.5,
        "is_authoritative": False,
    },
    {
        "domain": "kalakshetra.assam.gov.in",
        "name": "Srimanta Sankaradeva Kalakshetra",
        "base_url": "https://kalakshetra.assam.gov.in",
        "crawl_allowed": True,
        "robots_txt_url": "https://kalakshetra.assam.gov.in/robots.txt",
        "license_info": "Cultural Affairs Directorate Public Information",
        "language_focus": "mixed",
        "rate_limit_delay": 2.0,
        "is_authoritative": True,
    },
    {
        "domain": "dheassam.gov.in",
        "name": "Directorate of Higher Education, Assam",
        "base_url": "https://dheassam.gov.in",
        "crawl_allowed": True,
        "robots_txt_url": "https://dheassam.gov.in/robots.txt",
        "license_info": "Government of Assam Official Public Portal",
        "language_focus": "mixed",
        "rate_limit_delay": 2.0,
        "is_authoritative": True,
    },
]
