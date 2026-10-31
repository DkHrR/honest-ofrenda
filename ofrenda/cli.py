import sys
from typing import Dict, List, Optional
from ofrenda.checker import find_soft_claims, find_unsupported
from ofrenda.evidence import build_evidence
from ofrenda.facts import load_facts


def format_checker_result(problems: List[Dict[str, str]]) -> str:
    """
    Format checker results for display.
    Never uses words 'verified', 'safe' or 'accurate'.
    """
    if not problems:
        return "Checker: nothing unsupported found"
    lines = ["Checker: FLAGGED"]
    for p in problems:
        lines.append(f"- {p['kind']}: {p['text']}")
    return "\n".join(lines)


def format_soft_claims(soft_claims: List[str]) -> str:
    """
    Format soft claims for human review.
    Never uses words 'verified', 'safe' or 'accurate'.
    """
    if soft_claims:
        return f"Review by hand (soft claims not in your facts): {', '.join(soft_claims)}"
    return "Review by hand: no listed soft-claim words found"


def format_evidence_view(evidence: List[Dict]) -> str:
    """
    Format evidence view for human review.
    Never uses words 'verified', 'safe' or 'accurate'.
    """
    if not evidence:
        return ""
    lines = ["Evidence view (for review by hand):"]
    for item in evidence:
        words_str = ", ".join(item["unmatched_words"]) if item["unmatched_words"] else "none"
        lines.append(
            f"- {item['sentence']} | closest fact: {item['best_fact']} | words in no fact: {words_str}"
        )
    return "\n".join(lines)



def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("Usage: python -m ofrenda.cli <path-to-facts> [--save <out-path>]")
        sys.exit(1)

    save_path: Optional[str] = None
    facts_path: Optional[str] = None
    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg == "--save":
            if idx + 1 < len(argv):
                save_path = argv[idx + 1]
                idx += 2
                continue
            else:
                print("Error: --save requires a path")
                sys.exit(1)
        elif not facts_path:
            facts_path = arg
            idx += 1
        else:
            idx += 1

    if not facts_path:
        print("Usage: python -m ofrenda.cli <path-to-facts> [--save <out-path>]")
        sys.exit(1)

    facts = load_facts(facts_path)

    # Lazy import to avoid importing engine when testing formatting functions
    from ofrenda.engine import write_remembrance

    remembrance = write_remembrance(facts)
    print(remembrance)
    print()

    problems = find_unsupported(remembrance, facts)
    print(format_checker_result(problems))

    soft_claims = find_soft_claims(remembrance, facts)
    print(format_soft_claims(soft_claims))

    evidence = build_evidence(remembrance, facts)
    ev_view = format_evidence_view(evidence)
    if ev_view:
        print()
        print(ev_view)

    if save_path:
        from pathlib import Path
        from ofrenda.page import build_page

        page_content = build_page(facts, remembrance, problems, soft_claims, evidence)
        out_p = Path(save_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(page_content, encoding="utf-8")
        print(f"Saved: {save_path}")


if __name__ == "__main__":
    main()
