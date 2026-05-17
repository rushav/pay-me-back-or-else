"""Form input validation for the demand worksheet."""


REQUIRED_FIELDS = ("debtor_name", "amount", "time_owed", "time_unit", "relationship")


def validate_form(form_data: dict) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_FIELDS:
        if not str(form_data.get(key, "")).strip():
            errors.append(f"{key.replace('_', ' ')} is required")

    raw_amount = str(form_data.get("amount", "")).strip().lstrip("$")
    if raw_amount:
        try:
            amount = float(raw_amount)
            if amount <= 0:
                errors.append("amount must be greater than zero")
        except ValueError:
            errors.append("amount must be a number")

    raw_time = str(form_data.get("time_owed", "")).strip()
    if raw_time:
        try:
            n = float(raw_time)
            if n <= 0:
                errors.append("time owed must be greater than zero")
        except ValueError:
            errors.append("time owed must be a number")

    rage = form_data.get("rage_level")
    if rage is not None:
        try:
            if int(rage) not in (1, 2, 3, 4):
                errors.append("rage level must be between 1 and 4")
        except (TypeError, ValueError):
            errors.append("rage level must be between 1 and 4")

    return errors
