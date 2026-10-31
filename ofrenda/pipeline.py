from typing import Any, Callable, Dict, List
from ofrenda.checker import find_soft_claims, find_unsupported
from ofrenda.clean import clean_output
from ofrenda.cli import format_checker_result, format_soft_claims
from ofrenda.evidence import build_evidence


def run_all(
    facts_text: str, write_fn: Callable[[List[str]], str]
) -> Dict[str, Any]:
    """
    Run the remembrance pipeline.
    Rejects text over 2000 characters, lines over 200 characters, or > 12 facts.
    Calls write_fn(facts), cleans output, runs checks, and builds evidence view.
    """
    if len(facts_text) > 2000:
        raise ValueError("Facts text exceeds maximum length of 2000 characters")

    lines = facts_text.splitlines()
    facts: List[str] = []
    for line in lines:
        if len(line) > 200:
            raise ValueError("A single line exceeds maximum length of 200 characters")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        facts.append(stripped)

    if len(facts) > 12:
        raise ValueError("More than 12 facts provided")
    if not facts:
        raise ValueError("No facts provided")

    non_name_facts = [f for f in facts if not f.lower().startswith("name:")]
    if len(non_name_facts) < 4:
        raise ValueError(
            "Please give at least 4 facts besides the Name line, one per line. "
            "With fewer, the model has nothing to stay inside and adds its own details."
        )

    name = "someone remembered"
    for f in facts:
        if f.lower().startswith("name:"):
            extracted = f.split(":", 1)[1].strip()
            if extracted:
                name = extracted
            break

    raw_output = write_fn(facts)
    remembrance = clean_output(raw_output)

    problems = find_unsupported(remembrance, facts)
    soft_claims = find_soft_claims(remembrance, facts)
    evidence = build_evidence(remembrance, facts)

    checker_line = format_checker_result(problems)
    review_line = format_soft_claims(soft_claims)

    total_sentences = len(evidence)
    unmatched_sentences = sum(1 for item in evidence if item.get("best_fact") == "none")

    return {
        "name": name,
        "facts": facts,
        "remembrance": remembrance,
        "problems": problems,
        "soft_claims": soft_claims,
        "evidence": evidence,
        "checker_line": checker_line,
        "review_line": review_line,
        "total_sentences": total_sentences,
        "unmatched_sentences": unmatched_sentences,
    }
