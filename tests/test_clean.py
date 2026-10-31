from ofrenda.clean import clean_output


def test_clean_output_removes_im_end():
    text = "Remembering Sunanda.<|im_end|>"
    assert clean_output(text) == "Remembering Sunanda."


def test_clean_output_removes_closed_and_unclosed_think_blocks():
    # Closed think block
    text_closed = "<think>internal reasoning</think>Warm remembrance."
    assert clean_output(text_closed) == "Warm remembrance."

    # Unclosed think block
    text_unclosed = "<think>internal reasoning that never closes..."
    assert clean_output(text_unclosed) == ""

    # Both closed and unclosed
    text_both = "<think>part 1</think>Keep this.<think>cut this off"
    assert clean_output(text_both) == "Keep this."


def test_clean_output_leaves_normal_text_unchanged():
    text = "Plain remembrance with no tokens or think tags."
    assert clean_output(text) == text
