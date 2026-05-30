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
# Profanity is appended ONLY when (rage_level in {3, 4}) AND (user_age >= 18).
# All other combinations produce the censored, default-tone prompt.


def test_age_under_18_no_profanity_modifier():
    """Age 17 at rage 4 — none of the explicit-profanity markers present."""
    prompt = _prompt(rage_level=4, user_age=17)
    assert "uncensored" not in prompt
    assert "fuck" not in prompt
    assert "profanity" not in prompt


def test_age_18_plus_rage_4_has_heavy_profanity_modifier():
    """Age 25 at rage 4 — the heavy-profanity instruction is appended."""
    prompt = _prompt(rage_level=4, user_age=25)
    assert "uncensored" in prompt.lower()
    assert "heavily profane" in prompt.lower()
    # The word "fuck" should appear in the instruction itself (the model
    # is told it can use it). Don't depend on output text, just the prompt.
    assert "fuck" in prompt.lower()


def test_age_18_plus_rage_2_unchanged():
    """Adult age must NOT change rage 1/2 — those are spec-locked clean."""
    clean = _prompt(rage_level=2, user_age=None)
    adult = _prompt(rage_level=2, user_age=25)
    assert clean == adult
    assert "uncensored" not in adult
    assert "fuck" not in adult


def test_age_none_treated_as_under_18():
    """Missing age must NOT unlock profanity at rage 4."""
    prompt = _prompt(rage_level=4, user_age=None)
    assert "uncensored" not in prompt
    assert "fuck" not in prompt
    assert "heavily profane" not in prompt.lower()
