import os
from datetime import datetime
from urllib.parse import urlencode

import requests
from seatable_api import Base, context


# ============================================================
# Constants
# ============================================================

MENTEES_TABLE = "Mentees"

MENTEE_ID_COLUMN = "Mentee-ID"
FIRST_NAME_COLUMN = "Vorname"
PHONE_COLUMN = "Telefonnummer"
SENT_COLUMN = "Zwischenbericht verschickt"
SENT_AT_COLUMN = "Zwischenbericht versendet am"

FORM_URL = "https://cloud.seatable.io/dtable/forms/396ef8a7-d532-4ebf-aa04-1efc8657651f/"

META_GRAPH_API = "https://graph.facebook.com/v23.0"
WHATSAPP_TEMPLATE_NAME = "zwischenbericht_template"
WHATSAPP_TEMPLATE_LANGUAGE = "de"

# For SeaTable Cloud, set these directly in the script for now.
WHATSAPP_TOKEN = "REPLACE_ME"
WHATSAPP_PHONE_NUMBER_ID = "REPLACE_ME"


# ============================================================
# SeaTable
# ============================================================


def get_base() -> Base:
    base = Base(context.api_token, context.server_url)
    base.auth()
    return base



def build_form_url(form_url: str, mentee_id: str) -> str:
    query = urlencode({"prefillHide_mentee_id": mentee_id})
    separator = "&" if "?" in form_url else "?"
    return f"{form_url}{separator}{query}"



def get_mentees_to_send(base: Base) -> list[dict]:
    rows = base.list_rows(MENTEES_TABLE)

    return [
        row
        for row in rows
        if row.get(PHONE_COLUMN)
        and row.get(MENTEE_ID_COLUMN)
        and not row.get(SENT_COLUMN)
    ]



def mark_as_sent(base: Base, mentee: dict) -> None:
    base.update_row(
        MENTEES_TABLE,
        mentee["_id"],
        {
            SENT_COLUMN: True,
            SENT_AT_COLUMN: datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    )


# ============================================================
# WhatsApp
# ============================================================


def normalize_phone_number(phone_number: str) -> str:
    return (
        phone_number
        .replace("+", "")
        .replace("-", "")
        .replace(" ", "")
    )



def send_whatsapp_message(
    phone_number: str,
    first_name: str,
    form_url: str,
) -> None:
    response = requests.post(
        f"{META_GRAPH_API}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
        headers={
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "to": normalize_phone_number(phone_number),
            "type": "template",
            "template": {
                "name": WHATSAPP_TEMPLATE_NAME,
                "language": {"code": WHATSAPP_TEMPLATE_LANGUAGE},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": first_name},
                            {"type": "text", "text": form_url},
                        ],
                    }
                ],
            },
        },
    )

    response.raise_for_status()


# ============================================================
# Main
# ============================================================


def main() -> None:
    base = get_base()

    mentees = get_mentees_to_send(base)

    print(f"{len(mentees)} Mentees found")

    for mentee in mentees:
        mentee_id = mentee[MENTEE_ID_COLUMN]
        first_name = mentee.get(FIRST_NAME_COLUMN) or ""
        phone_number = mentee[PHONE_COLUMN]

        personalized_url = build_form_url(FORM_URL, mentee_id)

        send_whatsapp_message(
            phone_number=phone_number,
            first_name=first_name,
            form_url=personalized_url,
        )

        mark_as_sent(base, mentee)
        print(f"Sent: {mentee_id}")


if __name__ == "__main__":
    main()
