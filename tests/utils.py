import os
import tempfile
import requests
import subprocess
import wave
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

import io
from googleapiclient.http import MediaIoBaseDownload
from utils.google_drive_service import get_drive_service  # Импортируй свою функцию


load_dotenv()

ffmpeg_path = os.getenv('FFMPEG_PATH')
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url = "https://api.openai.com/v1/chat/completions"


def call_openai_api(system_message, user_message):
    print("Calling OpenAI API", openai_api_key)
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.5,
        "max_tokens": 2000
    }
    response = requests.post(openai_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def download_file_from_drive(file_id):
    service, _ = get_drive_service()

    # Получаем информацию о файле
    file = service.files().get(fileId=file_id).execute()
    file_name = file['name']

    # Создаем временный файл
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file_name)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')

    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while not done:
        status, done = downloader.next_chunk()

    return file_path


def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    command = [
        ffmpeg_path, "-i", video_path,
        "-ac", "1",            # Mono audio
        "-ar", "16000",        # Sample rate 16000 Hz (optimal for Vosk)
        "-sample_fmt", "s16",  # 16-bit PCM
        audio_path
    ]
    subprocess.run(command, check=True)
    return audio_path


def transcribe_with_vosk(audio_path):
    model = Model(lang="en-us")
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 44100]:
        raise ValueError("Audio file must be WAV format mono PCM.")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    result = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result += " " + res.get("text", "")

    final_res = json.loads(rec.FinalResult())
    result += " " + final_res.get("text", "")
    wf.close()

    return result.strip()
