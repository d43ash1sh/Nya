"""
Assamese Unicode Text Normalizer.
Handles Assamese-specific characters (ৱ, ৰ, ক্ষ, য়, ড়, ঢ়),
Unicode NFC normalization, ZWJ/ZWNJ cleanup, and diacritic handling.
"""

import unicodedata
import re

# Assamese script Unicode block: U+0980 to U+09FF
ASSAMESE_UNICODE_RANGE = re.compile(r"[\u0980-\u09FF]")

# Specific Assamese distinct graphemes
ASSAMESE_WA = "\u09F0"  # ৱ (Assamese letter Va/Wa)
ASSAMESE_RA = "\u09F1"  # ৰ (Assamese letter Ra)
BENGALI_RA = "\u09B0"   # র (Bengali letter Ra)
BENGALI_BA = "\u09AC"   # ব (Bengali letter Ba)

# Zero-width characters
ZWJ = "\u200D"
ZWNJ = "\u200C"


class AssameseNormalizer:
    """Normalizes Assamese and multilingual search text."""

    def __init__(self, canonicalize_bengali_script: bool = True):
        self.canonicalize_bengali = canonicalize_bengali_script

    def normalize(self, text: str) -> str:
        """
        Full normalization pipeline for Assamese and multilingual queries.
        1. Unicode normalization (NFC)
        2. Zero-width character cleanup
        3. Assamese character canonicalization (e.g. mapping Bengali Ra to Assamese Ra when appropriate)
        4. Diacritic and space standardization
        """
        if not text:
            return ""

        # Step 1: Unicode NFC normalization
        normalized = unicodedata.normalize("NFC", text)

        # Step 2: Remove redundant zero-width non-joiners unless preceded by virama
        # Keep ZWJ/ZWNJ if part of legitimate ligature, else remove isolated ones
        normalized = re.sub(r"(?<!\u09CD)[\u200C\u200D]", "", normalized)

        # Step 3: Canonicalize character variants
        if self.canonicalize_bengali:
            # When indexing Assamese literature, map cross-script variants to Assamese standards
            # For instance, substitute Bengali Ra (র) with Assamese Ra (ৰ) in search indices
            normalized = normalized.replace(BENGALI_RA, ASSAMESE_RA)

        # Step 4: Normalize danda punctuation and whitespaces
        normalized = re.sub(r"[।॥]+", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text respecting Assamese and Latin word boundaries."""
        normalized = self.normalize(text)
        # Split on whitespace and non-word characters except Assamese diacritics
        tokens = re.findall(r"[\u0980-\u09FF\w]+", normalized, re.UNICODE)
        return [t.lower() if t.isascii() else t for t in tokens if t]

    def contains_assamese(self, text: str) -> bool:
        """Check if string contains native Assamese/Eastern Indic characters."""
        return bool(ASSAMESE_UNICODE_RANGE.search(text))

    def has_distinct_assamese_chars(self, text: str) -> bool:
        """Check if string contains specifically Assamese characters (ৱ or ৰ)."""
        return ASSAMESE_WA in text or ASSAMESE_RA in text
