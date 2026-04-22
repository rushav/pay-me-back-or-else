RELATIONSHIP_TONES: dict[str, str] = {
    "Best Friend": (
        "They're your best friend so tease them mercilessly. Inside joke energy. "
        "'I can't believe you of all people...' Make it funny because you actually love them."
    ),
    "Roommate": (
        "Mention shared living situations. 'I see you every day and you still haven't paid me.' "
        "Reference the fridge, the couch, the bathroom."
    ),
    "Family": (
        "Family guilt is the strongest weapon. Invoke parents, grandparents, holiday dinners. "
        "'What would grandma think?'"
    ),
    "Co-worker": (
        "Corporate passive-aggression. CC fictional managers. Reference 'per my last email' energy. "
        "Mention the break room."
    ),
    "Ex-Boyfriend": (
        "Be RUTHLESS. This is revenge energy. Reference the breakup. "
        "'You took my heart AND my money.' Maximum pettiness."
    ),
    "Ex-Girlfriend": (
        "Be RUTHLESS. This is revenge energy. Reference the breakup. "
        "'You took my heart AND my money.' Maximum pettiness."
    ),
    "Acquaintance": (
        "Awkward formality. 'We barely know each other and yet here I am, writing you a letter about $47.'"
    ),
    "Frenemy": (
        "Backhanded compliments and plausible deniability. "
        "'I'm sure someone as successful as you just forgot...'"
    ),
}

RAGE_TONES: dict[int, str] = {
    1: (
        "Write an angelic, sweet, almost apologetic letter. 'I hate to even bring this up...' "
        "Kill them with kindness. Add a blessing at the end."
    ),
    2: (
        "Write a passive-aggressive letter. Subtle shade. 'Just checking in!' energy. "
        "Track how many times you've asked. Backhanded compliments."
    ),
    3: (
        "Write a clearly angry letter. No more nice. 'This is getting ridiculous.' "
        "Be direct and confrontational but still funny."
    ),
    4: (
        "Write an UNHINGED, over-the-top dramatic letter. Invoke fictional courts, imaginary witnesses, "
        "threaten to tell their grandmother AND their ancestors. Full theatrical chaos. "
        "Dramatic monologue energy. If profanity is allowed, use it liberally."
    ),
}


def build_prompt(
    form_data: dict,
    rage_level: int,
    family_friendly: bool,
    regenerate: bool = False,
) -> tuple[str, str]:
    """Build system and user messages for the Claude API call."""
    if family_friendly:
        ff_instruction = (
            "Keep the language completely clean -- no profanity, no vulgar words, "
            "no sexual references. PG-rated only."
        )
    else:
        ff_instruction = (
            "You can use profanity, crude humor, and vulgar language freely. "
            "R-rated is fine. Go wild."
        )

    system_message = (
        "You are a comedic letter writer who specializes in funny, over-the-top "
        "debt collection letters. You write like a dramatic friend helping someone "
        "get their money back. Your letters should be entertaining, shareable, and "
        f"make people laugh. {ff_instruction}"
    )

    relationship = form_data.get("relationship", "Acquaintance")
    rel_tone = RELATIONSHIP_TONES.get(relationship, RELATIONSHIP_TONES["Acquaintance"])
    rage_tone = RAGE_TONES[rage_level]

    payment_line = ""
    handle = form_data.get("payment_handle", "")
    if handle:
        payment_line = f"\n- Payment handle (weave naturally into the letter): {handle}"

    context_line = ""
    context = form_data.get("context", "")
    if context:
        context_line = f"\n- What happened: {context}"

    regen_line = ""
    if regenerate:
        regen_line = "\n\nWrite a completely different version. Different opening, structure, and jokes."

    user_message = f"""Write a debt collection letter with these details:
- Debtor's name: {form_data['name']}
- Amount owed: ${form_data['amount']:.2f}
- How long they've owed: {form_data['duration_str']}
- Relationship: {relationship}{context_line}{payment_line}

Relationship tone: {rel_tone}

Rage level {rage_level}/4 tone: {rage_tone}

Rules:
- 150-300 words
- Address {form_data['name']} by name
- NEVER include anything that could be a real legal threat{regen_line}"""

    return system_message, user_message
