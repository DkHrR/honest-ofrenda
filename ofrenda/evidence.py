"""
Evidence view for human review of a remembrance against facts.

Comment:
This is a review aid with false alarms (for example "selling" vs "sold");
it does not prove anything.
"""

import re
from typing import Dict, List, Union

STOPLIST = {
    "the",
    "and",
    "she",
    "her",
    "was",
    "for",
    "with",
    "while",
    "that",
    "from",
    "his",
    "its",
    "our",
    "who",
    "they",
    "them",
    "had",
    "has",
    "are",
    "you",
    "but",
    "not",
    "all",
    "one",
    "my",
    "me",
    "to",
    "of",
    "in",
    "at",
    "on",
    "it",
    "is",
    "as",
    "be",
    "by",
    "an",
    "a",
    "i",
}


def _extract_content_words(text: str) -> List[str]:
    """
    Extract content words: lowercase alphabetic words of 3+ letters not in STOPLIST,
    and number tokens.
    """
    tokens = re.findall(r"\d+(?:[.,]\d+)*|[a-zA-Z]+", text)
    content_words: List[str] = []
    for token in tokens:
        if re.match(r"^\d+(?:[.,]\d+)*$", token):
            content_words.append(token)
        else:
            w = token.lower()
            if len(w) >= 3 and w not in STOPLIST:
                content_words.append(w)
    return content_words


def build_evidence(
    reply: str, facts: Union[List[str], str]
) -> List[Dict[str, Union[str, List[str]]]]:
    """
    Build evidence list for each sentence in reply.
    Splits on . ! ? and newlines, skipping empty sentences.
    Each item contains:
    - sentence: stripped sentence text
    - best_fact: fact sharing the most content words (or "none" if 0 shared)
    - unmatched_words: content words in sentence appearing in no fact (lowercase, unique, in order)
    """
    if not reply:
        return []

    if isinstance(facts, list):
        fact_lines = [f.strip() for f in facts if f.strip()]
    else:
        fact_lines = [f.strip() for f in facts.splitlines() if f.strip()]

    # Extract all content words across all facts for quick membership lookup
    all_fact_content_words = set()
    fact_words_list: List[set] = []
    for f in fact_lines:
        words = set(_extract_content_words(f))
        fact_words_list.append(words)
        all_fact_content_words.update(words)

    # Split reply on . ! ? and newlines, skip empty
    raw_sentences = [s.strip() for s in re.split(r"[.!?\r\n]+", reply) if s.strip()]

    evidence = []
    for s in raw_sentences:
        s_words = _extract_content_words(s)
        s_words_set = set(s_words)

        # Unmatched content words: in sentence, in no fact, unique, in order
        seen = set()
        unmatched = []
        for w in s_words:
            if w not in all_fact_content_words and w not in seen:
                seen.add(w)
                unmatched.append(w)

        # Find best fact (most shared content words)
        best_fact = "none"
        max_shared = 0
        for fact_text, f_set in zip(fact_lines, fact_words_list):
            shared_count = len(s_words_set & f_set)
            if shared_count > max_shared:
                max_shared = shared_count
                best_fact = fact_text

        evidence.append(
            {
                "sentence": s,
                "best_fact": best_fact,
                "unmatched_words": unmatched,
            }
        )

    return evidence
