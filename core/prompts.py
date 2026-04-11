"""Prompt templates for rage-level debt collection letters."""

TONE_INSTRUCTIONS = {
    1: (
        "Write a warm, polite letter. Give them the benefit of the doubt. "
        "Use phrases like 'I'm sure you just forgot' and 'whenever you get a chance.' "
        "Keep it lighthearted and friendly."
    ),
    2: (
        "Write a passive-aggressive letter. Subtle shade. Use phrases like "
        "'just circling back' and 'I'm sure you've been busy.' Hint that you're "
        "keeping track. Add a backhanded compliment."
    ),
    3: (
        "Write a firmly annoyed letter. Be direct. No more excuses. Use phrases "
        "like 'this is getting ridiculous' and 'I shouldn't have to ask again.' "
        "Make it clear you're fed up but still civilized."
    ),
    4: (
        "Write an over-the-top dramatic letter. Full theatrical performance. "
        "Reference fictional court proceedings, invoke imaginary witnesses, "
        "threaten to tell their grandmother. Make it absurdly funny and "
        "emotionally devastating. Use dramatic flourishes and rhetorical questions. "
        "This is a comedy monologue disguised as a letter."
    ),
}

RAGE_LABELS = {
    1: ("Gentle Nudge", "Polite, warm, benefit of the doubt"),
    2: ("Passive Aggressive", "Subtle shade, 'just checking in' energy"),
    3: ("Fed Up", "Direct, firm, clearly annoyed"),
    4: ("Full Drama", "Emotional, dramatic, heavy guilt-trip"),
}

SYSTEM_MESSAGE = (
    "You are a comedic letter writer who specializes in funny, creative debt "
    "collection letters. Your letters are humorous and entertaining — never "
    "genuinely threatening or legally actionable. You write with personality, "
    "wit, and flair. Never include anything that could be construed as a real "
    "legal threat. Keep the tone fun and cathartic."
)


def build_prompt(form_data: dict, rage_level: int, regenerate: bool = False) -> str:
    """Build the user message for Claude based on form data and rage level.

    Args:
        form_data: Dict with keys debtor_name, amount, duration, relationship,
                   context, venmo_handle.
        rage_level: Integer 1-4.
        regenerate: If True, instruct Claude to write a completely different version.

    Returns:
        The user message string to send to Claude.
    """
    label, description = RAGE_LABELS[rage_level]
    tone = TONE_INSTRUCTIONS[rage_level]

    parts = [
        f"Write a debt collection letter addressed to {form_data['debtor_name']}.",
        f"They owe me ${form_data['amount']:.2f}.",
        f"They've owed me for {form_data['duration']}.",
        f"Our relationship: {form_data['relationship']}.",
    ]

    if form_data.get("context"):
        parts.append(f"Here's what happened: {form_data['context']}")

    if form_data.get("venmo_handle"):
        parts.append(
            f"My payment handle is {form_data['venmo_handle']}. "
            "Weave this payment info naturally into the letter so they know "
            "exactly where to send the money."
        )

    parts.append(f"\nRage Level: {rage_level}/4 — {label} ({description})")
    parts.append(f"\nTone instructions: {tone}")
    parts.append(
        "\nThe letter should be 150-300 words. Address the debtor by name. "
        "Be creative and funny. Do NOT include any real legal threats."
    )

    if regenerate:
        parts.append(
            "\nIMPORTANT: Write a completely different version from the last one. "
            "Different opening, different structure, different jokes."
        )

    return "\n".join(parts)
