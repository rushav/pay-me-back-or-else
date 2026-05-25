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
