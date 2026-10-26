# Aelius SeaTable automations

- `scripts/`: entry points (local REST and SeaTable-internal)
- `shared/seatable_client.py`: lightweight SeaTable REST and internal adapters
- `shared/whatsapp_client.py`: WhatsApp Cloud API requests
- `shared/forms.py`: form lookup and personalized URLs
- `build/`: standalone script bundler
- `tests/`: offline unit tests
- `dist/`: generated standalone scripts (gitignored)

From repository root:

```bash
uv sync
uv run python -m unittest discover -s automation/tests -v
uv run python automation/build/bundle.py
```

The build generates `automation/dist/*.py`. GitHub Actions runs tests and uploads these files as downloadable artifacts. **Do not commit dist or insert real credentials into generated files.** No deployment to SeaTable or WhatsApp sending is performed by the build.

The builder inlines direct imports from `shared/*.py`; nested shared imports and aliases are deliberately unsupported. Local scripts use environment variables (`SEATABLE_TOKEN`, `SEATABLE_ACCOUNT_TOKEN`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`). The internal SeaTable script uses `seatable_api.context` for its base and expects WhatsApp credentials from the runtime environment; verify your SeaTable Cloud runtime actually supports secure environment variables before executing. No secrets are bundled.

**Operational caution:** Internal script currently uses interactive confirmation and is not suitable for unattended schedules. Both scripts mark rows sent only after API acceptance, but a failure between WhatsApp acceptance and updating SeaTable can still cause duplicate sends on rerun. Test on a safe subset before using with real recipients.
