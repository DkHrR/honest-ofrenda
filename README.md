# honest-ofrenda

## What it is
honest-ofrenda is a tool that turns biographical facts about a remembered person into a short remembrance for an ofrenda. The open-weight language model writes the wording, while deterministic code checks that the draft introduces no names or numbers absent from the provided facts.

## Run it
Install dependencies:
```bash
pip install -r requirements.txt
```

Set your Tinker key in `.env`:
```bash
API_KEY=your_api_key_here
MODEL=Qwen/Qwen3-8B
```

Run the tool:
```bash
python -m ofrenda.cli samples/sunanda.txt --save out/sunanda.md
```

## Use it for someone you remember
Copy `samples/template.txt` into a folder named `my_facts/` (which is git-ignored), and fill in 6 to 8 facts about the person.
Run the tool:
```bash
python -m ofrenda.cli my_facts/yourfile.txt --save out/yourfile.md
```
Read every sentence yourself, and compare it with your facts because the checks catch only some changes. Note that your facts are sent to the Tinker hosted API. The tool has been run only on the two made-up samples, not on a real family's facts.

## How the checks work
- **Model generation**: An open-weight model (Qwen3-8B via Tinker) writes a warm first-person remembrance strictly constrained to the facts.
- **Name and number check**: Plain code inspects the reply. Every number token and non-sentence-starting capitalized word must appear in the facts.
- **Soft-word list**: A review list flags emotional and superlative words (such as "always" or "warmth") for human inspection.
- **Evidence view**: Each sentence is mapped to the closest matching fact, highlighting words found in no fact.

## Known limits
- A made-up name at the start of a sentence is not caught.
- A made-up lowercase word such as a food or song is not caught.
- Small drift like "loved making puran poli" when the fact says "favourite food" is not caught.
- The evidence view has false alarms (for example grammatical variants like "selling" vs "sold").
- One real run took 46.00 s including a cold start and is not a benchmark.

## Data note
The facts are sent to the Tinker hosted API, so do not use this for anything you would not send to a hosted service. The sample files represent made-up people.

## License
MIT
