"""
Automated 30+ Query Search Coverage and General-Purpose Retrieval Evaluation for ঞ (Nya) Search.
Evaluates:
- General knowledge, Science, Tech, History, Geography
- Native Assamese, Romanized Assamese, English, Mixed language
- Result counts, top source domains, AI grounding, and latencies
"""

import urllib.request
import urllib.parse
import json
import time
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TEST_QUERIES = [
    # 1. Native Assamese Culture & Heritage
    {"query": "ৰঙালী বিহু", "category": "Assamese Culture"},
    {"query": "কাজিৰঙা ৰাষ্ট্ৰীয় উদ্যান", "category": "Assam Wildlife"},
    {"query": "শ্ৰীমন্ত শংকৰদেৱ বৰগীত", "category": "Assamese Literature"},
    {"query": "মাজুলী নদীদ্বীপ ঐতিহ্য", "category": "Assam Geography"},
    {"query": "লাচিত বৰফুকন শৰাইঘাট", "category": "Assam History"},
    {"query": "চৰাইদেউ মৈদাম", "category": "Heritage Sites"},

    # 2. Technology & Programming
    {"query": "Python programming language", "category": "Computer Science"},
    {"query": "Next.js React framework", "category": "Web Development"},
    {"query": "FastAPI framework tutorial", "category": "Software Engineering"},
    {"query": "Quantum computing", "category": "Future Tech"},

    # 3. Science & Nature
    {"query": "Photosynthesis process", "category": "Biology"},
    {"query": "DNA double helix structure", "category": "Genetics"},
    {"query": "Black hole physics", "category": "Astrophysics"},
    {"query": "James Webb Space Telescope", "category": "Space Exploration"},

    # 4. History & World Knowledge
    {"query": "Indus Valley Civilization", "category": "Ancient History"},
    {"query": "Albert Einstein theory of relativity", "category": "Biography & Physics"},
    {"query": "Indian Constitution fundamental rights", "category": "Civics & Law"},
    {"query": "Mahatma Gandhi freedom struggle", "category": "Modern History"},

    # 5. Organizations & Institutions
    {"query": "Indian Space Research Organisation ISRO", "category": "Institutions"},
    {"query": "Gauhati University Assam", "category": "Higher Education"},
    {"query": "IIT Guwahati campus research", "category": "Higher Education"},
    {"query": "World Health Organization", "category": "Global Organizations"},

    # 6. Geography & Places
    {"query": "Brahmaputra river origin and course", "category": "Geography"},
    {"query": "Himalayas mountain range", "category": "Physical Geography"},
    {"query": "Guwahati Smart City developments", "category": "Urban Development"},

    # 7. Romanized Assamese (Transliterated)
    {"query": "axom bhugol", "category": "Romanized Assamese"},
    {"query": "bihu geet itihas", "category": "Romanized Assamese"},
    {"query": "kaziranga rhino conservation", "category": "Romanized Assamese"},
    {"query": "guwahati biswabidyalay admission", "category": "Romanized Assamese"},

    # 8. Mixed Queries & Current Topics
    {"query": "Assam tea industry economy", "category": "Economy & Agriculture"},
    {"query": "Renewable solar energy India", "category": "Energy & Climate"},
    {"query": "অৰুণোদোদয় আঁচনি নিৰ্দেশনা", "category": "Government Schemes"},
]

def run_evaluation():
    base_url = "http://127.0.0.1:8000/api/v1/search"
    results_report = []

    print(f"\n=======================================================")
    print(f" ঞ (Nya) Search Engine — 30+ Query Coverage Evaluation")
    print(f"=======================================================\n")

    passed_count = 0
    total_count = len(TEST_QUERIES)

    for i, test_case in enumerate(TEST_QUERIES, start=1):
        q = test_case["query"]
        category = test_case["category"]

        encoded_q = urllib.parse.quote(q)
        url = f"{base_url}?q={encoded_q}&enable_ai=true"

        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NyaEvaluationRunner/1.0"})
            with urllib.request.urlopen(req, timeout=12) as response:
                duration_ms = round((time.time() - t0) * 1000, 1)
                data = json.loads(response.read().decode("utf-8"))

                total_results = data.get("total_results", 0)
                items = data.get("results", [])
                det_lang = data.get("detected_language", "unknown")
                has_ai = bool(data.get("ai_answer") and data.get("ai_answer", {}).get("answer"))

                top_domain = items[0].get("source_domain", "N/A") if items else "None"
                top_title = items[0].get("title", "") if items else ""

                is_pass = total_results > 0
                if is_pass:
                    passed_count += 1

                status_str = "PASS" if is_pass else "FAIL"

                print(f"[{i:02d}/{total_count}] [{status_str}] {category.ljust(22)} | Query: {q[:30].ljust(30)}")
                print(f"     -> Results: {total_results} | Lang: {det_lang} | Top Domain: {top_domain} | AI: {has_ai} | Latency: {duration_ms}ms")

                results_report.append({
                    "index": i,
                    "query": q,
                    "category": category,
                    "status": status_str,
                    "results_count": total_results,
                    "detected_language": det_lang,
                    "top_domain": top_domain,
                    "top_title": top_title,
                    "has_ai_answer": has_ai,
                    "latency_ms": duration_ms,
                })

        except Exception as e:
            duration_ms = round((time.time() - t0) * 1000, 1)
            print(f"[{i:02d}/{total_count}] [ERROR] {category.ljust(22)} | Query: {q[:30].ljust(30)} -> Error: {e}")
            results_report.append({
                "index": i,
                "query": q,
                "category": category,
                "status": "ERROR",
                "error": str(e),
                "latency_ms": duration_ms,
            })

    print(f"\n=======================================================")
    print(f" Evaluation Completed: {passed_count}/{total_count} Passed ({round(passed_count / total_count * 100, 1)}%)")
    print(f"=======================================================\n")

    # Save structured report
    with open("evaluation/coverage_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_queries": total_count,
            "passed": passed_count,
            "coverage_percentage": round(passed_count / total_count * 100, 1),
            "results": results_report,
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_evaluation()
