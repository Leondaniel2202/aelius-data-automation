# SeaTable automations

- `scripts/`: executable SeaTable and local helper scripts
- `shared/`: pure, reusable Python functions
- `build/`: standalone script builder
- `tests/`: unit and build checks

Run from the repository root:

```bash
python -m unittest discover -s automation/tests -v
python automation/build/bundle.py
```

The build creates `automation/dist/*.py` for manual import into SeaTable. GitHub Actions publishes these files as a downloadable artifact. **It does not deploy or execute scripts.**

Only top-level `from shared.common import ...` imports are currently inlined. Keep shared helpers independent of runtime-specific credentials. Scripts that use `seatable_api.context` must execute in SeaTable; external REST scripts still need their own environment variables. Never commit live WhatsApp tokens or other secrets.

Note: the existing internal WhatsApp script has no send confirmation or per-recipient retry handling. Review it before production use.
