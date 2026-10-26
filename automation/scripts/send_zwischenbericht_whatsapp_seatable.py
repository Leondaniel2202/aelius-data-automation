"""WhatsApp Zwischenbericht sender executed inside SeaTable."""
import os
from datetime import datetime

import requests
from seatable_api import Base, context

from shared.forms import build_form_url
from shared.seatable_client import SeaTableInternalClient, eligible_mentees
from shared.whatsapp_client import WhatsAppClient

MENTEES_TABLE = "Mentees"
MENTEE_ID_COLUMN = "Mentee-ID"
FIRST_NAME_COLUMN = "Vorname"
PHONE_COLUMN = "Telefonnummer"
SENT_COLUMN = "Zwischenbericht verschickt"
SENT_AT_COLUMN = "Zwischenbericht versendet am"
FORM_URL = "https://cloud.seatable.io/dtable/forms/396ef8a7-d532-4ebf-aa04-1efc8657651f/"
TEMPLATE = "zwischenbericht_template"


def main() -> None:
    base = Base(context.api_token, context.server_url)
    base.auth()
    seatable = SeaTableInternalClient(base)
    mentees = eligible_mentees(seatable.list_rows(MENTEES_TABLE), PHONE_COLUMN, MENTEE_ID_COLUMN, SENT_COLUMN)
    print(f"{len(mentees)} Mentees found")
    if not mentees:
        return

    # Configure these in the SeaTable runtime. Never put live credentials in Git or dist.
    whatsapp = WhatsAppClient(os.environ["WHATSAPP_TOKEN"], os.environ["WHATSAPP_PHONE_NUMBER_ID"])
    # Require explicit confirmation: do not automatically send on a scheduled execution.
    if input("Send all messages? [y/N]: ").strip().lower() != "y":
        print("Cancelled.")
        return
    for mentee in mentees:
        mentee_id = mentee[MENTEE_ID_COLUMN]
        try:
            whatsapp.send_template(
                phone=mentee[PHONE_COLUMN], template=TEMPLATE,
                parameters=[mentee.get(FIRST_NAME_COLUMN) or "", build_form_url(FORM_URL, mentee_id)],
            )
            seatable.update_row(MENTEES_TABLE, mentee["_id"], {
                SENT_COLUMN: True,
                SENT_AT_COLUMN: datetime.now().astimezone().isoformat(timespec="seconds"),
            })
            print(f"Sent: {mentee_id}")
        except requests.RequestException as error:
            print(f"FAILED: {mentee_id}: {error}")


if __name__ == "__main__":
    main()
