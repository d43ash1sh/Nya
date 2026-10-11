"""
Assamese Romanized Transliteration and Phonetic Engine.
Maps Latin-script Assamese phonetic queries (e.g. 'axom', 'asom', 'namaskar', 'bhal', 'khobor')
to native Assamese script and provides query expansion.
"""

from typing import Dict, List, Optional, Tuple
import re

# Comprehensive dictionary for common Assamese terms in Romanized forms
ROMANIZED_DICTIONARY: Dict[str, str] = {
    # Places & Geography
    "asom": "অসম",
    "axom": "অসম",
    "assam": "অসম",
    "guwahati": "গুৱাহাটী",
    "gauhati": "গুৱাহাটী",
    "jorhat": "যোৰহাট",
    "dibrugarh": "ডিব্ৰুগড়",
    "silchar": "শিলচৰ",
    "tezpur": "তেজপুৰ",
    "nagaon": "নগাঁও",
    "kaziranga": "কাজিৰঙা",
    "majuli": "মাজুলী",
    "brahmaputra": "ব্ৰহ্মপুত্ৰ",
    "sivasagar": "শিৱসাগৰ",
    "haflong": "হাফলং",

    # Greetings & Common Phrases
    "namaskar": "নমস্কাৰ",
    "nomoskar": "নমস্কাৰ",
    "dhanyabad": "ধন্যবাদ",
    "dhonnobad": "ধন্যবাদ",
    "bhal": "ভাল",
    "bhaal": "ভাল",
    "khobor": "খবৰ",
    "ki": "কি",
    "kenekoi": "কেনেকৈ",
    "keneke": "কেনেকৈ",
    "kot": "ক'ত",
    "etiya": "এতিয়া",
    "aji": "আজি",
    "kali": "কালি",
    "kailoi": "কাইলৈ",

    # Culture & Society
    "bihu": "বিহু",
    "rongali": "ৰঙালী",
    "bhogali": "ভোগালী",
    "kongali": "কঙালি",
    "bhortaal": "ভোৰতাল",
    "sattriya": "সত্ৰীয়া",
    "naamghar": "নামঘৰ",
    "namghar": "নামঘৰ",
    "gamosa": "গামোচা",
    "gamusa": "গামোচা",
    "mekhela": "মেখেলা",
    "chador": "চাদৰ",
    "sador": "চাদৰ",
    "dhol": "ঢোল",
    "pepa": "পেঁপা",

    # Public Services, Education & News
    "khobor": "খবৰ",
    "batori": "বাতৰি",
    "sorkar": "চৰকাৰ",
    "xorkar": "চৰকাৰ",
    "porikha": "পৰীক্ষা",
    "porikhya": "পৰীক্ষা",
    "result": "ফলাফল",
    "folafol": "ফলাফল",
    "vidyalaya": "বিদ্যালয়",
    "bidyaloy": "বিদ্যালয়",
    "biswabidyalay": "বিশ্ববিদ্যালয়",
    "swasthya": "স্বাস্থ্য",
    "chakari": "চাকৰি",
    "chakri": "চাকৰি",
    "nizukti": "নিযুক্তি",
    "krishi": "কৃষি",
    "paryatan": "পৰ্যটন",
    "baxonto": "বসন্ত",
}

# Inverted mapping: Native script to popular Romanized representation
NATIVE_TO_ROMANIZED: Dict[str, str] = {v: k for k, v in ROMANIZED_DICTIONARY.items()}

# Phonetic consonants and vowels mapping for rule-based conversion
CONSONANTS_MAP = [
    ("kh", "খ"),
    ("gh", "ঘ"),
    ("ch", "চ"),
    ("jh", "ঝ"),
    ("th", "থ"),
    ("dh", "ধ"),
    ("ph", "ফ"),
    ("bh", "ভ"),
    ("sh", "শ"),
    ("ng", "ঙ"),
    ("k", "ক"),
    ("g", "গ"),
    ("c", "চ"),
    ("j", "জ"),
    ("t", "ত"),
    ("d", "দ"),
    ("n", "ন"),
    ("p", "প"),
    ("b", "ব"),
    ("m", "ম"),
    ("r", "ৰ"),
    ("l", "ল"),
    ("s", "স"),
    ("x", "স"),  # Assamese 'x' sound corresponds to স
    ("h", "হ"),
    ("w", "ৱ"),
    ("v", "ভ"),
    ("y", "য়"),
]

VOWELS_INDEPENDENT = {
    "a": "অ",
    "aa": "আ",
    "i": "ই",
    "ee": "ঈ",
    "u": "উ",
    "oo": "ঊ",
    "ri": "ঋ",
    "e": "এ",
    "ai": "ঐ",
    "o": "অ",
    "au": "ঔ",
}

MATRAS = {
    "aa": "া",
    "a": "",    # inherent vowel
    "i": "ি",
    "ee": "ী",
    "u": "ু",
    "oo": "ূ",
    "e": "ে",
    "ai": "ৈ",
    "o": "ো",
    "au": "ৌ",
}


class AssameseTransliterationEngine:
    """Translates Romanized Assamese to native script and vice versa."""

    def __init__(self):
        self.dictionary = ROMANIZED_DICTIONARY
        self.native_dict = NATIVE_TO_ROMANIZED

    def transliterate_word(self, word: str) -> Optional[str]:
        """Convert a single Romanized word to Assamese script."""
        lower = word.lower().strip()
        if lower in self.dictionary:
            return self.dictionary[lower]
        return None

    def transliterate_query(self, query: str) -> Tuple[str, bool]:
        """
        Transliterate full query if Romanized Assamese is identified.
        Returns (converted_query, was_transliterated).
        """
        words = query.strip().split()
        converted_words = []
        any_converted = False

        for word in words:
            # Preserve punctuation around word
            match = re.match(r"^(\W*)([\w]+)(\W*)$", word)
            if match:
                prefix, core, suffix = match.groups()
                core_lower = core.lower()
                if core_lower in self.dictionary:
                    converted_words.append(f"{prefix}{self.dictionary[core_lower]}{suffix}")
                    any_converted = True
                else:
                    converted_words.append(word)
            else:
                converted_words.append(word)

        if any_converted:
            return " ".join(converted_words), True
        return query, False

    def get_query_expansion_terms(self, word: str) -> List[str]:
        """Returns related terms or alternate spellings (both Latin and Assamese)."""
        lower = word.lower().strip()
        expansions = []

        if lower in self.dictionary:
            native = self.dictionary[lower]
            expansions.append(native)
            # Find sibling romanizations
            for k, v in self.dictionary.items():
                if v == native and k != lower:
                    expansions.append(k)
        elif word in self.native_dict:
            roman = self.native_dict[word]
            expansions.append(roman)

        return expansions
