"""
Checker for unsupported names and numbers in a remembrance reply.

Known limits:
- A made-up name at the very start of a sentence is not caught.
- A made-up lowercase word such as a food or a song is not caught.
"""

import re
from typing import Dict, List, Union


def find_unsupported(reply: str, facts: Union[List[str], str]) -> List[Dict[str, str]]:
    """
    Find numbers and capitalized names in reply that are not supported by facts.
    Returns a list of problems, each with kind ("number" or "name") and the text.
    An empty list means nothing unsupported was found (never call it "verified").
    """
    if not reply:
        return []

    if isinstance(facts, list):
        facts_text = "\n".join(facts)
    else:
        facts_text = str(facts)

    problems: List[Dict[str, str]] = []

    # 1. Numbers check:
    # Every number token in the reply (regex \d+(?:[.,]\d+)*) must appear as the
    # same token in the facts text.
    fact_numbers = set(re.findall(r"\d+(?:[.,]\d+)*", facts_text))
    for num in re.findall(r"\d+(?:[.,]\d+)*", reply):
        if num not in fact_numbers:
            problems.append({"kind": "number", "text": num})

    # 2. Names check:
    # Every capitalized word (regex [A-Z][a-zA-Z]+) that is NOT the first word
    # of a sentence and is not "I" must appear in the facts text, case-insensitive.
    # Sentence start = start of text, or after . ! ? or a newline,
    # ignoring leading quotes, asterisks and spaces.
    for m in re.finditer(r"[A-Z][a-zA-Z]+", reply):
        word = m.group(0)
        if word == "I":
            continue

        prefix = reply[: m.start()].rstrip(" \t\r\"'“”‘’*")
        if len(prefix) == 0 or prefix[-1] in ".!?\n":
            # First word of sentence, skip
            continue

        if not re.search(rf"\b{re.escape(word)}\b", facts_text, re.IGNORECASE):
            problems.append({"kind": "name", "text": word})

    return problems


SOFT_WORDS = {
    "always",
    "never",
    "every",
    "smile",
    "smiled",
    "smiling",
    "laugh",
    "laughed",
    "laughter",
    "warm",
    "warmth",
    "kind",
    "kindness",
    "gentle",
    "beautiful",
    "generous",
    "wise",
    "brave",
    "proud",
}


# This is a small word list for human review, not a lie detector.
def find_soft_claims(reply: str, facts: Union[List[str], str]) -> List[str]:
    """
    Find words from SOFT_WORDS appearing in reply that do not appear in facts.
    Whole-word, case-insensitive.
    Returns unique words in order of appearance in reply.
    """
    if not reply:
        return []

    if isinstance(facts, list):
        facts_text = "\n".join(facts)
    else:
        facts_text = str(facts)

    seen = set()
    flagged: List[str] = []

    for m in re.finditer(r"\b[a-zA-Z]+\b", reply):
        word_lower = m.group(0).lower()
        if word_lower in SOFT_WORDS:
            if not re.search(rf"\b{re.escape(word_lower)}\b", facts_text, re.IGNORECASE):
                if word_lower not in seen:
                    seen.add(word_lower)
                    flagged.append(word_lower)

    return flagged

