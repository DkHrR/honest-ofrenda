import sys
from ofrenda.cli import format_checker_result, format_soft_claims


def test_cli_format_empty_problems():
    result = format_checker_result([])
    assert result == "Checker: nothing unsupported found"
    assert "verified" not in result.lower()
    assert "safe" not in result.lower()
    assert "accurate" not in result.lower()
    assert "ofrenda.engine" not in sys.modules


def test_cli_format_flagged_problems():
    problems = [
        {"kind": "number", "text": "40"},
        {"kind": "name", "text": "Priya"},
    ]
    result = format_checker_result(problems)
    assert result == "Checker: FLAGGED\n- number: 40\n- name: Priya"
    assert "verified" not in result.lower()
    assert "safe" not in result.lower()
    assert "accurate" not in result.lower()
    assert "ofrenda.engine" not in sys.modules


def test_cli_format_empty_soft_claims():
    result = format_soft_claims([])
    assert result == "Review by hand: no listed soft-claim words found"
    assert "verified" not in result.lower()
    assert "safe" not in result.lower()
    assert "accurate" not in result.lower()
    assert "ofrenda.engine" not in sys.modules


def test_cli_format_non_empty_soft_claims():
    result = format_soft_claims(["smiled", "warmth"])
    assert result == "Review by hand (soft claims not in your facts): smiled, warmth"
    assert "verified" not in result.lower()
    assert "safe" not in result.lower()
    assert "accurate" not in result.lower()
    assert "ofrenda.engine" not in sys.modules

