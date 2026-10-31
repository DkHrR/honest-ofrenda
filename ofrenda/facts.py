from pathlib import Path
from typing import List


def load_facts(path: str) -> List[str]:
    """
    Load facts from a file. Skip blank lines and lines starting with '#'.
    Raises FileNotFoundError if the file is missing.
    Raises ValueError if the file has no facts.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Facts file not found: {path}")

    with p.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    facts = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        facts.append(stripped)

    if not facts:
        raise ValueError(f"No facts found in file: {path}")

    return facts
