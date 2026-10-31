import sys
from pathlib import Path
from ofrenda.facts import load_facts
from ofrenda.page import build_page

SAMPLE_RAMESH = Path(__file__).resolve().parent.parent / "samples" / "ramesh.txt"


def test_build_page_contains_expected_sections():
    facts = [
        "Name: Ramesh Joshi",
        "He was born in 1945 in Pune.",
        "His favourite food was shrikhand.",
    ]
    remembrance = "I remember Ramesh and his shrikhand."
    problems = []
    soft_claims = []
    evidence = []

    page = build_page(facts, remembrance, problems, soft_claims, evidence)

    assert "# Ofrenda for Ramesh Joshi" in page
    assert remembrance in page
    assert "- He was born in 1945 in Pune." in page
    assert "- His favourite food was shrikhand." in page
    assert "Name: Ramesh Joshi" not in page
    assert "Written by an open-weight model (Qwen3-8B via Tinker)." in page
    assert "ofrenda.engine" not in sys.modules


def test_build_page_title_fallback_when_no_name_line():
    facts = [
        "He was born in 1945 in Pune.",
        "His favourite food was shrikhand.",
    ]
    page = build_page(facts, "Remembrance text", [], [], [])
    assert "# Ofrenda for someone remembered" in page
    assert "ofrenda.engine" not in sys.modules


def test_page_never_contains_forbidden_words():
    facts = ["Name: Ramesh Joshi", "He was born in 1945 in Pune."]
    problems = [{"kind": "number", "text": "1950"}]
    soft_claims = ["always"]
    evidence = [
        {
            "sentence": "He was born in 1950.",
            "best_fact": "He was born in 1945 in Pune.",
            "unmatched_words": ["1950"],
        }
    ]
    page = build_page(facts, "He was born in 1950.", problems, soft_claims, evidence)
    assert "verified" not in page.lower()
    assert "safe" not in page.lower()
    assert "accurate" not in page.lower()
    assert "ofrenda.engine" not in sys.modules


def test_samples_ramesh_loads_and_has_8_facts():
    facts = load_facts(str(SAMPLE_RAMESH))
    assert len(facts) == 8


def test_save_run_writes_utf8_file_in_temp_folder(tmp_path):
    facts = ["Name: Ramesh Joshi", "He was born in 1945 in Pune."]
    remembrance = "Remembering Ramesh in Pune."
    page_content = build_page(facts, remembrance, [], [], [])

    out_file = tmp_path / "subfolder" / "ofrenda.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(page_content, encoding="utf-8")

    assert out_file.is_file()
    read_back = out_file.read_text(encoding="utf-8")
    assert read_back == page_content
    assert "ofrenda.engine" not in sys.modules
