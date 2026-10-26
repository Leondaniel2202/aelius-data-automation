# Aelius SeaTable automations

- `scripts/send_zwischenbericht_whatsapp.py`: the **only production script**, executed inside SeaTable
- `shared/seatable_client.py`: SeaTable adapters and reusable row filtering
- `shared/whatsapp_client.py`: Meta WhatsApp Cloud API client
- `shared/forms.py`: form URL helpers
- `build/bundle.py`: builds standalone Python scripts
- `tests/`: offline unit tests
- `dist/`: generated scripts, ignored by Git

From the repository root:

```bash
uv sync
uv run python -m unittest discover -s automation/tests -v
uv run python automation/build/bundle.py
```

The build produces `automation/dist/send_zwischenbericht_whatsapp.py`. GitHub Actions uploads the generated script as an artifact; it **does not automatically deploy or run it**.

The script uses `seatable_api.context` for SeaTable access and `shared.whatsapp_client.WhatsAppClient` for WhatsApp. It expects `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` in the execution environment. Verify that SeaTable Cloud supports securely supplying these before execution; never paste secrets into Git or generated artifacts.

**Operational limitations:** The script currently prompts for interactive confirmation, so it is not suitable for unattended SeaTable schedules as-is. WhatsApp acceptance followed by a failed SeaTable update can lead to a duplicate send on retry. Validate the runtime and test with a safe subset before production use.
