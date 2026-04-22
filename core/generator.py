import anthropic
import streamlit as st

from core.prompts import build_prompt


def generate_letter(
    form_data: dict,
    rage_level: int,
    family_friendly: bool,
    regenerate: bool = False,
) -> str:
    """Call Claude API to generate a debt collection letter. Returns the letter text or an error string."""
    system_msg, user_msg = build_prompt(form_data, rage_level, family_friendly, regenerate)

    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            temperature=0.9,
            system=system_msg,
            messages=[{"role": "user", "content": user_msg}],
            timeout=15.0,
        )
        return message.content[0].text
    except anthropic.APIConnectionError:
        return "ERROR: Could not connect to the AI service. Please check your internet connection and try again."
    except anthropic.APIError as e:
        return f"ERROR: The AI service returned an error. Please try again. ({e.message})"
    except Exception:
        return "ERROR: Something unexpected went wrong. Please try again."
