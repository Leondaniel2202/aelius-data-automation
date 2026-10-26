"""SeaTable form URL helpers."""
import json
from urllib.parse import urlencode


def build_form_url(form_url: str, mentee_id: str) -> str:
    query = urlencode({"prefillHide_mentee_id": mentee_id})
    return f"{form_url}{'&' if '?' in form_url else '?'}{query}"


def get_form_url(forms: list[dict], form_name: str) -> str:
    for form in forms:
        if json.loads(form["form_config"]).get("form_name") == form_name:
            return form["form_link"]
    raise ValueError(f"Form {form_name!r} not found")
