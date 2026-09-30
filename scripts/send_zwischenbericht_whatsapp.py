import json
import os
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


# ============================================================
# Constants
# ============================================================

SEATABLE_SERVER = "https://cloud.seatable.io"
META_GRAPH_API = "https://graph.facebook.com/v23.0"

MENTEES_TABLE = "Mentees"

MENTEE_ID_COLUMN = "Mentee-ID"
PHONE_COLUMN = "Telefonnummer"
SENT_COLUMN = "Zwischenbericht verschickt"

FORM_NAME = "T1-B - Zwischenbefragung (ohne Mentor:in)"

WHATSAPP_MESSAGE = (
    "Hallo! Hier ist dein Zwischenbericht von Aelius:\n\n"
    "{form_url}"
)


# ============================================================
# Environment
# ============================================================

load_dotenv()

SEATABLE_TOKEN = os.environ["SEATABLE_TOKEN"]
SEATABLE_ACCOUNT_TOKEN = os.environ["SEATABLE_ACCOUNT_TOKEN"]

WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
WHATSAPP_PHONE_NUMBER_ID = os.environ["WHATSAPP_PHONE_NUMBER_ID"]


# ============================================================
# SeaTable authentication
# ============================================================

def get_seatable_access() -> dict:
    response = requests.get(
        f"{SEATABLE_SERVER}/api/v2.1/dtable/app-access-token/",
        headers={
            "Authorization": f"Bearer {SEATABLE_TOKEN}",
        },
    )

    response.raise_for_status()
    return response.json()


# ============================================================
# SeaTable forms
# ============================================================

def get_forms(
    workspace_id: int,
    base_name: str,
) -> list[dict]:
    response = requests.get(
        f"{SEATABLE_SERVER}/api/v2.1/forms/",
        headers={
            "Authorization": f"Bearer {SEATABLE_ACCOUNT_TOKEN}",
        },
        params={
            "workspace_id_query": workspace_id,
            "base_name": base_name,
        },
    )

    response.raise_for_status()

    return response.json()["form_list"]


def get_form_url(
    forms: list[dict],
    form_name: str,
) -> str:
    for form in forms:
        config = json.loads(form["form_config"])

        if config.get("form_name") == form_name:
            return form["form_link"]

    available_forms = [
        json.loads(form["form_config"]).get("form_name")
        for form in forms
    ]

    raise ValueError(
        f"Form '{form_name}' not found. "
        f"Available forms: {available_forms}"
    )


def build_form_url(
    form_url: str,
    mentee_id: str,
) -> str:
    query = urlencode(
        {
            "prefillHide_mentee_id": mentee_id,
        }
    )

    separator = "&" if "?" in form_url else "?"

    return f"{form_url}{separator}{query}"


# ============================================================
# SeaTable rows
# ============================================================

def get_column_mapping(
    base_token: str,
    base_uuid: str,
    table_name: str,
) -> dict[str, str]:
    response = requests.get(
        f"{SEATABLE_SERVER}/api-gateway/api/v2/"
        f"dtables/{base_uuid}/columns/",
        headers={
            "Authorization": f"Bearer {base_token}",
        },
        params={
            "table_name": table_name,
        },
    )

    response.raise_for_status()

    return {
        column["key"]: column["name"]
        for column in response.json()["columns"]
    }


def get_rows(
    base_token: str,
    base_uuid: str,
    table_name: str,
) -> list[dict]:
    response = requests.get(
        f"{SEATABLE_SERVER}/api-gateway/api/v2/"
        f"dtables/{base_uuid}/rows/",
        headers={
            "Authorization": f"Bearer {base_token}",
        },
        params={
            "table_name": table_name,
        },
    )

    response.raise_for_status()

    rows = response.json()["rows"]

    column_mapping = get_column_mapping(
        base_token=base_token,
        base_uuid=base_uuid,
        table_name=table_name,
    )

    return [
        {
            column_mapping.get(key, key): value
            for key, value in row.items()
        }
        for row in rows
    ]


def get_mentees_to_send(
    base_token: str,
    base_uuid: str,
) -> list[dict]:
    rows = get_rows(
        base_token=base_token,
        base_uuid=base_uuid,
        table_name=MENTEES_TABLE,
    )

    return [
        row
        for row in rows
        if row.get(PHONE_COLUMN)
        and row.get(MENTEE_ID_COLUMN)
        and not row.get(SENT_COLUMN)
    ]


def mark_as_sent(
    base_token: str,
    base_uuid: str,
    mentee: dict,
) -> None:
    response = requests.put(
        f"{SEATABLE_SERVER}/api-gateway/api/v2/"
        f"dtables/{base_uuid}/rows/",
        headers={
            "Authorization": f"Bearer {base_token}",
            "Content-Type": "application/json",
        },
        json={
            "table_name": MENTEES_TABLE,
            "updates": [
                {
                    "row_id": mentee["_id"],
                    "row": {
                        SENT_COLUMN: True,
                    },
                }
            ],
        },
    )

    response.raise_for_status()


# ============================================================
# WhatsApp
# ============================================================

def send_whatsapp_message(
    phone_number: str,
    message: str,
) -> None:
    response = requests.post(
        f"{META_GRAPH_API}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages",
        headers={
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "to": "31617327648",
            "type": "template",
            "template": {
                "name": "zwischenbericht_template",
                "language": {"code": "en_US"},
            },
        }
    )

    response.raise_for_status()


# ============================================================
# Main
# ============================================================

def main() -> None:
    access = get_seatable_access()

    base_token = access["access_token"]
    base_uuid = access["dtable_uuid"]
    workspace_id = access["workspace_id"]
    base_name = access["dtable_name"]

    forms = get_forms(
        workspace_id=workspace_id,
        base_name=base_name,
    )

    form_url = get_form_url(
        forms=forms,
        form_name=FORM_NAME,
    )

    mentees = get_mentees_to_send(
        base_token=base_token,
        base_uuid=base_uuid,
    )

    print(f"\n{len(mentees)} Mentees found\n")

    for mentee in mentees:
        personalized_url = build_form_url(
            form_url=form_url,
            mentee_id=mentee[MENTEE_ID_COLUMN],
        )

        print(
            mentee[MENTEE_ID_COLUMN],
            mentee[PHONE_COLUMN],
            personalized_url,
        )

    if not mentees:
        return

    confirmation = input(
        "\nSend all messages? [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("Cancelled.")
        return

    for mentee in mentees:
        mentee_id = mentee[MENTEE_ID_COLUMN]
        phone_number = mentee[PHONE_COLUMN]

        personalized_url = build_form_url(
            form_url=form_url,
            mentee_id=mentee_id,
        )

        message = WHATSAPP_MESSAGE.format(
            form_url=personalized_url,
        )

        try:
            send_whatsapp_message(
                phone_number=phone_number,
                message=message,
            )

            mark_as_sent(
                base_token=base_token,
                base_uuid=base_uuid,
                mentee=mentee,
            )

            print(f"Sent: {mentee_id}")

        except requests.HTTPError as error:
            print(f"FAILED: {mentee_id}")
            print(error)


if __name__ == "__main__":
    main()