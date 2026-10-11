"""
Prompt Injection Defense and Sanitization for Untrusted Web Evidence.
Prevents malicious search content from hijacking LLM instructions.
"""

import re
from typing import List, Dict, Any

# Known prompt injection signatures
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(the\s+)?above", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\s*\|?\s*im_start\s*\|?\s*>", re.IGNORECASE),
    re.compile(r"<\s*\|?\s*im_end\s*\|?\s*>", re.IGNORECASE),
]


class PromptDefender:
    def sanitize_snippet(self, text: str) -> str:
        """Strip dangerous delimiter tricks and injection attempts from retrieved text."""
        sanitized = text

        # Neutralize common prompt injection phrases by defanging them
        for pattern in INJECTION_PATTERNS:
            sanitized = pattern.sub("[FILTERED_POTENTIAL_INJECTION]", sanitized)

        # Escape XML tag markers to prevent closing the evidence tags
        sanitized = sanitized.replace("<evidence", "&lt;evidence").replace("</evidence>", "&lt;/evidence&gt;")
        sanitized = sanitized.replace("<context>", "&lt;context&gt;").replace("</context>", "&lt;/context&gt;")

        return sanitized.strip()

    def build_evidence_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Builds strict, tamper-resistant evidence context for inference.
        Each document is labeled with an unambiguous index [1], [2], etc.
        """
        blocks = []
        for i, doc in enumerate(documents, start=1):
            title = self.sanitize_snippet(doc.get("title", ""))
            snippet = self.sanitize_snippet(doc.get("snippet", ""))
            domain = doc.get("source_domain", "web")
            blocks.append(
                f'<evidence index="{i}" domain="{domain}" title="{title}">\n{snippet}\n</evidence>'
            )

        return "\n\n".join(blocks)
