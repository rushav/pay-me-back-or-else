import anthropic
import streamlit as st


class LetterGenerationError(Exception):
    """Raised when the Claude API call fails."""
    pass


TONE_INSTRUCTIONS = {
    1: (
        "Polite, warm, giving full benefit of the doubt. Friendly reminder energy."
    ),
    2: (
        "Passive aggressive. Dripping with subtle shade. Lots of 'just checking in' "
        "and 'no worries if you forgot'. The reader should feel the tension."
    ),
    3: (
        "Direct and firm. Clearly annoyed. No more pleasantries. Mild implicit "
        "pressure. Not rude, just done being patient."
    ),
    4: (
        "Fully unhinged. Emotionally chaotic. Heavy guilt-trip. Dramatic. "
        "Bordering on courtroom monologue. Maximum entertainment value."
    ),
}

SYSTEM_PROMPT = (
    "You are a letter-writing assistant specializing in debt collection "
    "letters that are funny, personal, and actually readable. Write only "
    "the letter body — no subject line, no metadata, no commentary. "
    "The letter should be 150–300 words."
)


def generate_letter(
    name: str,
    amount: float,
    duration_str: str,
    relationship: str,
    rage_level: int,
    regenerate: bool = False,
) -> str:
    """Call Claude API to generate a debt collection letter."""
    user_prompt = f"""Write a debt collection letter with these details:
- Debtor's name: {name}
- Amount owed: ${amount:.2f}
- How long it has been: {duration_str}
- My relationship to them: {relationship}
- Rage level: {rage_level} out of 4

Tone instructions for rage level {rage_level}:
{TONE_INSTRUCTIONS[rage_level]}

Use {name}'s name and the specific dollar amount in the letter. Make it feel personal, not generic.
{"Write a completely different version than any previous letter." if regenerate else ""}"""

    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-opus-4-5-20250514",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
    except Exception as e:
        raise LetterGenerationError(str(e)) from e
