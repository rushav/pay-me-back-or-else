"""Tests for utils/validators.validate_form."""

from utils.validators import validate_form


def _valid() -> dict:
    return {
        "debtor_name": "Marcus",
        "amount": "240",
        "time_owed": "3",
        "time_unit": "weeks",
        "relationship": "friend",
        "rage_level": 2,
    }


def test_valid_form_has_no_errors():
    assert validate_form(_valid()) == []


def test_empty_form_reports_all_required_fields():
    errors = validate_form({})
    for field in ("debtor name", "amount", "time owed", "time unit", "relationship"):
        assert any(f"{field} is required" in e for e in errors), (field, errors)


def test_missing_single_required_field_is_flagged():
    form = _valid()
    del form["debtor_name"]
    assert "debtor name is required" in validate_form(form)


def test_zero_amount_rejected():
    form = _valid()
    form["amount"] = "0"
    assert any("greater than zero" in e for e in validate_form(form))


def test_negative_amount_rejected():
    form = _valid()
    form["amount"] = "-5"
    assert any("greater than zero" in e for e in validate_form(form))


def test_non_numeric_amount_rejected():
    form = _valid()
    form["amount"] = "abc"
    assert "amount must be a number" in validate_form(form)


def test_rage_level_above_range_rejected():
    form = _valid()
    form["rage_level"] = 5
    assert "rage level must be between 1 and 4" in validate_form(form)


def test_rage_level_below_range_rejected():
    form = _valid()
    form["rage_level"] = 0
    assert "rage level must be between 1 and 4" in validate_form(form)
