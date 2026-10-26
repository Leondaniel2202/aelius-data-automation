"""Pure helpers shared by Aelius automations."""
from urllib.parse import urlencode


def build_form_url(form_url: str, mentee_id: str) -> str:
    query = urlencode({"prefillHide_mentee_id": mentee_id})
    separator = "&" if "?" in form_url else "?"
    return f"{form_url}{separator}{query}"


def normalize_phone_number(phone_number: str) -> str:
    return phone_number.replace("+", "").replace("-", "").replace(" ", "")


def eligible_mentees(rows: list[dict], phone_column: str, id_column: str, sent_column: str) -> list[dict]:
    return [row for row in rows if row.get(phone_column) and row.get(id_column) and not row.get(sent_column)]
