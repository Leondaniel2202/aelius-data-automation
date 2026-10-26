"""Minimal Meta WhatsApp Cloud API client."""
import requests


def normalize_phone_number(phone_number: str) -> str:
    return phone_number.replace("+", "").replace("-", "").replace(" ", "")


class WhatsAppClient:
    def __init__(self, token: str, phone_number_id: str, graph_api: str = "https://graph.facebook.com/v23.0"):
        if not token or not phone_number_id or token == "REPLACE_ME" or phone_number_id == "REPLACE_ME":
            raise ValueError("WhatsApp token and phone number ID must be configured")
        self.token = token
        self.phone_number_id = phone_number_id
        self.graph_api = graph_api.rstrip("/")

    def send_template(self, phone: str, template: str, parameters: list[str], language: str = "de") -> dict:
        response = requests.post(
            f"{self.graph_api}/{self.phone_number_id}/messages",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp",
                "to": normalize_phone_number(phone),
                "type": "template",
                "template": {
                    "name": template,
                    "language": {"code": language},
                    "components": [{"type": "body", "parameters": [{"type": "text", "text": value} for value in parameters]}],
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
