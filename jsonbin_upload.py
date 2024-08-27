import requests
import os
from dotenv import load_dotenv

load_dotenv()

BIN_ID = os.getenv('BIN_ID')
API_KEY = os.getenv('API_KEY')
url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': f'{API_KEY}',
}

data = {"sample": "Hello World"}

# req = requests.put(url, json=data, headers=headers)
