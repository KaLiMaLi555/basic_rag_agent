import base64
import uuid

import requests


def sarwam_translate(query: str, api_key: str):
    url = "https://api.sarvam.ai/translate"
    payload = {
        "input": query,
        "source_language_code": "en-IN",
        "target_language_code": "hi-IN",
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": True,
    }
    headers = {
        "Content-Type": "application/json",
        "API-Subscription-Key": api_key,
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    translated_string = response.json()["translated_text"]
    return translated_string


def sarwam_text_to_speech(query: str, api_key: str):
    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [query],
        "target_language_code": "hi-IN",
        "speaker": "meera",
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 8000,
        "enable_preprocessing": True,
        "model": "bulbul:v1",
    }
    headers = {
        "Content-Type": "application/json",
        "API-Subscription-Key": api_key,
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    audio_string = response.json()["audios"][0]
    save_file = uuid.uuid4().hex + ".wav"
    with open(f"public/{save_file}", "wb") as f:
        f.write(base64.b64decode(audio_string))
    return save_file


def get_speech(text: str, sarwam_api_key: str) -> str:
    translated_text = sarwam_translate(text, sarwam_api_key)
    speech = sarwam_text_to_speech(translated_text, sarwam_api_key)
    return speech
