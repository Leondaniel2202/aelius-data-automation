import importlib.util
import tempfile
import unittest
from pathlib import Path

from automation.shared.common import build_form_url, normalize_phone_number, eligible_mentees

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bundle", ROOT / "build" / "bundle.py")
BUNDLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUNDLER)


class HelpersTest(unittest.TestCase):
    def test_form_url(self):
        self.assertEqual(build_form_url("https://example.org/form", "ME-000123"), "https://example.org/form?prefillHide_mentee_id=ME-000123")
        self.assertIn("&prefillHide_mentee_id=", build_form_url("https://example.org/form?x=1", "ME-1"))

    def test_phone(self):
        self.assertEqual(normalize_phone_number("+31 6-123"), "316123")

    def test_eligibility(self):
        rows = [{"id": "1", "phone": "123", "sent": False}, {"id": "2", "phone": "456", "sent": True}, {"id": "3", "phone": "", "sent": False}]
        self.assertEqual(eligible_mentees(rows, "phone", "id", "sent"), [rows[0]])

    def test_build_all(self):
        with tempfile.TemporaryDirectory() as directory:
            for script in (ROOT / "scripts").glob("*.py"):
                output = Path(directory) / script.name
                BUNDLER.bundle(script, output)
                self.assertTrue(output.exists())
                self.assertNotIn("from shared.common import", output.read_text())


if __name__ == "__main__":
    unittest.main()
