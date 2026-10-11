"""
Multilingual Evaluation Benchmark Queries and Ground-Truth Relevance Judgments.
Covers:
- Native Assamese (as_native)
- Romanized Assamese (as_romanized)
- English (en)
- Mixed-language (mixed)
"""

from typing import List, Dict, Any

EVALUATION_QUERIES: List[Dict[str, Any]] = [
    # 1. Native Assamese queries
    {
        "query": "অসমৰ ৰাজধানী আৰু ভূগোল",
        "category": "as_native",
        "expected_relevant_urls": [
            "https://assam.gov.in/about-us/assam-at-a-glance",
            "https://as.wikipedia.org/wiki/মাজুলী",
        ],
    },
    {
        "query": "ৰঙালী বিহু অসমৰ জাতীয় উৎসৱ",
        "category": "as_native",
        "expected_relevant_urls": [
            "https://as.wikipedia.org/wiki/বিহু",
            "https://kalakshetra.assam.gov.in/about-us",
        ],
    },
    {
        "query": "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান এশিঙীয়া গঁড়",
        "category": "as_native",
        "expected_relevant_urls": [
            "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
            "https://assam.gov.in/about-us/assam-at-a-glance",
        ],
    },
    {
        "query": "গুৱাহাটী বিশ্ববিদ্যালয় শিক্ষা",
        "category": "as_native",
        "expected_relevant_urls": [
            "https://gauhati.ac.in/academic/admissions-history",
        ],
    },
    {
        "query": "অৰুণোদোদয় আঁচনি মহিলা সবলীকৰণ",
        "category": "as_native",
        "expected_relevant_urls": [
            "https://assam.gov.in/schemes/orunodoi-scheme",
        ],
    },

    # 2. Romanized Assamese queries
    {
        "query": "axom bhugol aru nodi",
        "category": "as_romanized",
        "expected_relevant_urls": [
            "https://assam.gov.in/about-us/assam-at-a-glance",
            "https://as.wikipedia.org/wiki/মাজুলী",
        ],
    },
    {
        "query": "bihu utsav rongali",
        "category": "as_romanized",
        "expected_relevant_urls": [
            "https://as.wikipedia.org/wiki/বিহু",
        ],
    },
    {
        "query": "kaziranga rhino udyan",
        "category": "as_romanized",
        "expected_relevant_urls": [
            "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
        ],
    },
    {
        "query": "guwahati smart city",
        "category": "as_romanized",
        "expected_relevant_urls": [
            "https://assamtribune.com/assam/guwahati-smart-city-infrastructure-updates",
        ],
    },

    # 3. English queries
    {
        "query": "Guwahati Smart City infrastructure developments",
        "category": "en",
        "expected_relevant_urls": [
            "https://assamtribune.com/assam/guwahati-smart-city-infrastructure-updates",
        ],
    },
    {
        "query": "Kaziranga national park rhinoceros sanctuary",
        "category": "en",
        "expected_relevant_urls": [
            "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
            "https://assam.gov.in/about-us/assam-at-a-glance",
        ],
    },
    {
        "query": "Gauhati University history and admissions",
        "category": "en",
        "expected_relevant_urls": [
            "https://gauhati.ac.in/academic/admissions-history",
        ],
    },

    # 4. Mixed-language queries
    {
        "query": "অসম tourism and Kaziranga wildlife",
        "category": "mixed",
        "expected_relevant_urls": [
            "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
            "https://assam.gov.in/about-us/assam-at-a-glance",
        ],
    },
    {
        "query": "Guwahati বিশ্ববিদ্যালয় courses and admissions",
        "category": "mixed",
        "expected_relevant_urls": [
            "https://gauhati.ac.in/academic/admissions-history",
        ],
    },
    {
        "query": "Bihu festival ৰঙালী বিহু traditions",
        "category": "mixed",
        "expected_relevant_urls": [
            "https://as.wikipedia.org/wiki/বিহু",
            "https://kalakshetra.assam.gov.in/about-us",
        ],
    },
]
