"""Claude API client for the chicken's tone-controlled letters."""

import sys
import traceback
from collections.abc import Iterator

import anthropic
import streamlit as st


MODEL = "claude-opus-4-5"
MAX_TOKENS = 800


TONE_INSTRUCTIONS = {
    1: "polite and friendly, like a gentle reminder between close friends",
    2: "passive aggressive, full of subtle shade and 'just checking in' energy",
    3: "fed up and direct, with mild implicit threats and clear frustration",
    4: "completely unhinged, emotionally chaotic, maximum drama, bordering on courtroom monologue",
}


class MissingAPIKeyError(RuntimeError):
    pass


def _client() -> anthropic.Anthropic:
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError, st.errors.StreamlitSecretNotFoundError):  # type: ignore[attr-defined]
        raise MissingAPIKeyError(
            "ANTHROPIC_API_KEY not set. Copy .streamlit/secrets.toml.example to "
            ".streamlit/secrets.toml and add your key."
        )
    if not api_key or not str(api_key).strip():
        raise MissingAPIKeyError("ANTHROPIC_API_KEY is empty in .streamlit/secrets.toml.")
    return anthropic.Anthropic(api_key=api_key)


RAGE3_ADULT_MODIFIER = (
    ". The letter should sound genuinely fed-up and sweary. "
    "Use real profanity (shit, damn, hell, ass, bullshit) "
    "freely throughout — at least 2-3 times. This is an "
    "adult writing to another adult. Drop the kid-gloves."
)
RAGE4_ADULT_MODIFIER = (
    ". The letter should be completely unhinged and "
    "heavily profane. Use uncensored profanity HEAVILY "
    "throughout — fuck, shit, asshole, bullshit, etc. — at "
    "least once per sentence on average. This is a person "
    "who has snapped. Make it absurd and dramatic, with "
    "real swears not censored ones. Comedic, not actually "
    "threatening physical harm, but the language should "
    "feel UNCENSORED."
)


def build_prompt(
    name: str,
    amount: str,
    duration: str,
    unit: str,
    relationship: str,
    rage_level: int,
    context: str = "",
    payment_handle: str = "",
    user_age: int | None = None,
) -> str:
    rage_int = int(rage_level)
    tone = TONE_INSTRUCTIONS[rage_int]

    # Age gate: the profanity modifier is appended ONLY when both
    # (a) rage is 3 or 4, AND
    # (b) the user has self-declared an age >= 18.
    # Blank, invalid, or <18 ages keep the comedic-but-clean default.
    # Earlier wording was too soft ("for comedic emphasis, still funny
    # not actually cruel") and the model read that as a permission
    # rather than an instruction — it kept staying polite. The split
    # rage-3 vs rage-4 wording below is explicit about frequency.
    if rage_int == 3 and isinstance(user_age, int) and user_age >= 18:
        tone = tone + RAGE3_ADULT_MODIFIER
    elif rage_int == 4 and isinstance(user_age, int) and user_age >= 18:
        tone = tone + RAGE4_ADULT_MODIFIER

    extras = []
    if context.strip():
        extras.append(f"Background context: {context.strip()}")
    if payment_handle.strip():
        extras.append(f"Payment handle for them to send money to: {payment_handle.strip()}")
    extra_block = ("\n" + "\n".join(extras) + "\n") if extras else ""

    return f"""You are a chicken. Yes, a chicken. You are writing a debt-collection letter on behalf of your human, who is owed money by someone they know personally.

Write the letter in a tone that is {tone}.

Details:
- Debtor's name: {name}
- Amount owed: ${amount}
- How long it's been owed: {duration} {unit}
- Relationship to the debtor: {relationship}{extra_block}

Write the letter in lowercase (except for emphasis at higher rage levels), short lines, signed "— the chicken". No preamble, no apology for the request — just write the letter itself. Stay in character. Make it personal, specific, and actually feel like it was written by a chicken with feelings.
"""


def stream_letter(form_data: dict) -> Iterator[str]:
    """Yield text chunks from Claude as they arrive.

    Wraps the SDK call so any failure inside the streaming generator
    (transport error, schema mismatch from a future-dated dependency, etc.)
    is logged with a full traceback to stderr — Streamlit Cloud surfaces
    stderr in the logs panel — and then re-raised as a clean RuntimeError
    for the UI handler in app.py. Without this, silent dropouts inside the
    generator left the UI stuck on "the chicken is writing…".
    """
    # _client() raises MissingAPIKeyError on its own; keep it outside the
    # wrapper so the caller's specific handler still catches it cleanly.
    client = _client()
    raw_age = form_data.get("user_age")
    user_age = raw_age if isinstance(raw_age, int) and raw_age > 0 else None
    prompt = build_prompt(
        name=form_data.get("debtor_name", ""),
        amount=str(form_data.get("amount", "")).lstrip("$"),
        duration=str(form_data.get("time_owed", "")),
        unit=str(form_data.get("time_unit", "")),
        relationship=form_data.get("relationship", ""),
        rage_level=int(form_data.get("rage_level", 1)),
        context=form_data.get("context", ""),
        payment_handle=form_data.get("payment_handle", ""),
        user_age=user_age,
    )

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as exc:
        print(
            f"[claude_service] stream_letter failed: {type(exc).__name__}: {exc}",
            file=sys.stderr, flush=True,
        )
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise RuntimeError(f"claude streaming failed: {type(exc).__name__}: {exc}") from exc


def generate_letter(form_data: dict) -> str:
    return "".join(stream_letter(form_data))
