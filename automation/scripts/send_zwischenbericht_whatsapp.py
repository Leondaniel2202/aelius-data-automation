"""Manual local WhatsApp Zwischenbericht sender."""
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from shared.forms import build_form_url, get_form_url
from shared.seatable_client import SeaTableRestClient, eligible_mentees
from shared.whatsapp_client import WhatsAppClient

MENTEES_TABLE = "Mentees"
MENTEE_ID_COLUMN = "Mentee-ID"
FIRST_NAME_COLUMN = "Vorname"
PHONE_COLUMN = "Telefonnummer"
SENT_COLUMN = "Zwischenbericht verschickt"
SENT_AT_COLUMN = "Zwischenbericht versendet am"
FORM_NAME = "T1-B - Zwischenbefragung (ohne Mentor:in)"
TEMPLATE = "zwischenbericht_template"


def main() -> None:
    load_dotenv()
    seatable = SeaTableRestClient(os.environ["SEATABLE_TOKEN"], os.environ["SEATABLE_ACCOUNT_TOKEN"])
    form_url = get_form_url(seatable.list_forms(), FORM_NAME)
    mentees = eligible_mentees(seatable.list_rows(MENTEES_TABLE), PHONE_COLUMN, MENTEE_ID_COLUMN, SENT_COLUMN)

    print(f"\n{len(mentees)} Mentees found\n")
    for mentee in mentees:
        print(mentee[MENTEE_ID_COLUMN], mentee.get(FIRST_NAME_COLUMN, ""), mentee[PHONE_COLUMN],
              build_form_url(form_url, mentee[MENTEE_ID_COLUMN]))
    if not mentees or input("\nSend all messages? [y/N]: ").strip().lower() != "y":
        print("Cancelled or no recipients.")
        return

    whatsapp = WhatsAppClient(os.environ["WHATSAPP_TOKEN"], os.environ["WHATSAPP_PHONE_NUMBER_ID"])
    for mentee in mentees:
        mentee_id = mentee[MENTEE_ID_COLUMN]
        try:
            whatsapp.send_template(
                phone=mentee[PHONE_COLUMN], template=TEMPLATE,
                parameters=[mentee.get(FIRST_NAME_COLUMN) or "", build_form_url(form_url, mentee_id)],
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
