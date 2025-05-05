import os
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Путь к JSON-файлу с ключами
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'gdrive-credentials.json'


def get_drive_service():
    # Загружаем учетные данные
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    return service, credentials

