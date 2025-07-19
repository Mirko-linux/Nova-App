# Elenco componenti proprietari

In questo documento sono riportati tutti i componenti proprietari di ArcadiaAI

## Google Gemini AP
/ArcadiaAI/sr/app.py

Libreria: google.generativeai

Modelli: Gemini 2.0 flash lite e 2.5 flash

import google.generativeai as genai
gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
ces_plus_model = genai.GenerativeModel('gemini-2.5-flash')

## Google Cloud Text-to-Speech
/ArcadiaAI/sr/app.py

Libreria: google.cloud.texttospeech_v1
from google.cloud import texttospeech_v1 as texttospeech
