"""Tests for services/claude_service.build_prompt — a pure function.

No Anthropic API client is constructed and no network call is made; only the
prompt-construction logic is exercised.
"""

from services.claude_service import build_prompt


def _prompt(**overrides) -> str:
    args = dict(
        name="Marcus",
        amount="240",
        duration="3",
        unit="weeks",
        relationship="friend",
        rage_level=1,
        context="brunch, again",
        payment_handle="@marcus",
    )
    args.update(overrides)
    return build_prompt(**args)


def test_prompt_includes_form_details():
    prompt = _prompt()
    assert "Marcus" in prompt          # debtor name
    assert "240" in prompt             # amount
    assert "brunch, again" in prompt   # context


def test_tone_differs_between_rage_1_and_4():
    assert _prompt(rage_level=1) != _prompt(rage_level=4)


def test_all_rage_levels_produce_nonempty_prompt():
    for level in (1, 2, 3, 4):
        prompt = _prompt(rage_level=level)
        assert isinstance(prompt, str)
        assert prompt.strip()


# ── Age gate ──────────────────────────────────────────────────
#
# Profanity is allowed ONLY when (rage_level in {3, 4}) AND (user_age >= 18).
# All other combinations produce the censored, default-tone prompt.

PROFANITY_MARKER = "profanity allowed"


def test_age_none_keeps_prompt_clean_at_high_rage():
    """Missing age is treated as under-18 — no profanity modifier."""
    for rage in (3, 4):
        prompt = _prompt(rage_level=rage, user_age=None)
        assert PROFANITY_MARKER not in prompt


def test_age_under_18_keeps_prompt_clean_at_high_rage():
    """A user age below 18 must NOT unlock profanity, even at rage 4."""
    for rage in (3, 4):
        prompt = _prompt(rage_level=rage, user_age=17)
        assert PROFANITY_MARKER not in prompt


def test_age_18_plus_unlocks_profanity_at_rage_3_and_4():
    """rage 3 and rage 4 with adult age include the uncensored modifier."""
    for rage in (3, 4):
        prompt = _prompt(rage_level=rage, user_age=25)
        assert PROFANITY_MARKER in prompt


def test_age_18_plus_does_not_change_low_rage():
    """Even with an adult age, rage 1 and 2 stay unchanged."""
    for rage in (1, 2):
        clean = _prompt(rage_level=rage, user_age=None)
        adult = _prompt(rage_level=rage, user_age=25)
        assert clean == adult
        assert PROFANITY_MARKER not in adult
