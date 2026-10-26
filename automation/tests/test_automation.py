import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from automation.shared.forms import build_form_url, get_form_url
from automation.shared.seatable_client import SeaTableInternalClient, eligible_mentees
from automation.shared.whatsapp_client import WhatsAppClient, normalize_phone_number

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bundle", ROOT / "build" / "bundle.py")
BUNDLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUNDLER)


class AutomationTests(unittest.TestCase):
    def test_form_url(self):
        self.assertEqual(build_form_url("https://example.org/form", "ME-000123"),
                         "https://example.org/form?prefillHide_mentee_id=ME-000123")
        self.assertIn("&prefillHide_mentee_id=", build_form_url("https://example.org/form?x=1", "ME-1"))

    def test_form_lookup(self):
        self.assertEqual(get_form_url([{"form_config": '{"form_name":"test"}', "form_link": "https://example.org"}], "test"),
                         "https://example.org")
        with self.assertRaises(ValueError):
            get_form_url([], "missing")

    def test_phone(self):
        self.assertEqual(normalize_phone_number("+31 6-123"), "316123")

    def test_eligibility(self):
        rows = [{"id": "1", "phone": "123", "sent": False}, {"id": "2", "phone": "456", "sent": True},
                {"id": "3", "phone": "", "sent": False}]
        self.assertEqual(eligible_mentees(rows, "phone", "id", "sent"), [rows[0]])

    def test_internal_adapter(self):
        base = Mock()
        base.list_rows.return_value = [{"_id": "1"}]
        adapter = SeaTableInternalClient(base)
        self.assertEqual(adapter.list_rows("Mentees"), [{"_id": "1"}])
        adapter.update_row("Mentees", "1", {"sent": True})
        base.update_row.assert_called_once_with("Mentees", "1", {"sent": True})

    @patch("automation.shared.whatsapp_client.requests.post")
    def test_whatsapp_payload(self, post):
        post.return_value.json.return_value = {"messages": [{"id": "abc"}]}
        client = WhatsAppClient("fake-token", "123")
        client.send_template("+31 6-123", "test", ["Anna", "https://example.org"])
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["to"], "316123")
        self.assertEqual(payload["template"]["components"][0]["parameters"][0]["text"], "Anna")
        post.return_value.raise_for_status.assert_called_once()

    def test_missing_whatsapp_credentials(self):
        with self.assertRaises(ValueError):
            WhatsAppClient("REPLACE_ME", "123")

    def test_build_all(self):
        with tempfile.TemporaryDirectory() as directory:
            for script in (ROOT / "scripts").glob("*.py"):
                output = Path(directory) / script.name
                BUNDLER.bundle(script, output)
                self.assertTrue(output.exists())
                self.assertNotIn("from shared.", output.read_text())
                compile(output.read_text(), str(output), "exec")


if __name__ == "__main__":
    unittest.main()
