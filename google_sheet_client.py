import os
import pandas as pd
import gspread
from pathlib import Path
from dotenv import load_dotenv


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class GoogelSheetClient:
    def __init__(self):
        credentials = {
            "type": "service_account",
            "project_id": os.environ.get('PROJECT_ID'),
            "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
            "private_key": os.environ.get('PRIVATE_KEY'),
            "client_email": os.environ.get('CLIENT_EMAIL'),
            "client_id": os.environ.get('CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get('CLIENT_CERT_URL')
        }
        self.client = gspread.service_account_from_dict(credentials)

    def get_worksheet(self):
        return self.client.open(os.environ.get('SPREADSHEET_NAME')).worksheet(os.environ.get('WORKSHEET_NAME'))
