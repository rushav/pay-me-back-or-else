"""Claude API integration for letter generation."""

import anthropic

from core.prompts import SYSTEM_MESSAGE, build_prompt


def generate_letter(form_data: dict, rage_level: int, regenerate: bool = False) -> str:
    """Generate a debt collection letter using the Claude API.

    Args:
        form_data: Dict with debtor info from the form.
        rage_level: Integer 1-4.
        regenerate: If True, request a different version.

    Returns:
        The generated letter text, or an error message string on failure.
    """
    try:
        client = anthropic.Anthropic()
        user_message = build_prompt(form_data, rage_level, regenerate)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            temperature=0.9,
            system=SYSTEM_MESSAGE,
            messages=[{"role": "user", "content": user_message}],
        )

        return response.content[0].text

    except anthropic.APIConnectionError:
        return (
            "Oops! Couldn't connect to the letter-writing bureau. "
            "Check your internet connection and try again."
        )
    except anthropic.RateLimitError:
        return (
            "Whoa, too many letters at once! The letter-writing bureau is "
            "overwhelmed. Wait a moment and try again."
        )
    except anthropic.APIError as e:
        return (
            f"The letter-writing bureau ran into a problem: {e.message}. "
            "Try again in a moment."
        )
