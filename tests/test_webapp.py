import re
from pathlib import Path
import threading
import time
import pytest
from ofrenda.checker import find_soft_claims, find_unsupported
from ofrenda.cli import format_checker_result, format_soft_claims
from ofrenda.pipeline import run_all
from ofrenda.webapp import create_app


def test_get_index():
    app = create_app()
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    expected_footer = (
        "Written by an open-weight model (Qwen3-8B via Tinker). "
        "Plain code checks names, numbers and a few soft words only. "
        "Read every line yourself."
    )
    assert expected_footer in res.text


def test_start_without_run_fn_returns_501():
    app = create_app()
    client = app.test_client()
    res = client.post("/start", json={"facts": "Name: Sunanda"})
    assert res.status_code == 501
    assert "not wired yet" in res.text


def test_job_lifecycle_with_stub_run_fn():
    expected_result = {
        "name": "Sunanda",
        "remembrance": "I remember Sunanda.",
        "problems": [],
        "soft_claims": [],
        "evidence": [],
        "checker_line": "Checker: nothing unsupported found",
        "review_line": "Review by hand: no listed soft-claim words found",
    }

    def stub_run(facts_text):
        return expected_result

    app = create_app(run_fn=stub_run)
    client = app.test_client()
    res = client.post("/start", json={"facts": "Name: Sunanda"})
    assert res.status_code == 200
    data = res.get_json()
    assert "id" in data
    job_id = data["id"]

    for _ in range(20):
        s_res = client.get(f"/status/{job_id}")
        assert s_res.status_code == 200
        s_data = s_res.get_json()
        if s_data.get("state") == "done":
            break
        time.sleep(0.05)
    else:
        pytest.fail("Job did not finish in time")

    assert s_data["state"] == "done"
    assert s_data["name"] == "Sunanda"
    assert s_data["remembrance"] == "I remember Sunanda."
    assert s_data["checker_line"] == "Checker: nothing unsupported found"
    assert s_data["review_line"] == "Review by hand: no listed soft-claim words found"


def test_concurrent_start_returns_429():
    release_event = threading.Event()

    def slow_run(facts_text):
        release_event.wait(timeout=2.0)
        return {"name": "Test"}

    app = create_app(run_fn=slow_run)
    client = app.test_client()

    res1 = client.post("/start", json={"facts": "Name: Sunanda"})
    assert res1.status_code == 200

    res2 = client.post("/start", json={"facts": "Name: Ramesh"})
    assert res2.status_code == 429
    data2 = res2.get_json()
    assert "already running" in data2.get("error", "")

    release_event.set()


def test_run_all_validation_limits():
    # 13 facts
    thirteen_facts = "\n".join([f"Fact {i}" for i in range(13)])
    with pytest.raises(ValueError, match="More than 12 facts"):
        run_all(thirteen_facts, lambda facts: "test")

    # line over 200 characters
    long_line = "A" * 201
    with pytest.raises(ValueError, match="exceeds maximum length of 200 characters"):
        run_all(long_line, lambda facts: "test")

    # total length over 2000 characters
    total_long = ("A" * 150 + "\n") * 15
    with pytest.raises(ValueError, match="exceeds maximum length of 2000 characters"):
        run_all(total_long, lambda facts: "test")


def test_run_all_with_second_run_sample():
    sunanda_facts_path = Path("samples/sunanda.txt")
    facts_text = sunanda_facts_path.read_text(encoding="utf-8")

    second_run_path = Path("docs/second_run.txt")
    remembrance_text = second_run_path.read_text(encoding="utf-8").splitlines()[0]

    def stub_write(facts):
        return remembrance_text

    result = run_all(facts_text, stub_write)

    expected_checker = format_checker_result(result["problems"])
    expected_review = format_soft_claims(result["soft_claims"])
    assert result["checker_line"] == expected_checker
    assert result["review_line"] == expected_review
    assert result["checker_line"] == "Checker: nothing unsupported found"
    assert result["review_line"] == "Review by hand (soft claims not in your facts): always"

def test_pipeline_rejects_fewer_than_4_non_name_facts():
    facts_3 = "Name: Someone\nFact one\nFact two\nFact three"
    expected_msg = (
        "Please give at least 4 facts besides the Name line, one per line. "
        "With fewer, the model has nothing to stay inside and adds its own details."
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        run_all(facts_3, lambda facts: "remembrance")


def test_pipeline_accepts_4_non_name_facts():
    facts_4 = "Name: Someone\nFact one\nFact two\nFact three\nFact four"
    result = run_all(facts_4, lambda facts: "I remember someone.")
    assert result["name"] == "Someone"
    assert len(result["facts"]) == 5
    assert result["remembrance"] == "I remember someone."


def test_pipeline_unmatched_and_total_sentences():
    sunanda_text = Path("samples/sunanda.txt").read_text(encoding="utf-8")
    stub_text = "I light a candle. I keep the altar clean."

    result = run_all(sunanda_text, lambda facts: stub_text)
    assert result["total_sentences"] == 2
    assert result["unmatched_sentences"] == 2

