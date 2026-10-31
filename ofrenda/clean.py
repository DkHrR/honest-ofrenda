import re


def clean_output(text: str) -> str:
    """
    Remove closed and unclosed <think> blocks and any token matching <|[^|>]*|>,
    then strip whitespace.
    """
    if not text:
        return ""
    # Remove closed <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Remove unclosed <think>... to end
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)
    # Remove special tokens matching <|...|>
    text = re.sub(r"<\|[^|>]*\|>", "", text)
    return text.strip()
