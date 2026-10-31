from pathlib import Path
import pytest
from ofrenda.checker import find_soft_claims, find_unsupported
from ofrenda.facts import load_facts

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "samples" / "sunanda.txt"


@pytest.fixture
def sunanda_facts():
    return load_facts(str(SAMPLE_PATH))


def test_reply_using_only_facts_passes(sunanda_facts):
    reply = "She was born in 1948 in Nashik. For 31 years she worked at the market."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == []


def test_invented_year_caught(sunanda_facts):
    reply = "She was born in 1950 in Nashik."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == [{"kind": "number", "text": "1950"}]


def test_invented_number_caught(sunanda_facts):
    reply = "She sold bangles for 40 years."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == [{"kind": "number", "text": "40"}]


def test_correct_31_passes(sunanda_facts):
    reply = "She spent 31 years selling bangles."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == []


def test_invented_name_caught(sunanda_facts):
    reply = "Her sister was Priya."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == [{"kind": "name", "text": "Priya"}]


def test_sentence_start_word_skipped(sunanda_facts):
    # Made-up name at the very start of a sentence is skipped
    reply = "Priya was born in 1948 in Nashik. Also she cooked."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == []


def test_number_followed_by_full_stop_handled(sunanda_facts):
    reply = "She was born in 1948. She left in 1971."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == []


def test_case_insensitive_name_match(sunanda_facts):
    reply = "Remembering Kulkarni who lived in Nashik."
    problems = find_unsupported(reply, sunanda_facts)
    assert problems == []


def test_empty_reply_returns_empty_list(sunanda_facts):
    assert find_unsupported("", sunanda_facts) == []
    assert find_unsupported(None, sunanda_facts) == []


def test_facts_loader_skips_comments_and_blanks(tmp_path):
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text(
        "# Heading\n\nFact 1\n   \n# Another comment\nFact 2\n",
        encoding="utf-8",
    )
    facts = load_facts(str(dummy_file))
    assert facts == ["Fact 1", "Fact 2"]


def test_loader_errors_on_missing_file_and_empty_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_facts(str(tmp_path / "does_not_exist.txt"))

    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("# only comments\n   \n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_facts(str(empty_file))


def test_real_sunanda_facts_loads_and_has_8_facts():
    facts = load_facts(str(SAMPLE_PATH))
    assert len(facts) == 8


def test_find_soft_claims_flags_words_in_first_run(sunanda_facts):
    first_run_path = Path(__file__).resolve().parent.parent / "docs" / "first_run.txt"
    first_run_text = first_run_path.read_text(encoding="utf-8")
    flagged = find_soft_claims(first_run_text, sunanda_facts)
    assert set(flagged) == {"smiled", "warmth", "always", "every"}


def test_find_soft_claims_does_not_flag_words_in_facts():
    facts = ["She was a warm and wise person."]
    reply = "She was warm and wise."
    assert find_soft_claims(reply, facts) == []


def test_find_soft_claims_whole_word_only(sunanda_facts):
    reply = "She lived in alwaysland."
    assert find_soft_claims(reply, sunanda_facts) == []

