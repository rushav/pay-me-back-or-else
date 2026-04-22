def validate_form(name: str, amount: float, duration: int) -> dict[str, str]:
    """Validate form inputs. Returns a dict of field_name -> error_message for any failures."""
    errors = {}

    if not name or not name.strip():
        errors["name"] = "Debtor's name cannot be empty."

    if amount is None or amount <= 0:
        errors["amount"] = "Amount must be greater than $0.00."

    if duration is None or duration < 1:
        errors["duration"] = "Duration must be at least 1."

    return errors
