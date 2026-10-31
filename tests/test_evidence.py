import re
import sys
from pathlib import Path
from ofrenda.clean import clean_output
from ofrenda.cli import format_evidence_view
from ofrenda.evidence import build_evidence
from ofrenda.facts import load_facts

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "samples" / "sunanda.txt"
FIRST_RUN_PATH = Path(__file__).resolve().parent.parent / "docs" / "first_run.txt"


def test_sentence_fully_made_of_fact_words_gives_empty_unmatched_words():
    facts = ["She was born in 1948 in Nashik."]
    items = build_evidence("She was born in 1948 in Nashik.", facts)
    assert len(items) == 1
    assert items[0]["unmatched_words"] == []
    assert "ofrenda.engine" not in sys.modules


def test_loved_and_making_appear_in_unmatched_words():
    facts = load_facts(str(SAMPLE_PATH))
    sentence = (
        "She loved making puran poli and hummed old film songs while she cooked."
    )
    items = build_evidence(sentence, facts)
    assert len(items) == 1
    assert "loved" in items[0]["unmatched_words"]
    assert "making" in items[0]["unmatched_words"]
    assert "ofrenda.engine" not in sys.modules


def test_best_fact_for_31_years_sentence_contains_31_years():
    facts = load_facts(str(SAMPLE_PATH))
    sentence = "I remember Aaji selling bangles at the market for 31 years."
    items = build_evidence(sentence, facts)
    assert len(items) == 1
    assert "31 years" in items[0]["best_fact"]
    assert "ofrenda.engine" not in sys.modules


def test_sentence_with_no_shared_words_gives_best_fact_none():
    facts = ["She was born in 1948."]
    sentence = "Zebras gallop across distant plains."
    items = build_evidence(sentence, facts)
    assert len(items) == 1
    assert items[0]["best_fact"] == "none"
    assert "ofrenda.engine" not in sys.modules


def test_docs_first_run_after_clean_output_gives_one_item_per_sentence():
    facts = load_facts(str(SAMPLE_PATH))
    text = FIRST_RUN_PATH.read_text(encoding="utf-8")
    cleaned = clean_output(text)
    items = build_evidence(cleaned, facts)
    expected_sentences = [
        s.strip() for s in re.split(r"[.!?\r\n]+", cleaned) if s.strip()
    ]
    assert len(items) == len(expected_sentences)
    assert len(items) > 0
    assert "ofrenda.engine" not in sys.modules


def test_format_evidence_view_empty_list():
    res = format_evidence_view([])
    assert res == ""
    assert "verified" not in res.lower()
    assert "safe" not in res.lower()
    assert "accurate" not in res.lower()
    assert "ofrenda.engine" not in sys.modules
