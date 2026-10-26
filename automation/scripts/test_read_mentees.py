import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ["SEATABLE_TOKEN"]

token_response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={"Authorization": f"Bearer {api_token}"},
)
token_response.raise_for_status()

token_data = token_response.json()
base_token = token_data["access_token"]
base_uuid = token_data["dtable_uuid"]

url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{base_uuid}/rows/"

response = requests.get(
    url,
    headers={"Authorization": f"Bearer {base_token}"},
    params={"table_name": "Mentees"},
)

response.raise_for_status()

print(response.json()["rows"][:3])