"""Small SeaTable adapters for local REST and internal SeaTable execution."""
import requests


def eligible_mentees(rows: list[dict], phone_column: str, id_column: str, sent_column: str) -> list[dict]:
    return [row for row in rows if row.get(phone_column) and row.get(id_column) and not row.get(sent_column)]


class SeaTableRestClient:
    def __init__(self, api_token: str, account_token: str | None = None, server: str = "https://cloud.seatable.io"):
        self.server = server.rstrip("/")
        self.account_token = account_token
        response = requests.get(
            f"{self.server}/api/v2.1/dtable/app-access-token/",
            headers={"Authorization": f"Bearer {api_token}"}, timeout=30,
        )
        response.raise_for_status()
        self.access = response.json()
        self.token = self.access["access_token"]
        self.uuid = self.access["dtable_uuid"]

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def list_rows(self, table_name: str) -> list[dict]:
        url = f"{self.server}/api-gateway/api/v2/dtables/{self.uuid}"
        response = requests.get(f"{url}/rows/", headers=self._headers(), params={"table_name": table_name}, timeout=30)
        response.raise_for_status()
        columns = requests.get(f"{url}/columns/", headers=self._headers(), params={"table_name": table_name}, timeout=30)
        columns.raise_for_status()
        mapping = {column["key"]: column["name"] for column in columns.json()["columns"]}
        return [{mapping.get(key, key): value for key, value in row.items()} for row in response.json()["rows"]]

    def update_row(self, table_name: str, row_id: str, values: dict) -> None:
        response = requests.put(
            f"{self.server}/api-gateway/api/v2/dtables/{self.uuid}/rows/",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"table_name": table_name, "updates": [{"row_id": row_id, "row": values}]},
            timeout=30,
        )
        response.raise_for_status()

    def list_forms(self) -> list[dict]:
        if not self.account_token:
            raise ValueError("SEATABLE_ACCOUNT_TOKEN is required to list forms")
        response = requests.get(
            f"{self.server}/api/v2.1/forms/",
            headers={"Authorization": f"Bearer {self.account_token}"},
            params={"workspace_id_query": self.access["workspace_id"], "base_name": self.access["dtable_name"]},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["form_list"]


class SeaTableInternalClient:
    def __init__(self, base):
        self.base = base

    def list_rows(self, table_name: str) -> list[dict]:
        return self.base.list_rows(table_name)

    def update_row(self, table_name: str, row_id: str, values: dict) -> None:
        self.base.update_row(table_name, row_id, values)
