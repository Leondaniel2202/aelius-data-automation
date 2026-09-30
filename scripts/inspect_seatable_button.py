import os

import requests
from dotenv import load_dotenv

load_dotenv()

SEATABLE_API_TOKEN = os.environ["SEATABLE_TOKEN"]

TABLE_NAME = "AL_Mentees"
BUTTON_COLUMN = "T1-B (Ohne Mentor) - Form"

# Get Base-Token
token_response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={
        "Authorization": f"Bearer {SEATABLE_API_TOKEN}",
    },
)

token_response.raise_for_status()

token_data = token_response.json()

base_token = token_data["access_token"]
base_uuid = token_data["dtable_uuid"]

print("Connected to:", token_data.get("dtable_name"))
print("Base UUID:", base_uuid)

# Try column metadata request
url = (
    f"https://cloud.seatable.io/api-gateway/api/v2/"
    f"dtables/{base_uuid}/columns/"
)

response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {base_token}",
        "Accept": "application/json",
    },
    params={
        "table_name": TABLE_NAME,
    },
)

print("Status:", response.status_code)
print("Response:", response.text)

response.raise_for_status()

columns = response.json()["columns"]

for column in columns:
    if column.get("name") == BUTTON_COLUMN:
        print("Found column:")
        print(column)
        break