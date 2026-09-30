"""Manual proof of concept for sending Aelius Zwischenbericht forms via WhatsApp.

Current intended flow:
1. Read the SeaTable `Mentees` table.
2. Keep rows where:
   - a phone number exists,
   - `Zwischenbericht verschickt` is not checked,
   - a Mentee ID exists.
3. Resolve the corresponding form link from `al_mentee`.
   For now we start with `T1-B (Ohne Mentor) - Form` only.
4. Preview recipients and require explicit confirmation.
5. Send the WhatsApp message.
6. Only after a successful send, mark `Zwischenbericht verschickt` as checked.

This file intentionally contains only the skeleton until the exact SeaTable API
representation of the form-button field is confirmed.
"""

from __future__ import annotations


def get_mentees_to_send() -> list[dict]:
    """Return eligible Mentee rows from SeaTable.

    TODO: Connect to SeaTable and implement filtering.
    """
    raise NotImplementedError


def get_form_link(mentee: dict) -> str:
    """Resolve the T1-B form URL for the Mentee from `al_mentee`.

    TODO: Inspect how SeaTable exposes the button field through its API before
    implementing this.
    """
    raise NotImplementedError


def preview_messages(mentees: list[dict]) -> None:
    """Print the recipients/messages that would be sent."""
    raise NotImplementedError


def confirm_send() -> bool:
    """Require explicit user confirmation before any WhatsApp message is sent."""
    return input("Send these messages? [y/N]: ").strip().lower() == "y"


def send_whatsapp_message(mentee: dict, form_link: str) -> None:
    """Send one WhatsApp message through the Meta WhatsApp Cloud API.

    TODO: Implement once the final message/template format is decided.
    """
    raise NotImplementedError


def mark_zwischenbericht_as_sent(mentee: dict) -> None:
    """Check `Zwischenbericht verschickt` in SeaTable after a successful send."""
    raise NotImplementedError


def main() -> None:
    mentees = get_mentees_to_send()

    if not mentees:
        print("No Mentees found that need a Zwischenbericht message.")
        return

    preview_messages(mentees)

    if not confirm_send():
        print("Cancelled. No messages were sent.")
        return

    for mentee in mentees:
        form_link = get_form_link(mentee)
        send_whatsapp_message(mentee, form_link)
        mark_zwischenbericht_as_sent(mentee)


if __name__ == "__main__":
    main()
