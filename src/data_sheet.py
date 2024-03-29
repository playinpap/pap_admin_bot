import os
import gspread
from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint
from typing import List

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def get_gspread_service_account():
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
    return gspread.service_account_from_dict(credentials)

def get_worksheet(svc_account, spreadsheet: str, worksheet: str):
    sheet = svc_account.open(spreadsheet).worksheet(worksheet)
    return sheet.get_all_records()

def insert_worksheet(svc_account, spreadsheet: str, worksheet: str, data: List[list]):
    '''
    시트에 데이터를 추가합니다.
    '''
    sheet = svc_account.open(spreadsheet).worksheet(worksheet)
    for row in data:
        sheet.append_row(row)

def delete_worksheet_contents(svc_account, spreadsheet: str, worksheet: str):
    '''
    Header row를 제외한 나머지 컨텐츠를 제거합니다.
    '''
    sheet = svc_account.open(spreadsheet).worksheet(worksheet)
    sheet.batch_clear(['A2:Z'])
