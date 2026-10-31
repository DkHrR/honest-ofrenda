from typing import Dict, List
from ofrenda.cli import (
    format_checker_result,
    format_evidence_view,
    format_soft_claims,
)


def build_page(
    facts: List[str],
    remembrance: str,
    problems: List[Dict[str, str]],
    soft_claims: List[str],
    evidence: List[Dict],
) -> str:
    """Build a remembrance markdown page from facts, output and review checks."""
    name = None
    for f in facts:
        stripped = f.strip()
        if stripped.lower().startswith("name:"):
            name = stripped.split(":", 1)[1].strip()
            break

    if name:
        title = f"# Ofrenda for {name}"
    else:
        title = "# Ofrenda for someone remembered"

    remembrance_section = remembrance.strip()

    fact_bullets = []
    for f in facts:
        stripped = f.strip()
        if stripped.lower().startswith("name:"):
            continue
        fact_bullets.append(f"- {stripped}")

    what_told = "## What you told me\n" + "\n".join(fact_bullets)

    checks_lines = [
        "## Checks",
        format_checker_result(problems),
        format_soft_claims(soft_claims),
    ]
    checks_section = "\n".join(checks_lines)

    ev_section = format_evidence_view(evidence)

    footer = (
        "Written by an open-weight model (Qwen3-8B via Tinker). "
        "Plain code checks names, numbers and a few soft words only. "
        "Read every line yourself."
    )

    parts = [
        title,
        remembrance_section,
        what_told,
        checks_section,
    ]
    if ev_section:
        parts.append(ev_section)
    parts.append(f"---\n{footer}")

    return "\n\n".join(parts) + "\n"
