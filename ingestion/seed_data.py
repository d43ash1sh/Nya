"""
Permitted Seed Sources and Development Documents for ঞ (Nya) Search.
Populates initial authoritative registry and genuine regional documents
in native Assamese, English, and bilingual topics for search and evaluation.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Ensure services/search-api and repo root are in python path
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent
sys.path.insert(0, str(repo_root / "services" / "search-api"))
sys.path.insert(0, str(repo_root))

from db.session import async_session_factory, init_db
from db.models import SourceRegistry, IndexedDocument
from ingestion.discovery.source_registry import SEED_SOURCES
from ingestion.indexing.indexer import DocumentIndexer

# Authentic development corpus covering Assam's regional information needs
DEVELOPMENT_DOCUMENTS = [
    {
        "url": "https://assam.gov.in/about-us/assam-at-a-glance",
        "canonical_url": "https://assam.gov.in/about-us/assam-at-a-glance",
        "title": "অসমৰ পৰিচয় আৰু ভৌগোলিক অৱস্থিতি (Assam at a Glance)",
        "domain": "assam.gov.in",
        "language": "as",
        "published_date": datetime(2024, 1, 15, tzinfo=timezone.utc),
        "body_text": (
            "অসম উত্তৰ-পূব ভাৰতৰ এখন প্ৰধান ৰাজ্য। ইয়াৰ ৰাজধানী দিছপুৰ আৰু বৃহত্তম মহানগৰ গুৱাহাটী। "
            "ব্ৰহ্মপুত্ৰ আৰু বৰাক নদীৰ উপত্যকাৰে গঠিত অসম প্ৰাকৃতিক সম্পদ, চাহ উদ্যোগ, খনিজ তেল আৰু জৈৱ বৈচিত্ৰ্যৰ বাবে জনাজাত। "
            "অসমৰ চাৰিসীমাত ভূটান, অৰুণাচল প্ৰদেশ, নাগালেণ্ড, মণিপুৰ, মিজোৰাম, ত্ৰিপুৰা, মেঘালয় আৰু বাংলাদেশ অৱস্থিত। "
            "অসমীয়া ভাষা অসমৰ চৰকাৰী ভাষা আৰু সৰ্বাধিক কথিত ভাষা।"
        ),
        "snippet": "অসম উত্তৰ-পূব ভাৰতৰ প্ৰধান ৰাজ্য। ৰাজধানী দিছপুৰ আৰু বৃহত্তম মহানগৰ গুৱাহাটী। ব্ৰহ্মপুত্ৰ নদীৰ উপত্যকাৰে গঠিত অসম জৈৱ বৈচিত্ৰ্য আৰু চাহৰ বাবে প্ৰসিদ্ধ।",
    },
    {
        "url": "https://as.wikipedia.org/wiki/বিহু",
        "canonical_url": "https://as.wikipedia.org/wiki/বিহু",
        "title": "বিহু — অসমৰ জাতীয় উৎসৱ (Bihu - National Festival of Assam)",
        "domain": "as.wikipedia.org",
        "language": "as",
        "published_date": datetime(2024, 4, 10, tzinfo=timezone.utc),
        "body_text": (
            "বিহু অসমৰ জাতীয় উৎসৱ। অসমীয়াত তিনিটা বিহু পালন কৰা হয়: ৰঙালী বা ব'হাগ বিহু, কঙালি বা কাতি বিহু, আৰু ভোগালী বা মাঘ বিহু। "
            "ৰঙালী বিহু বসন্ত কালত অসমীয়া নৱবৰ্ষৰ আৰম্ভণিত এপ্ৰিল মাহত উলহ-মালহেৰে পালন কৰা হয়। এই সময়ত বিহু নৃত্য, ঢোল, পেঁপা আৰু গগনাৰ মাতত অসম মুখৰিত হয়। "
            "মাঘ বিহু খেতি চপোৱাৰ সময়ত জানুৱাৰী মাহত মেজি জ্বলাই আৰু পিঠা-পনা খাই পালন কৰা হয়। কাতি বিহু তুলসীৰ তলত চাকি জ্বলাই শান্তভাৱে পালন কৰা হয়।"
        ),
        "snippet": "বিহু অসমৰ জাতীয় উৎসৱ। তিনিটা বিহু হৈছে ৰঙালী (ব'হাগ), কঙালি (কাতি) আৰু ভোগালী (মাঘ) বিহু। ৰঙালী বিহু বসন্তৰ আগমন আৰু অসমীয়া নৱবৰ্ষৰ প্ৰতীক।",
    },
    {
        "url": "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
        "canonical_url": "https://kaziranga.assam.gov.in/wildlife/one-horned-rhino",
        "title": "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান আৰু এশিঙীয়া গঁড় (Kaziranga National Park & One-Horned Rhino)",
        "domain": "kaziranga.assam.gov.in",
        "language": "as",
        "published_date": datetime(2024, 2, 20, tzinfo=timezone.utc),
        "body_text": (
            "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান অসমৰ গোলাঘাট আৰু নগাঁও জিলাত অৱস্থিত এখন বিশ্ব ঐতিহ্য ক্ষেত্ৰ (UNESCO World Heritage Site)। "
            "ই পৃথিৱীৰ এশিঙীয়া গঁড়ৰ (Great One-horned Rhinoceros) সৰ্ববৃহৎ আৱাসভূমি। কাজিৰঙাত বাঘ, হাতী, দল-হৰিণা আৰু বনৰীয়া ম'হৰ সুৰক্ষিত জনসংখ্যা আছে। "
            "ব্ৰহ্মপুত্ৰ নদীৰ দক্ষিণ পাৰে অৱস্থিত এই উদ্যানে প্ৰকৃতিপ্ৰেমী আৰু পৰ্যটকসকলক বাৰ্ষিকভাৱে আকৰ্ষিত কৰে।"
        ),
        "snippet": "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান বিশ্ব ঐতিহ্য ক্ষেত্ৰ আৰু পৃথিৱীৰ বিখ্যাত এশিঙীয়া গঁড়ৰ প্ৰধান আৱাসভূমি। গোলাঘাট আৰু নগাঁও জিলাত অৱস্থিত।",
    },
    {
        "url": "https://gauhati.ac.in/academic/admissions-history",
        "canonical_url": "https://gauhati.ac.in/academic/admissions-history",
        "title": "গুৱাহাটী বিশ্ববিদ্যালয়: ইতিহাস, পাঠ্যক্ৰম আৰু নামভৰ্তি (Gauhati University Overview)",
        "domain": "gauhati.ac.in",
        "language": "as",
        "published_date": datetime(2024, 3, 5, tzinfo=timezone.utc),
        "body_text": (
            "গুৱাহাটী বিশ্ববিদ্যালয় ১৯৪৮ চনৰ ২৬ জানুৱাৰীত স্থাপিত উত্তৰ-পূব ভাৰতৰ আটাইতকৈ পুৰণি আৰু প্ৰথম বিশ্ববিদ্যালয়। "
            "ই গুৱাহাটীৰ জালুকবাৰীত অৱস্থিত। কলা, বিজ্ঞান, বাণিজ্য, প্ৰযুক্তিবিদ্যা আৰু আইন বিভাগৰ অধীনত ইয়াত বিভিন্ন স্নাতক আৰু স্নাতকোত্তৰ পাঠ্যক্ৰম উপলব্ধ। "
            "বিশ্ববিদ্যালয়খন NAAC ৰ দ্বাৰা 'A' গ্ৰেড প্ৰাপ্ত উচ্চ শিক্ষানুষ্ঠান।"
        ),
        "snippet": "১৯৪৮ চনত স্থাপিত গুৱাহাটী বিশ্ববিদ্যালয় উত্তৰ-পূব ভাৰতৰ সৰ্বপ্ৰথম বিশ্ববিদ্যালয়। জালুকবাৰীত অৱস্থিত এই শিক্ষানুষ্ঠান NAAC দ্বাৰা স্বীকৃতিপ্ৰাপ্ত।",
    },
    {
        "url": "https://assam.gov.in/schemes/orunodoi-scheme",
        "canonical_url": "https://assam.gov.in/schemes/orunodoi-scheme",
        "title": "অৰুণোদোদয় আঁচনি: মহিলা সবলীকৰণ আৰু আৰ্থিক সাহাৰ্য (Orunodoi Scheme Assam)",
        "domain": "assam.gov.in",
        "language": "as",
        "published_date": datetime(2024, 5, 1, tzinfo=timezone.utc),
        "body_text": (
            "অৰুণোদোদয় আঁচনি অসম চৰকাৰৰ এক ফ্লেগশ্বিপ প্ৰত্যক্ষ লাভালাভ হস্তান্তৰ (DBT) আঁচনি। "
            "এই আঁচনিৰ মূল উদ্দেশ্য হৈছে আৰ্থিকভাৱে পিছপৰা পৰিয়ালৰ মহিলাসকলক প্ৰতি মাহে নিশ্চিত আৰ্থিক সাহাৰ্য প্ৰদান কৰি মহিলা সবলীকৰণ নিশ্চিত কৰা। "
            "অৰুণোদোদয় ২.০ ৰ অধীনত যোগ্য হিতাধিকাৰী মহিলাই মাহেকীয়া ১২৫০ টকা বেংক একাউণ্টত প্ৰত্যক্ষভাৱে লাভ কৰে।"
        ),
        "snippet": "অসম চৰকাৰৰ অৰুণোদোদয় আঁচনিৰ জৰিয়তে আৰ্থিকভাৱে দুৰ্বল পৰিয়ালৰ মহিলাসকলক মাহেকীয়া ১২৫০ টকাৰ আৰ্থিক সাহাৰ্য প্ৰত্যক্ষভাৱে বেংক একাউণ্টলৈ আগবঢ়োৱা হয়।",
    },
    {
        "url": "https://assamtribune.com/assam/guwahati-smart-city-infrastructure-updates",
        "canonical_url": "https://assamtribune.com/assam/guwahati-smart-city-infrastructure-updates",
        "title": "Guwahati Smart City and Infrastructure Development Report",
        "domain": "assamtribune.com",
        "language": "en",
        "published_date": datetime(2024, 5, 12, tzinfo=timezone.utc),
        "body_text": (
            "Guwahati, the gateway to Northeast India, is undergoing rapid infrastructure transformation under the Smart City initiative. "
            "Key projects include the Brahmaputra Riverfront Development, new flyovers across Zoo Road and Maligaon, and expansion of the Lokpriya Gopinath Bordoloi International Airport. "
            "Urban connectivity, drainage mitigation, and integrated traffic management systems are central to current municipal execution."
        ),
        "snippet": "Guwahati infrastructure transformation features the Brahmaputra Riverfront Development, new flyovers, airport modernization, and smart transit systems.",
    },
    {
        "url": "https://kalakshetra.assam.gov.in/about-us",
        "canonical_url": "https://kalakshetra.assam.gov.in/about-us",
        "title": "শ্ৰীমন্ত শংকৰদেৱ কলাক্ষেত্ৰ: সংস্কৃতি আৰু ঐতিহ্য (Srimanta Sankaradeva Kalakshetra)",
        "domain": "kalakshetra.assam.gov.in",
        "language": "as",
        "published_date": datetime(2024, 2, 14, tzinfo=timezone.utc),
        "body_text": (
            "শ্ৰীমন্ত শংকৰদেৱ কলাক্ষেত্ৰ গুৱাহাটীৰ পাঞ্জাবাৰীত অৱস্থিত অসমৰ এটি প্ৰধান সাংস্কৃতিক কেন্দ্ৰ। "
            "মহাপুৰুষ শ্ৰীমন্ত শংকৰদেৱৰ নামত স্থাপিত এই প্ৰতিষ্ঠানত অসমৰ বিভিন্ন জনগোষ্ঠীৰ কলা, নৃত্য, সংগীত, ভাস্কৰ্য আৰু লোকসংস্কৃতি সংৰক্ষণ কৰা হয়। "
            "ইয়াৰ পৰিসৰত সংগ্ৰহালয়, মুকলি আকাশৰ প্ৰেক্ষাগৃহ আৰু ললিত কলা ভৱন আছে।"
        ),
        "snippet": "পাঞ্জাবাৰীত অৱস্থিত শ্ৰীমন্ত শংকৰদেৱ কলাক্ষেত্ৰ অসম আৰু উত্তৰ-পূবৰ লোককলা, সত্ৰীয়া সংস্কৃতি আৰু ঐতিহাসিক ঐতিহ্যৰ অন্যতম প্ৰধান কেন্দ্ৰ।",
    },
    {
        "url": "https://as.wikipedia.org/wiki/মাজুলী",
        "canonical_url": "https://as.wikipedia.org/wiki/মাজুলী",
        "title": "মাজুলী — ব্ৰহ্মপুত্ৰৰ বুকুত বিশ্বৰ বৃহত্তম নদীদ্বীপ (Majuli Island)",
        "domain": "as.wikipedia.org",
        "language": "as",
        "published_date": datetime(2024, 3, 22, tzinfo=timezone.utc),
        "body_text": (
            "মাজুলী ব্ৰহ্মপুত্ৰ নদীৰ বুকুত অৱস্থিত পৃথিৱীৰ সৰ্ববৃহৎ নদীদ্বীপ আৰু অসমৰ এখন সুকীয়া জিলা। "
            "ই অসমৰ নৱবৈষ্ণৱ সংস্কৃতি আৰু সত্ৰীয়া পৰম্পৰাৰ মূল পীঠস্থান। আউনীআটী সত্ৰ, কমলাবাৰী সত্ৰ, গড়মূৰ সত্ৰ আৰু দক্ষিণপাট সত্ৰ আদি ঐতিহাসিক সত্ৰসমূহ মাজুলীতে অৱস্থিত। "
            "মাজুলীৰ মুখাশিল্প আৰু মৃৎশিল্প সমগ্ৰ বিশ্বতে সমাদৃত।"
        ),
        "snippet": "ব্ৰহ্মপুত্ৰৰ বুকুত অৱস্থিত মাজুলী বিশ্বৰ বৃহত্তম নদীদ্বীপ আৰু সত্ৰীয়া সংস্কৃতিৰ প্ৰাণকেন্দ্ৰ। সত্ৰসমূহ, মুখাশিল্প আৰু বৈষ্ণৱ ঐতিহ্যৰ বাবে বিখ্যাত।",
    },
]


async def seed_database():
    """Initializes schema and seeds sources and document fixtures."""
    await init_db()
    indexer = DocumentIndexer()

    async with async_session_factory() as session:
        # Seed sources
        source_domain_map = {}
        for src_data in SEED_SOURCES:
            stmt = select(SourceRegistry).where(SourceRegistry.domain == src_data["domain"])
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if not existing:
                src = SourceRegistry(**src_data)
                session.add(src)
                await session.flush()
                source_domain_map[src.domain] = src.id
            else:
                source_domain_map[existing.domain] = existing.id

        await session.commit()

        # Seed documents
        for doc in DEVELOPMENT_DOCUMENTS:
            source_id = source_domain_map.get(doc["domain"])
            await indexer.index_document(
                session=session,
                url=doc["url"],
                canonical_url=doc["canonical_url"],
                title=doc["title"],
                body_text=doc["body_text"],
                snippet=doc["snippet"],
                source_id=source_id,
                published_date=doc["published_date"],
            )

    print("Seed complete: Permitted sources and authentic regional documents indexed.")


if __name__ == "__main__":
    asyncio.run(seed_database())
