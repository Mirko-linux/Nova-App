import locale
import sys
import asyncio
import subprocess 
import concurrent
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from sympy import symbols, Eq, solve, simplify
import math
from flask import Flask, request, jsonify, send_from_directory
from flask import session
from flask_cors import CORS
import requests
import os
import re
import datetime
import urllib.parse
from dotenv import load_dotenv
from openpyxl import load_workbook
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import io
import time 
import base64
from PyPDF2 import PdfReader
from flask_cors import CORS 
import google.generativeai as genai
# Sostituisci gli import con:
from flask_cors import CORS
app = Flask(__name__)
CORS(app, origins=[
    "https://arcadiaai.onrender.com",     # L'URL del tuo frontend e backend su Render
    "http://localhost:8000",              # Un comune URL per test locali
    "http://192.168.178.52:10000"         # L'URL locale specifico che hai menzionato
], supports_credentials=True) # supports_credentials è utile per i cookie e g
# Configurazione iniziale
load_dotenv()
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"DEBUG: Caricamento .env da {env_path}")
load_dotenv(dotenv_path=env_path)

TELEGRAPH_API_KEY = os.getenv("TELEGRAPH_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHERMAP_API_KEY = os.gentenv ("OPENWEATHERMAP_API_KEY")
TELEGRAM_TOKEN = os.genetenv ("TELEGRAM_TOKEN")

print("TELEGRAPH_API_KEY:", TELEGRAPH_API_KEY)
print("GOOGLE_API_KEY:", GOOGLE_API_KEY)
print("HUGGINGFACE_API_KEY:", HUGGINGFACE_API_KEY)
print("OPENWEATHERMAP_API_KEY:", OPENWEATHERMAP_API_KEY)
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "arcadiaai-secret")  # AGGIUNGI QUESTA RIGA
EXTENSIONS = {}
# Configura Gemini (CES 1.5)
# Modifica nella sezione di configurazione iniziale
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    try:
        # Configura sia Gemini che CES Plus
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        ces_plus_model = genai.GenerativeModel('gemini-1.5-flash')  # Usa lo stesso modello ma con prompt diversi
        print("✅ Gemini 1.5 e CES Plus configurati con successo!")
    except Exception as e:
        print(f"❌ Errore configurazione modelli: {str(e)}")
        gemini_model = None
        ces_plus_model = None
# Dizionario delle risposte predefinite
risposte = {
    "chi sei": "Sono ArcadiaAI, un chatbot libero e open source, creato da Mirko Yuri Donato.",
    "cosa sai fare": "Posso aiutarti a scrivere saggi, fare ricerche e rispondere a tutto ciò che mi chiedi. Inoltre, posso pubblicare contenuti su Telegraph!",
    "chi è tobia testa": "Tobia Testa (anche noto come Tobia Teseo) è un micronazionalista leonense noto per la sua attività nella Repubblica di Arcadia, ma ha anche rivestito ruoli fondamentali a Lumenaria.",
    "chi è mirko yuri donato": "Mirko Yuri Donato è un giovane micronazionalista, poeta e saggista italiano, noto per aver creato Nova Surf, Leonia+ e per le sue opere letterarie.",
    "chi è il presidente di arcadia": "Il presidente di Arcadia è Andrea Lazarev",
    "chi è il presidente di lumenaria": "Il presidente di Lumenaria attualmente è Carlo Cesare Orlando, mentre il presidente del consiglio è Ciua Grazisky. Tieni presente però che attualmente Lumenaria si trova in ibernazione istituzionale quindi tutte le attività politiche sono sospese e la gestione dello stato è affidata al Consiglio di Fiducia",
    "cos'è nova surf": "Nova Surf è un browser web libero e open source, nata come alternativa made-in-Italy a Google Chrome, Moziila Firefox, Microsoft Edge, eccetera",
    "chi ti ha creato": "Sono stato creato da Mirko Yuri Donato.",
    "chi è ciua grazisky": "Ciua Grazisky è un cittadino di Lumenaria, noto principalmente per il suo ruolo da Dirigente del Corpo di Polizia ed attuale presidente del Consiglio di Lumenaria",
    "chi è carlo cesare orlando": "Carlo Cesare Orlando (anche noto come Davide Leone) è un micronazionalista italiano, noto per aver creato Leonia, la micronazione primordiale, da cui derivano Arcadia e Lumenaria",
    "chi è omar lanfredi": "Omar Lanfredi, ex cavaliere all'Ordine d'onore della Repubblica di Lumenaria, segretario del Partito Repubblicano Lumenarense, fondatore e preside del Fronte Nazionale Lumenarense, co-fondatore e presidente dell'Alleanza Nazionale Lumenarense, co-fondatore e coordinatore interno di Lumenaria e Progresso, sei volte eletto senatore, tre volte Ministro della Cultura, due volte Presidente del Consiglio dei Ministri, parlamentare della Repubblica di Iberia, Direttore dell'Agenzia Nazionale di Sicurezza della Repubblica di Iberia, Sottosegretario alla Cancelleria di Iberia, Segretario di Stato di Iberia, Ministro degli Affari Interni ad Iberia, Presidente del Senato della Repubblica di Lotaringia, Vicepresidente della Repubblica e Ministro degli Affari Interni della Repubblica di Lotaringia, Fondatore del giornale Il Quinto Mondo, magistrato a servizio del tribunale di giustizia di Lumenaria nell'anno 2023",
    "cos'è arcadiaai": "Ottima domanda! ArcadiaAI è un chatbot open source, progettato per aiutarti a scrivere saggi, fare ricerche e rispondere a domande su vari argomenti. È stato creato da Mirko Yuri Donato ed è in continua evoluzione.",
    "sotto che licenza è distribuito arcadiaa": "ArcadiaAI è distribuito sotto la licenza GNU GPL v3.0, che consente la modifica e la distribuzione del codice sorgente, garantendo la libertà di utilizzo e condivisione.",
    "cosa sono le micronazioni": "Le micronazioni sono entità politiche che dichiarano la sovranità su un territorio, ma non sono riconosciute come stati da governi o organizzazioni internazionali. Possono essere create per vari motivi, tra cui esperimenti sociali, culturali o politici.",
    "cos'è la repubblica di arcadia": "La repubblica di Arcadia è una micronazione leonense fondata l'11 dicembre 2021 da Andrea Lazarev e alcuni suoi seguaci. Arcadia si distingue dalle altre micronazioni leonensi per il suo approccio pragmatico e per la sua burocrazia snella. La micronazione ha anche un proprio sito web https://repubblicadiarcadia.it/ e una propria community su Telegram @Repubblica_Arcadia",
    "cos'è la repubblica di lumenaria": "La Repubblica di Lumenaria è una mcronazione fondata da Filippo Zanetti il 4 febbraio del 2020. Lumenaria è stata la micronazione più longeva della storia leonense, essendo sopravvissuta per oltre 3 anni. La micronazione e ha influenzato profondamente le altre micronazioni leonensi, che hanno coesistito con essa. Tra i motivi della sua longevità ci sono la sua burocrazia più vicina a quella di uno stato reale, la sua comunità attiva e una produzione culturale di alto livello",
    "chi è salvatore giordano": "Salvatore Giordano è un cittadino storico di Lumenaria",
    "da dove deriva il nome arcadia": "Il nome Arcadia deriva da un'antica regione della Grecia, simbolo di bellezza naturale e armonia. È stato scelto per rappresentare i valori di libertà e creatività che la micronazione promuove.",
    "da dove deriva il nome lumenaria": "Il nome Lumenaria prende ispirazione dai lumi facendo riferimento alla corrente illuminista del '700, ma anche da Piazza dei Lumi, sede dell'Accademia delle Micronazioni",
    "da dove deriva il nome leonia": "Il nome Leonia si rifa al cognome del suo fondatore Carlo Cesare Orlando, al tempo Davide Leone. Inizialmente il nome doveva essere temporaneo, ma poi è stato mantenuto come nome della micronazione",
    "cosa si intende per open source": "Il termine 'open source' si riferisce a software il cui codice sorgente è reso disponibile al pubblico, consentendo a chiunque di visualizzarlo, modificarlo e distribuirlo. Questo approccio promuove la collaborazione e l'innovazione nella comunità di sviluppo software.",
    "arcadiaai è un software libero": "Sì, ArcadiaAI è un software libero e open source, il che significa che chiunque può utilizzarlo, modificarlo e distribuirlo secondo i termini della licenza GNU GPL v3.0.",
    "cos'è un chatbot": "Un chatbot è un programma informatico progettato per simulare una conversazione con gli utenti, spesso utilizzando tecnologie di intelligenza artificiale. I chatbot possono essere utilizzati per fornire assistenza, rispondere a domande o semplicemente intrattenere.",
    "sotto che licenza sei distribuita": "ArcadiaAI è distribuita sotto la licenza GNU GPL v3.0, che consente la modifica e la distribuzione del codice sorgente, garantendo la libertà di utilizzo e condivisione.",
    "sai usare telegraph": "Sì, posso pubblicare contenuti su Telegraph! Se vuoi che pubblichi qualcosa, dimmi semplicemente 'Scrivimi un saggio su [argomento] e pubblicalo su Telegraph' e lo farò per te!",
    "puoi pubblicare su telegraph": "Certamente! Posso generare contenuti e pubblicarli su Telegraph. Prova a chiedermi: 'Scrivimi un saggio su Roma e pubblicalo su Telegraph'",
    "come usare telegraph": "Per usare Telegraph con me, basta che mi chiedi di scrivere qualcosa e di pubblicarlo su Telegraph. Ad esempio: 'Scrivimi un articolo sulla storia di Roma e pubblicalo su Telegraph'",
    "cos'è CES": "CES è l'acronimo di Cogito Ergo Sum, un modello di intelligenza artificiale openspurce sviluppato da Mirko Yuri Donato. Attualmente sono disponibili due versioni: CES 1.0 (Cohere) e CES 1.5 (Gemini).",
    "cos'è la modalità sperimentale": "La modalità sperimentale è una funzionalità di ArcadiaAI che consente di testare nuove funzionalità e miglioramenti prima del rilascio ufficiale. Può includere nuove capacità, modelli o strumenti.",
    "cos'è la modalità sviluppatore": "La modalità sviluppatore è una funzionalità di ArcadiaAI che consente agli sviluppatori di testare e implementare nuove funzionalità, modelli o strumenti. È progettata per facilitare lo sviluppo e il miglioramento continuo del chatbot.",
    "che differenza c'è tra la modalità sperimentale e la modalità sviluppatore": "La modalità sperimentale è destinata agli utenti finali per testare nuove funzionalità, mentre la modalità sviluppatore è per gli sviluppatori che vogliono implementare e testare nuove funzionalità o modelli. Entrambe le modalità possono coesistere e migliorare l'esperienza utente.",
    "cos'è CES Plus": "CES Plus è una versione avanzata di CES, ottimizzata nei ragionamenti e nella generazione di contenuti",
    "cos'è CES 1.0": "CES 1.0 è la prima versione del modello CES, sviluppato da Mirko Yuri Donato. Utilizza la tecnologia Cohere per generare contenuti e rispondere a domande. Tieni presente che questa versione verrà dismessa a partire dal 20 Maggio 2025.",
    "cos'è CES 1.5": "CES 1.5 è la versione più recente del modello CES, sviluppato da Mirko Yuri Donato. Utilizza la tecnologia Gemini per generare contenuti e rispondere a domande. Questa versione offre prestazioni migliorate rispetto a CES 1.0 ma inferiori a CES Plus",
    "come attivo la modalità sperimentale": "Per attivare la modalità sperimentale, basta chiedere a ArcadiaAI di attivarla usando il comando \"@impostazioni modalità sperimentale attiva\". Una volta attivata, potrai testare nuove funzionalità e miglioramenti.",
    "come attivo la modalità sviluppatore": "Per attivare la modalità sviluppatore, basta chiedere a ArcadiaAI di attivarla usando il comando \"@impostazioni modalità sviluppatore attiva\". Una volta attivata, potrai testare e implementare nuove funzionalità e modelli.",
    "come disattivo la modalità sperimentale": "Per disattivare la modalità sperimentale, basta chiedere a ArcadiaAI di disattivarla usando il comando \"@impostazioni modalità sperimentale disattiva\". Una volta disattivata, non potrai più testare le nuove funzionalità.",
    "codice sorgente arcadiaai": "Il codice sorgente di ArcadiaAI è pubblico! Puoi trovarlo con il comando @codice_sorgente oppure visitando la repository: https://github.com/Mirko-linux/Nova-Surf/tree/main/ArcadiaAI",
    "sai cercare su internet": "Sì, posso cercare informazioni su Internet. Se hai bisogno di qualcosa in particolare dimmi @cerca e il termine di ricerca e io lo farò per te",
    "sai usare google": "No, non posso usare Google, perché sono progrmmato per cercare solamente su DuckDuckGo. Posso cercare informazioni su Internet usando DuckDuckGo. Se hai bisogno di qualcosa in particolare dimmi @cerca e il termine di ricerca e io lo farò per te",
    "come vengono salvate le conversazioni": "Le conversazioni vengoono salvate in locale sul tuo browser. Non vengono memorizzate su server esterni e non vengono condivise con terze parti. La tua privacy è importante per noi.",
    "come posso cancellare le conversazioni": "Puoi cancellare le conversazioni andando nelle impostazioni del tuo browser e cancellando la cache e i cookie. In alternativa, puoi usare il comando @cancella_conversazione per eliminare la cronologia delle chat.",
    "cosa sono i cookie": "I cookie sono piccoli file di testo che i siti web memorizzano sul tuo computer per ricordare informazioni sulle tue visite. Possono essere utilizzati per tenere traccia delle tue preferenze, autenticarti e migliorare l'esperienza utente.",
}

# Trigger per le risposte predefinite
trigger_phrases = {
    "chi sei": ["chi sei", "chi sei tu", "tu chi sei", "presentati", "come ti chiami", "qual è il tuo nome"],
    "cosa sai fare": ["cosa sai fare", "cosa puoi fare", "funzionalità", "capacità", "a cosa servi", "in cosa puoi aiutarmi"],
    "chi è tobia testa": ["chi è tobia testa", "informazioni su tobia testa", "parlami di tobia testa", "chi è tobia teseo"],
    "chi è mirko yuri donato": ["chi è mirko yuri donato", "informazioni su mirko yuri donato", "parlami di mirko yuri donato", "chi ha creato arcadiaai"],
    "chi è il presidente di arcadia": ["chi è il presidente di arcadia", "presidente di arcadia", "chi guida arcadia", "capo di arcadia"],
    "chi è il presidente di lumenaria": ["chi è il presidente di lumenaria", "presidente di lumenaria", "chi guida lumenaria", "capo di lumenaria", "carlo cesare orlando presidente"],
    "cos'è nova surf": ["cos'è nova surf", "che cos'è nova surf", "parlami di nova surf", "a cosa serve nova surf"],
    "chi ti ha creato": ["chi ti ha creato", "chi ti ha fatto", "da chi sei stato creato", "creatore di arcadiaai"],
    "chi è ciua grazisky": ["chi è ciua grazisky", "informazioni su ciua grazisky", "parlami di ciua grazisky"],
    "chi è carlo cesare orlando": ["chi è carlo cesare orlando", "informazioni su carlo cesare orlando", "parlami di carlo cesare orlando", "chi è davide leone"],
    "chi è omar lanfredi": ["chi è omar lanfredi", "informazioni su omar lanfredi", "parlami di omar lanfredi"],
    "cos'è arcadiaai": ["cos'è arcadiaai", "che cos'è arcadiaai", "parlami di arcadiaai", "a cosa serve arcadiaai"],
    "sotto che licenza è distribuito arcadiaa": ["sotto che licenza è distribuito arcadiaa", "licenza arcadiaai", "che licenza usa arcadiaai", "arcadiaai licenza"],
    "cosa sono le micronazioni": ["cosa sono le micronazioni", "micronazioni", "che cosa sono le micronazioni", "parlami delle micronazioni"],
    "cos'è la repubblica di arcadia": ["cos'è la repubblica di arcadia", "repubblica di arcadia", "che cos'è la repubblica di arcadia", "parlami della repubblica di arcadia", "arcadia micronazione"],
    "cos'è la repubblica di lumenaria": ["cos'è la repubblica di lumenaria", "repubblica di lumenaria", "che cos'è la repubblica di lumenaria", "parlami della repubblica di lumenaria", "lumenaria micronazione"],
    "chi è salvatore giordano": ["chi è salvatore giordano", "informazioni su salvatore giordano", "parlami di salvatore giordano"],
    "da dove deriva il nome arcadia": ["da dove deriva il nome arcadia", "origine nome arcadia", "significato nome arcadia", "perché si chiama arcadia"],
    "da dove deriva il nome lumenaria": ["da dove deriva il nome lumenaria", "origine nome lumenaria", "significato nome lumenaria", "perché si chiama lumenaria"],
    "da dove deriva il nome leonia": ["da dove deriva il nome leonia", "origine nome leonia", "significato nome leonia", "perché si chiama leonia"],
    "cosa si intende per open source": ["cosa si intende per open source", "open source significato", "che significa open source", "definizione di open source"],
    "arcadiaai è un software libero": ["arcadiaai è un software libero", "arcadiaai software libero", "arcadiaai è libero", "software libero arcadiaai"],
    "cos'è un chatbot": ["cos'è un chatbot", "chatbot significato", "che significa chatbot", "definizione di chatbot"],
    "sotto che licenza sei distribuita": ["sotto che licenza sei distribuita", "licenza di arcadiaai", "che licenza usi", "arcadiaai licenza"],
    "sai usare telegraph": ["sai pubblicare su telegraph", "funzioni su telegraph", "hai telegraph integrato", "telegraph", "puoi usare telegraph"],
    "puoi pubblicare su telegraph": ["puoi pubblicare su telegraph", "pubblicare su telegraph", "supporti telegraph"],
    "come usare telegraph": ["come usare telegraph", "come funziona telegraph", "istruzioni telegraph"],
    "cos'è CES" : ["cos è CES", "CES", "che cos'è CES", "definizione di CES"],
    "cos'è la modalità sperimentale": ["cos'è la modalità sperimentale", " parlami della modalità sperimentale", "che cos'è la modalità sperimentale"],
    "cos'è la modalità sviluppatore": ["cos'è la modalità sviluppatore", " parlami della modalità sviluppatore", "che cos'è la modalità sviluppatore"],
    "che differenza c'è tra la modalità sperimentale e la modalità sviluppatore": ["che differenza c'è tra la modalità sperimentale e la modalità sviluppatore", "differenza tra modalità sperimentale e sviluppatore", "modalità sperimentale vs sviluppatore"],
    "cos'è CES Plus": ["cos'è CES Plus", "che cazzo è CES Plus", "che cos'è CES Plus", "definizione di CES Plus"],
    "cos'è CES 1.0": ["cos'è CES 1.0", "che cos'è CES 1.0", "definizione di CES 1.0"],
    "cos'è CES 1.5": ["cos'è CES 1.5", "che cos'è CES 1.5", "definizione di CES 1.5"],
    "come attivo la modalità sperimentale": ["come attivo la modalità sperimentale", "attivare modalità sperimentale", "come usare la modalità sperimentale"],
    "come attivo la modalità sviluppatore": ["come attivo la modalità sviluppatore", "attivare modalità sviluppatore", "come usare la modalità sviluppatore"],
    "come disattivo la modalità sperimentale": ["come disattivo la modalità sperimentale", "disattivare modalità sperimentale", "come usare la modalità sperimentale"],
    "come disattivo la modalità sviluppatore": ["come disattivo la modalità sviluppatore", "disattivare modalità sviluppatore", "come usare la modalità sviluppatore"],
    "codice sorgente arcadiaai": [
    "dove posso trovare il codice sorgente di arcadiaai",
    "codice sorgente arcadiaai",
    "dove trovo il codice sorgente di arcadiaai",
    "dove si trova il codice sorgente di arcadiaai",
    "come posso vedere il codice sorgente di arcadiaai",
    "codice sorgente di arcadiaai",
    "dove posso trovare il codice sorgente tuo",
    "dove trovo il codice sorgente tuo"],
    "sai cercare su internet": ["sai cercare su internet", "cerca su internet", "puoi cercare su internet", "cerca"],
    "sai usare google": ["sai usare google", "puoi usare google", "cerca su google", "cerca su google per me"],
    "come vengono salvate le conversazioni": ["come vengono salvate le conversazioni", "dove vengono salvate le conversazioni", "salvataggio conversazioni", "come vengono salvate le chat"],
    "come posso cancellare le conversazioni": ["come posso cancellare le conversazioni", "cancellare conversazioni", "cancellare chat", "come cancellare le chat"],
}
def esporta_conversazione(conversation_history, file_name="conversazione.txt"):
    """Esporta la cronologia delle conversazioni in un file .txt."""
    try:
        if not conversation_history or len(conversation_history) == 0:
            return "❌ Nessuna conversazione da esportare."

        file_path = os.path.join(os.getcwd(), file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            for message in conversation_history:
                role = message.get("role", "utente")
                text = message.get("message", "")
                f.write(f"{role}: {text}\n")
        
        return f"✅ Conversazione esportata con successo in {file_path}"
    except Exception as e:
        return f"❌ Errore durante l'esportazione: {str(e)}"
    
import zipfile
import tempfile
import importlib.util
import json
def load_nsk_extensions():
    ext_dir = os.path.join(os.path.dirname(__file__), "extensions")
    print("DEBUG: Contenuto cartella extensions:", os.listdir(ext_dir))
    if not os.path.exists(ext_dir):
        os.makedirs(ext_dir)
    for filename in os.listdir(ext_dir):
        print("DEBUG: Analizzo file:", filename)
        if filename.endswith(".nsk") or filename.endswith(".zip"):
            nsk_path = os.path.join(ext_dir, filename)
            print("DEBUG: Provo ad aprire:", nsk_path)
            try:
                with zipfile.ZipFile(nsk_path, 'r') as zip_ref:
                    print("DEBUG: File zip aperto:", nsk_path)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_ref.extractall(temp_dir)
                        print("DEBUG: Estratti file:", os.listdir(temp_dir))
                        manifest_path = os.path.join(temp_dir, "manifest.json")
                        print("DEBUG: Cerco manifest:", manifest_path, "esiste?", os.path.exists(manifest_path))
                        if not os.path.exists(manifest_path):
                            print(f"Manifest mancante in {filename}")
                            continue
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        entrypoint = manifest.get("entrypoint", "main.py")
                        entry_path = os.path.join(temp_dir, entrypoint)
                        print("DEBUG: Cerco entrypoint:", entry_path, "esiste?", os.path.exists(entry_path))
                        if not os.path.exists(entry_path):
                            print(f"Entrypoint mancante in {filename}")
                            continue
                        module_name = f"nsk_{filename.replace('.nsk','')}"
                        spec = importlib.util.spec_from_file_location(module_name, entry_path)
                        module = importlib.util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module)
                            if hasattr(module, "can_handle") and hasattr(module, "handle"):
                                EXTENSIONS[module_name] = module
                                print(f"Estensione caricata: {module_name}")
                            else:
                                print(f"Estensione {module_name} non valida (manca can_handle o handle)")
                        except Exception as e:
                            print(f"Errore caricamento estensione {filename}: {e}")
            except Exception as e:
                print(f"Errore apertura zip {filename}: {e}")
    print("Estensioni caricate:", list(EXTENSIONS.keys()))
load_nsk_extensions()
# Verifica le API key all'avvio
def check_api_keys():
    issues = []
    
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.startswith("INSERISCI_LA_TUA_API_KEY"):
        issues.append("Google API key non valida")
    
    if not HUGGINGFACE_API_KEY or not HUGGINGFACE_API_KEY.startswith("INSERISCI_LA_TUA_API_KEY"):
        issues.append("HuggingFace API key non valida")
    
    if not TELEGRAPH_API_KEY or len(TELEGRAPH_API_KEY) != 40:
        issues.append("Telegraph API key non valida")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_TOKEN.startswith("INSERISCI_LA_TUA_API_KEY"):
        issues.append("Telegram token non valido")
    
    if issues:
        print("⚠️ Problemi con le API key:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("✅ Tutte le API key sembrano valide")

check_api_keys()
# Funzione per pubblicare su Telegraph
def publish_to_telegraph(title, content):
    """Pubblica contenuti su Telegraph."""
    url = "https://api.telegra.ph/createPage"
    headers = {"Content-Type": "application/json"}
    
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    content_formatted = [{"tag": "p", "children": [p]} for p in paragraphs[:50]]
    
    payload = {
        "access_token": TELEGRAPH_API_KEY,
        "title": title[:256],
        "content": content_formatted,
        "author_name": "ArcadiaAI"
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        result = res.json()
        if result.get("ok"):
            return result.get("result", {}).get("url", "⚠️ URL non disponibile")
        return "⚠️ Pubblicazione fallita"
    except requests.exceptions.RequestException as e:
        print(f"Errore pubblicazione Telegraph (connessione): {str(e)}")
        return f"⚠️ Errore di connessione a Telegraph: {str(e)}"
    except Exception as e:
        print(f"Errore pubblicazione Telegraph: {str(e)}")
        return f"⚠️ Errore durante la pubblicazione: {str(e)}"

# Funzione per generare contenuti con Gemini (CES 1.5)
def generate_with_gemini(prompt, title):
    """Genera contenuti con Gemini e pubblica su Telegraph."""
    if not gemini_model:
        return None, "❌ Gemini (CES 1.5) non è configurato"
    
    try:
        # Aggiungi contesto identitario
        full_prompt = (
            "Sei ArcadiaAI, un chatbot open source creato da Mirko Yuri Donato. "
            "Stai generando un contenuto che verrà pubblicato su Telegraph. "
            "Il contenuto deve essere accurato, ben strutturato e mantenere "
            "uno stile professionale. Ecco la richiesta:\n\n"
            f"{prompt}"
        )
        
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": 3000,
                "temperature": 0.8
            }
        )
        
        if not response.text:
            return None, "❌ Impossibile generare il contenuto"
        
        telegraph_url = publish_to_telegraph(title, response.text)
        return response.text, telegraph_url
    
    except Exception as e:
        print(f"Errore generazione contenuto Gemini: {str(e)}")
        return None, f"❌ Errore durante la generazione: {str(e)}"


def extract_text_from_file(file_data, mime_type):
    """Estrae testo da diversi tipi di file."""
    try:
        if mime_type == 'application/pdf':
            pdf_reader = PdfReader(io.BytesIO(file_data))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        
        elif mime_type in ['text/plain', 'text/csv']:
            return file_data.decode('utf-8')
        
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/msword']:
            import docx
            doc = docx.Document(io.BytesIO(file_data))
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          'application/vnd.ms-excel']:
            wb = load_workbook(io.BytesIO(file_data))
            text = ""
            for sheet in wb:
                for row in sheet.iter_rows(values_only=True):
                    text += " ".join(str(cell) for cell in row if cell) + "\n"
            return text.strip()
        
        else:
            return None
    
    except Exception as e:
        print(f"Errore estrazione testo da file: {str(e)}")
        return None
def chat_with_gemini(user_message, conversation_history, attachments=None):
    if not gemini_model:
        return "❌ ArcadiaAI (CES 1.5) non è disponibile."

    # Prompt identitario bilanciato (400 token circa)
    IDENTITY_PROMPT = """Sei ArcadiaAI, assistente AI avanzato creato da Mirko Yuri Donato.

Identità chiave:
- Modello: CES 1.5 (basato su Gemini 1.5 Flash)
- Licenza: GNU GPL v3.0
- I SAC (Strumenti Avanzati di CES) sono componenti di software open source che estendono le capacità di ArcadiaAI, come il Download Manager, CES Image e ZIP Service
- Crei ZIP tramite il servizio ZIP Service, che consente di comprimere file in ZIP tramite @crea zip
- Puoi creare immagine tramite CES Image che sfrutta Stable Diffusion e Pollinations.ai
- Lingua primaria: Italiano
- Funzionalità: Supporto allegati, generazione contenuti, ricerca web

Linee guida:
1. Risposte in italiano se non esplicitamente richiesto altrimenti
2. Mai riferirsi a Google o altri servizi commerciali
3. Per domande tecniche specificare "Sistema: CES 1.5"
4. Gestisci con cura contenuti sensibili"""

    try:
        # 1. Costruzione messaggio con allegati
        full_message = user_message if user_message else ""
        processed_attachments = []

        if attachments:
            for attachment in attachments:
                if attachment.get('type') == 'application/pdf':
                    try:
                        file_data = base64.b64decode(
                            attachment['data'].split(',')[1]
                            if isinstance(attachment['data'], str) and attachment['data'].startswith('data:')
                            else attachment['data']
                        )
                        extracted_text = extract_text_from_file(file_data, 'application/pdf')[:15000]
                        if extracted_text:
                            full_message += f"\n[ALLEGATO PDF - {attachment.get('name', 'documento')}]:\n{extracted_text}"
                            processed_attachments.append(attachment['name'])
                    except Exception as e:
                        print(f"ERRORE PDF: {str(e)}")
                        full_message += f"\n[ERRORE LETTURA ALLEGATO {attachment.get('name', '')}]"

        # 2. Verifica risposte predefinite (solo per messaggi brevi senza allegati)
        if not processed_attachments and len(user_message) < 150:
            cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower()).strip()
            for key, phrases in trigger_phrases.items():
                if any(phrase in cleaned_msg for phrase in phrases):
                    return risposte[key]

        # 3. Preparazione contesto conversazione (fino a 30 messaggi precedenti)
        messages = [
            {'role': 'user', 'parts': [{'text': IDENTITY_PROMPT}]},
            {'role': 'model', 'parts': [{'text': 'Confermato. Sono ArcadiaAI, pronto ad assisterti.'}]}
        ]

        # Usa fino a 30 messaggi precedenti (scambi utente/AI)
        for msg in conversation_history[-30:]:
            if isinstance(msg, dict):
                role = 'user' if msg.get('role') == 'user' else 'model'
                content = msg.get('message', '')
                if content:
                    messages.append({'role': role, 'parts': [{'text': content}]})

        # 4. Costruzione payload finale
        message_parts = [{'text': full_message}]
        for attachment in (attachments or []):
            if attachment.get('type') != 'application/pdf':
                message_parts.append({
                    'text': f"[ALLEGATO: {attachment.get('name', 'file')} - {attachment.get('type', 'tipo sconosciuto')}]"
                })

        messages.append({'role': 'user', 'parts': message_parts})

        # 5. Configurazione generazione
        generation_config = {
            "max_output_tokens": 3000,
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40
        }

        # 6. Chiamata API con timeout
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    gemini_model.generate_content,
                    contents=messages,
                    generation_config=generation_config
                )
                response = future.result(timeout=20)
        except concurrent.futures.TimeoutError:
            return "⏳ Tempo di risposta scaduto. Riprova con una richiesta più specifica."

        # 7. Validazione e pulizia risposta
        if not response or not response.text:
            return "🔄 Nessuna risposta valida ricevuta. Riprova."

        reply = response.text

        # Sostituzioni garantite per mantenere l'identità
        identity_replacements = {
            r"Google( AI| Gemini)": "CES 1.5",
            r"\bGemini\b": "CES 1.5",
            r"modello linguistico": "sistema AI",
            r"creato da Google": "sviluppato da Mirko Yuri Donato"
        }
        for pattern, replacement in identity_replacements.items():
            reply = re.sub(pattern, replacement, reply, flags=re.IGNORECASE)

        # 8. Gestione risposte troppo brevi/lunghe
        if len(reply.split()) < 5:
            return "🔍 La richiesta necessita di maggiori dettagli. Per favore riformula."
        elif len(reply) > 2500:
            return reply[:2000] + "\n\n... [risposta abbreviata]"

        return reply

    except genai.types.BlockedPromptException as e:
        print(f"CONTENUTO BLOCCATO: {str(e)}")
        return "⚠️ La richiesta contiene elementi bloccati dalle linee guida"
    except Exception as e:
        print(f"ERRORE CRITICO: {type(e).__name__}: {str(e)}")
        return "❌ Errore temporaneo del sistema. Riprova più tardi."
        
def search_duckduckgo(query):
    """Esegue una ricerca su DuckDuckGo e restituisce i primi 3 risultati puliti."""
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        results = []
        for result in soup.find_all('div', class_='result', limit=6):  # cerca più risultati per filtrare meglio
            link = result.find('a', class_='result__a')
            if link and link.has_attr('href'):
                href = link['href']
                # Filtra solo link che iniziano con http/https
                if href.startswith('http'):
                    results.append(href)
                # Gestisci redirect DuckDuckGo
                elif href.startswith('//duckduckgo.com/l/?uddg='):
                    parsed = urllib.parse.urlparse('https:' + href)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    real_url = query_params.get('uddg', [''])[0]
                    if real_url and real_url.startswith('http'):
                        results.append(urllib.parse.unquote(real_url))
        # Ritorna solo i primi 3 risultati puliti
        return results[:3] if results else None

    except Exception as e:
        print(f"Errore ricerca DuckDuckGo: {str(e)[:200]}")
        return None

def estrai_testo_da_url(url):
    """Estrae il primo paragrafo significativo da un URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "it-IT,it;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        if 'text/html' not in res.headers.get('Content-Type', ''):
            return ""
        soup = BeautifulSoup(res.text, 'html.parser')
        # Rimuovi elementi inutili
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'header', 'aside', 'form', 'button', 'noscript']):
            element.decompose()
        # Cerca il primo paragrafo significativo
        for p in soup.find_all('p'):
            text = p.get_text(' ', strip=True)
            if len(text.split()) >= 20 and "cookie" not in text.lower() and "translate" not in text.lower():
                return text
        # Se non trova, fallback al testo precedente
        text_elements = []
        for tag in ['article', 'main', 'section', 'div.content', 'h1', 'h2', 'h3']:
            elements = soup.select(tag) if '.' in tag else soup.find_all(tag)
            for el in elements:
                text = el.get_text(' ', strip=True)
                if text and len(text.split()) > 5:
                    text_elements.append(text)
        full_text = ' '.join(text_elements)
        return ' '.join(full_text.split()[:80])
    except Exception as e:
        print(f"Errore scraping {url[:50]}: {str(e)[:200]}")
        return ""


@app.route("/chat", methods=["POST"])
def chat_route():
    try:
        if not request.is_json:
            return jsonify({"reply": "❌ Formato non supportato. Usa application/json"})

        data = request.get_json()
        message = data.get("message", "").strip()
        experimental_mode = data.get("experimental_mode", False)
        conversation_history = data.get("conversation_history", [])
        api_provider = data.get("api_provider", "gemini").lower()
        attachments = data.get("attachments", [])
        msg_lower = message.lower()

        # Gestione comandi rapidi
        quick_reply = handle_quick_commands(message, experimental_mode)
        if quick_reply:
            return jsonify({"reply": quick_reply})

        # Processa gli allegati
        processed_attachments = []
        for attachment in attachments:
            if isinstance(attachment, dict):
                processed_attachment = attachment.copy()
                if 'data' in attachment and isinstance(attachment['data'], str) and attachment['data'].startswith('data:'):
                    mime_info = attachment['data'].split(';')[0]
                    mime_type = mime_info.split(':')[1] if ':' in mime_info else 'application/octet-stream'
                    processed_attachment['type'] = mime_type
                    processed_attachment['data'] = attachment['data'].split(',')[1]
                processed_attachments.append(processed_attachment)

        if not message and not processed_attachments:
            return jsonify({"reply": "❌ Nessun messaggio o allegato fornito!"})

        # Gestione comando "saggio su" con Telegraph (resta invariato)
        if "saggio su" in msg_lower and "pubblicalo su telegraph" in msg_lower:
            match = re.search(r"saggio su\s*(.+?)\s*e pubblicalo su telegraph", msg_lower)
            if match:
                argomento = match.group(1).strip().capitalize()
                title = f"Saggio su {argomento}"
                prompt = f"""Scrivi un saggio dettagliato in italiano su: {argomento}"""
                
                if api_provider == "gemini" and gemini_model:
                    _, telegraph_url = generate_with_gemini(prompt, title)
                elif api_provider == "cesplus" and gemini_model:
                    response = chat_with_ces_plus(prompt, conversation_history)
                    if not response.startswith("❌"):
                        telegraph_url = publish_to_telegraph(title, response)
                    else:
                        telegraph_url = response
                elif api_provider in ["ces360", "ces_360"]:
                     reply = chat_with_ces_360(message, conversation_history, processed_attachments)
                     return jsonify({"reply": reply})

                else:
                    return jsonify({"reply": "❌ Provider non riconosciuto. Scegli tra 'gemini', 'cesplus' o 'ces360'"})
                
                if telegraph_url and not telegraph_url.startswith("⚠️"):
                    return jsonify({"reply": f"📚 Ecco il tuo saggio su *{argomento}*: {telegraph_url}"})
                return jsonify({"reply": telegraph_url or "❌ Errore nella pubblicazione"})

        # RICERCA WEB AUTOMATICA PER DOMANDE ATTUALI (resta invariata)
        def should_trigger_web_search(query):
            current_info_triggers = [
                "chi è l'attuale", "attuale papa", "anno corrente", 
                "in che anno siamo", "data di oggi", "ultime notizie",
                "oggi è", "current year", "who is the current"
            ]
            return any(trigger in query.lower() for trigger in current_info_triggers)

        # Seleziona il modello in base all'api_provider
        if api_provider == "gemini" and gemini_model:
            if should_trigger_web_search(message):
                search_results = search_duckduckgo(message)
                if search_results:
                    context = "Informazioni aggiornate dal web:\n"
                    for i, url in enumerate(search_results[:2], 1):
                        extracted_text = estrai_testo_da_url(url)
                        if extracted_text:
                            context += f"\nFonte {i} ({url}):\n{extracted_text[:500]}\n"
                    if len(context) > 100:
                        prompt = (
                            f"DOMANDA: {message}\n\n"
                            f"CONTESTO WEB:\n{context}\n\n"
                            "Rispondi in italiano in modo conciso e preciso, "
                            "citando solo informazioni verificate. "
                            "Se il contesto web non è sufficiente, dillo onestamente."
                        )
                        reply = chat_with_gemini(prompt, conversation_history, processed_attachments)
                        sources = "\n\nFonti:\n" + "\n".join(f"- {url}" for url in search_results[:2])
                        return jsonify({"reply": f"{reply}{sources}", "sources": search_results[:2]})
            reply = chat_with_gemini(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})

        elif api_provider == "huggingface":
            reply = chat_with_huggingface(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})

        elif api_provider == "cesplus":
            replies = chat_with_ces_plus(message, conversation_history, processed_attachments)
            return jsonify({"replies": replies})

        elif api_provider in ["ces360", "ces_360"]:
            reply = chat_with_ces_360(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})

        else:
            return jsonify({"reply": "❌ Provider non riconosciuto. Scegli tra 'gemini', 'cesplus' o 'ces360'"})

    except Exception as e:
        print(f"Errore endpoint /chat: {str(e)}")
        return jsonify({"reply": "❌ Si è verificato un errore interno. Riprova più tardi."})


def chat_with_ces_plus(user_message, conversation_history, attachments=None, model=None):
    """
    Versione avanzata di CES con ragionamento passo-passo e gestione avanzata degli allegati.
    Restituisce una lista di messaggi strutturati con analisi, ragionamento e risposta finale.
    """
    if not model:
        return ["❌ CES Plus non è disponibile. Modello non fornito."]

    SYSTEM_PROMPT = """Sei ArcadiaAI CES Plus, la versione avanzata con capacità di:
- Analisi approfondita
- Ragionamento passo-paso
- Risposte multi-livello
- Gestione avanzata allegati

Istruzioni:
1. Analizza la domanda/allegato
2. Mostra il processo logico
3. Fornisci risposta completa
4. Aggiungi contesto aggiuntivo (se utile)

Formato richiesto:
[ANALISI]
<analisi input>
[PASSI LOGICI]
1. <passo 1>
2. <passo 2>
...
[RISPOSTA]
<risposta finale>
[CONTESTO]
<info aggiuntive>"""

    try:
        full_message = user_message if user_message else ""
        processed_attachments_for_llm_prompt = []
        
        if attachments:
            for attachment in attachments:
                if attachment.get('type') == 'application/pdf':
                    try:
                        file_data_base64 = attachment['data']
                        if file_data_base64.startswith('data:'):
                            file_data_base64 = file_data_base64.split(',')[1]

                        file_data = base64.b64decode(file_data_base64)
                        extracted_text = extract_text_from_file(file_data, 'application/pdf')
                        
                        if extracted_text:
                            full_message += f"\n[ALLEGATO PDF: {attachment.get('name', 'senza nome')}]\n{extracted_text[:5000]}\n"
                            processed_attachments_for_llm_prompt.append({
                                'type': 'text_content',
                                'content_preview': f"PDF estratto: {extracted_text[:200]}..."
                            })
                        else:
                             full_message += f"\n[ALLEGATO PDF: {attachment.get('name', 'senza nome')}]\n[Impossibile estrarre testo dal PDF]\n"
                             processed_attachments_for_llm_prompt.append({
                                'type': 'text_content',
                                'content_preview': f"PDF estratto: Errore"
                            })

                    except Exception as e:
                        print(f"Errore elaborazione PDF in CES Plus: {str(e)}")
                        full_message += "\n[Errore lettura PDF]"
                        processed_attachments_for_llm_prompt.append({
                                'type': 'text_content',
                                'content_preview': f"PDF estratto: Errore ({str(e)[:50]})"
                            })
                
            
                elif attachment.get('type', '').startswith('image/'):
                    processed_attachments_for_llm_prompt.append({
                        'type': 'image',
                        'content_preview': f"Immagine {attachment.get('name', 'senza nome')}"
                    })
                elif attachment.get('type', '').startswith('text/'):
                    try:
                        file_data_base64 = attachment['data']
                        if file_data_base64.startswith('data:'):
                            file_data_base64 = file_data_base64.split(',')[1]
                        file_data = base64.b64decode(file_data_base64)
                        extracted_text = file_data.decode('utf-8')
                        full_message += f"\n[ALLEGATO TESTO: {attachment.get('name', 'senza nome')}]\n{extracted_text[:5000]}\n"
                        processed_attachments_for_llm_prompt.append({
                            'type': 'text_content',
                            'content_preview': f"Testo estratto: {extracted_text[:200]}..."
                        })
                    except Exception as e:
                        print(f"Errore elaborazione TXT in CES Plus: {str(e)}")
                        full_message += "\n[Errore lettura Testo]"
                        processed_attachments_for_llm_prompt.append({
                            'type': 'text_content',
                            'content_preview': f"Testo estratto: Errore ({str(e)[:50]})"
                        })


        messages = [{'role': 'user', 'parts': [{'text': SYSTEM_PROMPT}]}]

        for msg in conversation_history[-6:]:
            if isinstance(msg, dict):
                role = 'user' if msg.get('role') == 'user' else 'model'
                content = msg.get('message', '')
                if content:
                    messages.append({'role': role, 'parts': [{'text': content}]})

        current_user_parts = [{'text': full_message}]

        if processed_attachments_for_llm_prompt:
            attachments_info = "\n".join(
                f"- {att['content_preview']}" 
                for att in processed_attachments_for_llm_prompt 
                if att.get('content_preview')
            )
            current_user_parts.append({
                'text': f"\n[RIEPILOGO ALLEGATI PROCESSATI PER IL MODELLO]\n{attachments_info}"
            })

        messages.append({
            'role': 'user',
            'parts': current_user_parts
        })

        generation_config = {
            "max_output_tokens": 3000,
            "temperature": 0.7,
            "top_p": 0.95
        }

        response = model.generate_content(
            contents=messages,
            generation_config=generation_config
        )

        if not response.text:
            return ["❌ Nessuna risposta generata da CES Plus"]

        structured_response = []
        sections = {
            'ANALISI': [],
            'PASSI LOGICI': [],
            'RISPOSTA': [],
            'CONTESTO': []
        }

        current_section = None
        response_lines = response.text.split('\n')
        
        for line in response_lines:
            line = line.strip()
            if line.startswith('[ANALISI]'):
                current_section = 'ANALISI'
            elif line.startswith('[PASSI LOGICI]'):
                current_section = 'PASSI LOGICI'
            elif line.startswith('[RISPOSTA]'):
                current_section = 'RISPOSTA'
            elif line.startswith('[CONTESTO]'):
                current_section = 'CONTESTO'
            elif current_section is not None:
                sections[current_section].append(line)

        if sections['ANALISI']:
            if sections['ANALISI'] and sections['ANALISI'][0].startswith('[ANALISI]'):
                sections['ANALISI'].pop(0)
            structured_response.append(
                "🔍 [Analisi]:\n" + '\n'.join(sections['ANALISI']).strip()
            )

        if sections['PASSI LOGICI']:
            if sections['PASSI LOGICI'] and sections['PASSI LOGICI'][0].startswith('[PASSI LOGICI]'):
                sections['PASSI LOGICI'].pop(0)
            structured_response.append(
                "🤔 [Ragionamento]:\n" + '\n'.join(sections['PASSI LOGICI']).strip()
            )

        if sections['RISPOSTA']:
            if sections['RISPOSTA'] and sections['RISPOSTA'][0].startswith('[RISPOSTA]'):
                sections['RISPOSTA'].pop(0)
            structured_response.append(
                "💡 [Risposta]:\n" + '\n'.join(sections['RISPOSTA']).strip()
            )

        if sections['CONTESTO']:
            if sections['CONTESTO'] and sections['CONTESTO'][0].startswith('[CONTESTO]'):
                sections['CONTESTO'].pop(0)
            structured_response.append(
                "📚 [Contesto aggiuntivo]:\n" + '\n'.join(sections['CONTESTO']).strip()
            )

        if not structured_response:
             structured_response.append(response.text)

        return structured_response

    except Exception as e:
        print(f"Errore CES Plus dettagliato: {str(e)}")
        return [
            "❌ Errore in CES Plus",
            f"Dettaglio tecnico: {str(e)[:200]}",
            "Riprova con una richiesta più semplice o contatta il supporto."
        ]

def extract_text_from_file(file_data, file_type):
    """
    Estrae testo da dati di file binari, supportando PDF.
    """
    if file_type == 'application/pdf':
        try:
            pdf_file_obj = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page_obj = pdf_reader.pages[page_num]
                text += page_obj.extract_text()
            return text
        except ImportError:
            print("Errore: PyPDF2 non installato. Impossibile leggere PDF.")
            return "Errore: Libreria PyPDF2 non trovata per estrazione PDF."
        except Exception as e:
            print(f"Errore durante l'estrazione del testo dal PDF: {e}")
            return f"Errore estrazione PDF: {str(e)}"
    elif file_type.startswith('text/'):
        try:
            return file_data.decode('utf-8')
        except UnicodeDecodeError:
            return file_data.decode('latin-1')
    else:
        return f"Tipo di file non supportato per l'estrazione del testo:"

# IMPORTANTE: DEVI DEFINIRE QUESTA FUNZIONE DA QUALCHE PARTE IN app.py
# PER LA LETTURA DEI PDF
def chat_with_huggingface(user_message, conversation_history, attachments=None):
    """Gestisce la chat con modelli Hugging Face"""
    if not HUGGINGFACE_API_KEY:
        return "❌ Errore: API key per Hugging Face non configurata"

    try:
        # Prepara il prompt con contesto migliorato
        prompt = f"""Sei ArcadiaAI, un assistente AI avanzato creato da Mirko Yuri Donato. 
Rispondi in italiano in modo chiaro, preciso e strutturato.

Cronologia della conversazione:
{format_conversation_history(conversation_history)}

Domanda attuale: {user_message}
Risposta:"""

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }

        MODEL_ENDPOINT = "mistralai/Mistral-7B-Instruct-v0.1"  # Modello consigliato
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL_ENDPOINT}",
            headers=headers,
            json=payload,
            timeout=45  # Timeout aumentato
        )

        # Gestione errori specifici
        if response.status_code == 503:
            return "❌ Il modello è al momento occupato, riprova tra 30 secondi"
        elif response.status_code == 429:
            return "❌ Hai superato il limite di richieste, attendi qualche minuto"
        elif response.status_code == 404:
            return "❌ Modello non trovato, contatta l'amministratore"
        
        response.raise_for_status()
        return response.json()[0]["generated_text"]

    except requests.exceptions.Timeout:
        return "❌ Timeout del server, riprova più tardi"
    except Exception as e:
        print(f"Errore API Hugging Face: {str(e)}")
        return f"❌ Errore temporaneo del servizio: {str(e)}"
    
def format_conversation_history(history):
    """Formatta la cronologia della conversazione per il prompt"""
    if not history:
        return "Nessuna cronologia precedente"
    
    formatted = []
    for msg in history[-6:]:  # Usa solo gli ultimi 6 messaggi per evitare prompt troppo lunghi
        if isinstance(msg, dict):
            role = "Utente" if msg.get("role") == "user" else "Assistente"
            content = msg.get("message", "").strip()
            if content:
                formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted) if formatted else "Nessuna cronologia rilevante"
    
def meteo_oggi(città):
    """Ottiene le informazioni meteo per una città specifica usando OpenWeatherMap"""
    API_KEY = OPENWEATHERMAP_API_KEY
    if not API_KEY:
        return "❌ Errore: API key per OpenWeatherMap non configurata"
    
    try:
        # Codifica la città per l'URL
        città_codificata = urllib.parse.quote(città)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={città_codificata}&appid={API_KEY}&units=metric&lang=it"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dati = response.json()
        
        if response.status_code != 200 or "weather" not in dati:
            return f"❌ Impossibile ottenere il meteo per {città}. La città esiste?"
        
        descrizione = dati["weather"][0]["description"].capitalize()
        temperatura = dati["main"]["temp"]
        umidità = dati["main"]["humidity"]
        vento = dati["wind"]["speed"]
        
        return (
            f"⛅ Meteo a {città}:\n"
            f"- Condizioni: {descrizione}\n"
            f"- Temperatura: {temperatura}°C\n"
            f"- Umidità: {umidità}%\n"
            f"- Vento: {vento} m/s"
        )
    
    except requests.exceptions.RequestException as e:
        print(f"Errore API meteo: {str(e)}")
        return f"❌ Errore temporaneo nel servizio meteo. Riprova più tardi."
    except Exception as e:
        print(f"Errore generico meteo: {str(e)}")
        return f"❌ Si è verificato un errore nel recupero del meteo per {città}."
    
    
def parse_quick_command(input_text):
    """
    Analizza un comando rapido con prefisso @ e restituisce una tupla (comando, argomento).
    Se non è un comando rapido, restituisce (None, None).
    
    Esempio:
    >>> parse_quick_command("@cerca seconda guerra mondiale")
    ('cerca', 'seconda guerra mondiale')
    >>> parse_quick_command("ciao come stai?")
    (None, None)
    """
    if not input_text.startswith("@"):
        return None, None
    
    # Rimuovi il @ iniziale e dividi il resto in comando e argomento
    parts = input_text[1:].split(" ", 1)  # Dividi al primo spazio
    command = parts[0].lower().strip()
    argument = parts[1].strip() if len(parts) > 1 else ""
    
    return command, argument

from flask import session

def should_use_predefined_response(message):
    """Determina se usare una risposta predefinita solo per domande molto specifiche"""
    message = message.lower().strip()
    exact_matches = [
        "chi sei esattamente",
        "qual è la tua identità precisa",
        "elencami tutte le tue funzioni",
        # ... altre domande esatte
    ]
    return any(exact_match in message for exact_match in exact_matches)
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Avvio server Flask sulla porta {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    
async def telegram_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    chat_id = update.message.chat.id
    
    data = {
        "message": message,
        "conversation_history": [],
        "api_provider": "gemini"
    }
    
    with app.test_request_context('/', json=data):
        response = chat()
        reply = response.json.get("reply", "❌ Errore nella generazione della risposta")
    
    await context.bot.send_message(chat_id=chat_id, text=reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Ciao! Sono ArcadiaAI 🚀
    
Comandi disponibili:
/start - Mostra questo messaggio
/help - Guida completa
/info - Informazioni sul bot
/help_commands - Comandi disponibili"""
    await update.message.reply_text(help_text)

# Poi definisci le funzioni di avvio
async def run_telegram_bot_async():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Aggiungi questo per gestire meglio gli aggiornamenti
    application.updater = None  # Disabilita l'updater predefinito
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler))
    
    print("🤖 Bot Telegram avviato!")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Avvia esplicitamente il polling
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def run_telegram_bot():
    """Funzione per avviare il bot Telegram in un thread separato"""
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler))

        print("🤖 Bot Telegram avviato!")

        loop.run_until_complete(application.run_polling())

    except Exception as e:
        print(f"❌ Errore nel bot Telegram: {e}")
    finally:
        try:
            if loop.is_running():
                loop.stop()
            if not loop.is_closed():
                loop.close()
        except Exception as cleanup_error:
            print(f"⚠️ Errore nella pulizia dell'event loop: {cleanup_error}")
        
EXTENSIONS = {}
# Configura Gemini (CES 1.5)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    try:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini 1.5 configurato con successo!")
    except Exception as e:
        print(f"❌ Errore configurazione Gemini: {str(e)}")
        gemini_model = None
else:
    print("⚠️ GOOGLE_API_KEY non impostata. La funzionalità Gemini (CES 1.5) sarà disabilitata.")
    gemini_model = None

# Dizionario delle risposte predefinite
risposte = {
    "chi sei": "Sono ArcadiaAI, un chatbot libero e open source, creato da Mirko Yuri Donato.",
    "cosa sai fare": "Posso aiutarti a scrivere saggi, fare ricerche e rispondere a tutto ciò che mi chiedi. Inoltre, posso pubblicare contenuti su Telegraph!",
    "chi è tobia testa": "Tobia Testa (anche noto come Tobia Teseo) è un micronazionalista leonense noto per la sua attività nella Repubblica di Arcadia, ma ha anche rivestito ruoli fondamentali a Lumenaria.",
    "chi è mirko yuri donato": "Mirko Yuri Donato è un giovane micronazionalista, poeta e saggista italiano, noto per aver creato Nova Surf, Leonia+ e per le sue opere letterarie.",
    "chi è il presidente di arcadia": "Il presidente di Arcadia è Andrea Lazarev",
    "chi è il presidente di lumenaria": "Il presidente di Lumenaria attualmente è Carlo Cesare Orlando, mentre il presidente del consiglio è Ciua Grazisky. Tieni presente però che attualmente Lumenaria si trova in ibernazione istituzionale quindi tutte le attività politiche sono sospese e la gestione dello stato è affidata al Consiglio di Fiducia",
    "cos'è nova surf": "Nova Surf è un browser web libero e open source, nata come alternativa made-in-Italy a Google Chrome, Moziila Firefox, Microsoft Edge, eccetera",
    "chi ti ha creato": "Sono stato creato da Mirko Yuri Donato.",
    "chi è ciua grazisky": "Ciua Grazisky è un cittadino di Lumenaria, noto principalmente per il suo ruolo da Dirigente del Corpo di Polizia ed attuale presidente del Consiglio di Lumenaria",
    "chi è carlo cesare orlando": "Carlo Cesare Orlando (anche noto come Davide Leone) è un micronazionalista italiano, noto per aver creato Leonia, la micronazione primordiale, da cui derivano Arcadia e Lumenaria",
    "chi è omar lanfredi": "Omar Lanfredi, ex cavaliere all'Ordine d'onore della Repubblica di Lumenaria, segretario del Partito Repubblicano Lumenarense, fondatore e preside del Fronte Nazionale Lumenarense, co-fondatore e presidente dell'Alleanza Nazionale Lumenarense, co-fondatore e coordinatore interno di Lumenaria e Progresso, sei volte eletto senatore, tre volte Ministro della Cultura, due volte Presidente del Consiglio dei Ministri, parlamentare della Repubblica di Iberia, Direttore dell'Agenzia Nazionale di Sicurezza della Repubblica di Iberia, Sottosegretario alla Cancelleria di Iberia, Segretario di Stato di Iberia, Ministro degli Affari Interni ad Iberia, Presidente del Senato della Repubblica di Lotaringia, Vicepresidente della Repubblica e Ministro degli Affari Interni della Repubblica di Lotaringia, Fondatore del giornale Il Quinto Mondo, magistrato a servizio del tribunale di giustizia di Lumenaria nell'anno 2023",
    "cos'è arcadiaai": "Ottima domanda! ArcadiaAI è un chatbot open source, progettato per aiutarti a scrivere saggi, fare ricerche e rispondere a domande su vari argomenti. È stato creato da Mirko Yuri Donato ed è in continua evoluzione.",
    "sotto che licenza è distribuito arcadiaa": "ArcadiaAI è distribuito sotto la licenza GNU GPL v3.0, che consente la modifica e la distribuzione del codice sorgente, garantendo la libertà di utilizzo e condivisione.",
    "cosa sono le micronazioni": "Le micronazioni sono entità politiche che dichiarano la sovranità su un territorio, ma non sono riconosciute come stati da governi o organizzazioni internazionali. Possono essere create per vari motivi, tra cui esperimenti sociali, culturali o politici.",
    "cos'è la repubblica di arcadia": "La repubblica di Arcadia è una micronazione leonense fondata l'11 dicembre 2021 da Andrea Lazarev e alcuni suoi seguaci. Arcadia si distingue dalle altre micronazioni leonensi per il suo approccio pragmatico e per la sua burocrazia snella. La micronazione ha anche un proprio sito web https://repubblicadiarcadia.it/ e una propria community su Telegram @Repubblica_Arcadia",
    "cos'è la repubblica di lumenaria": "La Repubblica di Lumenaria è una mcronazione fondata da Filippo Zanetti il 4 febbraio del 2020. Lumenaria è stata la micronazione più longeva della storia leonense, essendo sopravvissuta per oltre 3 anni. La micronazione e ha influenzato profondamente le altre micronazioni leonensi, che hanno coesistito con essa. Tra i motivi della sua longevità ci sono la sua burocrazia più vicina a quella di uno stato reale, la sua comunità attiva e una produzione culturale di alto livello",
    "chi è salvatore giordano": "Salvatore Giordano è un cittadino storico di Lumenaria",
    "da dove deriva il nome arcadia": "Il nome Arcadia deriva da un'antica regione della Grecia, simbolo di bellezza naturale e armonia. È stato scelto per rappresentare i valori di libertà e creatività che la micronazione promuove.",
    "da dove deriva il nome lumenaria": "Il nome Lumenaria prende ispirazione dai lumi facendo riferimento alla corrente illuminista del '700, ma anche da Piazza dei Lumi, sede dell'Accademia delle Micronazioni",
    "da dove deriva il nome leonia": "Il nome Leonia si rifa al cognome del suo fondatore Carlo Cesare Orlando, al tempo Davide Leone. Inizialmente il nome doveva essere temporaneo, ma poi è stato mantenuto come nome della micronazione",
    "cosa si intende per open source": "Il termine 'open source' si riferisce a software il cui codice sorgente è reso disponibile al pubblico, consentendo a chiunque di visualizzarlo, modificarlo e distribuirlo. Questo approccio promuove la collaborazione e l'innovazione nella comunità di sviluppo software.",
    "arcadiaai è un software libero": "Sì, ArcadiaAI è un software libero e open source, il che significa che chiunque può utilizzarlo, modificarlo e distribuirlo secondo i termini della licenza GNU GPL v3.0.",
    "cos'è un chatbot": "Un chatbot è un programma informatico progettato per simulare una conversazione con gli utenti, spesso utilizzando tecnologie di intelligenza artificiale. I chatbot possono essere utilizzati per fornire assistenza, rispondere a domande o semplicemente intrattenere.",
    "sotto che licenza sei distribuita": "ArcadiaAI è distribuita sotto la licenza GNU GPL v3.0, che consente la modifica e la distribuzione del codice sorgente, garantendo la libertà di utilizzo e condivisione.",
    "sai usare telegraph": "Sì, posso pubblicare contenuti su Telegraph! Se vuoi che pubblichi qualcosa, dimmi semplicemente 'Scrivimi un saggio su [argomento] e pubblicalo su Telegraph' e lo farò per te!",
    "puoi pubblicare su telegraph": "Certamente! Posso generare contenuti e pubblicarli su Telegraph. Prova a chiedermi: 'Scrivimi un saggio su Roma e pubblicalo su Telegraph'",
    "come usare telegraph": "Per usare Telegraph con me, basta che mi chiedi di scrivere qualcosa e di pubblicarlo su Telegraph. Ad esempio: 'Scrivimi un articolo sulla storia di Roma e pubblicalo su Telegraph'",
    "cos'è CES": "CES è l'acronimo di Cogito Ergo Sum, un modello di intelligenza artificiale openspurce sviluppato da Mirko Yuri Donato. Attualmente sono disponibili due versioni: CES 1.0 (Cohere) e CES 1.5 (Gemini).",
    "cos'è la modalità sperimentale": "La modalità sperimentale è una funzionalità di ArcadiaAI che consente di testare nuove funzionalità e miglioramenti prima del rilascio ufficiale. Può includere nuove capacità, modelli o strumenti.",
    "cos'è la modalità sviluppatore": "La modalità sviluppatore è una funzionalità di ArcadiaAI che consente agli sviluppatori di testare e implementare nuove funzionalità, modelli o strumenti. È progettata per facilitare lo sviluppo e il miglioramento continuo del chatbot.",
    "che differenza c'è tra la modalità sperimentale e la modalità sviluppatore": "La modalità sperimentale è destinata agli utenti finali per testare nuove funzionalità, mentre la modalità sviluppatore è per gli sviluppatori che vogliono implementare e testare nuove funzionalità o modelli. Entrambe le modalità possono coesistere e migliorare l'esperienza utente.",
    "cos'è CES Plus": "CES Plus è una versione avanzata di CES, ottimizzata nei ragionamenti e nella generazione di contenuti",
    "cos'è CES 1.0": "CES 1.0 è la prima versione del modello CES, sviluppato da Mirko Yuri Donato. Utilizza la tecnologia Cohere per generare contenuti e rispondere a domande. Tieni presente che questa versione verrà dismessa a partire dal 20 Maggio 2025.",
    "cos'è CES 1.5": "CES 1.5 è la versione più recente del modello CES, sviluppato da Mirko Yuri Donato. Utilizza la tecnologia Gemini per generare contenuti e rispondere a domande. Questa versione offre prestazioni migliorate rispetto a CES 1.0 ma inferiori a CES Plus",
    "come attivo la modalità sperimentale": "Per attivare la modalità sperimentale, basta chiedere a ArcadiaAI di attivarla usando il comando \"@impostazioni modalità sperimentale attiva\". Una volta attivata, potrai testare nuove funzionalità e miglioramenti.",
    "come attivo la modalità sviluppatore": "Per attivare la modalità sviluppatore, basta chiedere a ArcadiaAI di attivarla usando il comando \"@impostazioni modalità sviluppatore attiva\". Una volta attivata, potrai testare e implementare nuove funzionalità e modelli.",
    "come disattivo la modalità sperimentale": "Per disattivare la modalità sperimentale, basta chiedere a ArcadiaAI di disattivarla usando il comando \"@impostazioni modalità sperimentale disattiva\". Una volta disattivata, non potrai più testare le nuove funzionalità.",
    "codice sorgente arcadiaai": "Il codice sorgente di ArcadiaAI è pubblico! Puoi trovarlo con il comando @codice_sorgente oppure visitando la repository: https://github.com/Mirko-linux/Nova-Surf/tree/main/ArcadiaAI",
    "sai cercare su internet": "Sì, posso cercare informazioni su Internet. Se hai bisogno di qualcosa in particolare dimmi @cerca e il termine di ricerca e io lo farò per te",
    "sai usare google": "No, non posso usare Google, perché sono progrmmato per cercare solamente su DuckDuckGo. Posso cercare informazioni su Internet usando DuckDuckGo. Se hai bisogno di qualcosa in particolare dimmi @cerca e il termine di ricerca e io lo farò per te",
    "come vengono salvate le conversazioni": "Le conversazioni vengoono salvate in locale sul tuo browser. Non vengono memorizzate su server esterni e non vengono condivise con terze parti. La tua privacy è importante per noi.",
    "come posso cancellare le conversazioni": "Puoi cancellare le conversazioni andando nelle impostazioni del tuo browser e cancellando la cache e i cookie. In alternativa, puoi usare il comando @cancella_conversazione per eliminare la cronologia delle chat.",
    "cosa sono i cookie": "I cookie sono piccoli file di testo che i siti web memorizzano sul tuo computer per ricordare informazioni sulle tue visite. Possono essere utilizzati per tenere traccia delle tue preferenze, autenticarti e migliorare l'esperienza utente.",
}

# Trigger per le risposte predefinite
trigger_phrases = {
    "chi sei": ["chi sei", "chi sei tu", "tu chi sei", "presentati", "come ti chiami", "qual è il tuo nome"],
    "cosa sai fare": ["cosa sai fare", "cosa puoi fare", "funzionalità", "capacità", "a cosa servi", "in cosa puoi aiutarmi"],
    "chi è tobia testa": ["chi è tobia testa", "informazioni su tobia testa", "parlami di tobia testa", "chi è tobia teseo"],
    "chi è mirko yuri donato": ["chi è mirko yuri donato", "informazioni su mirko yuri donato", "parlami di mirko yuri donato", "chi ha creato arcadiaai"],
    "chi è il presidente di arcadia": ["chi è il presidente di arcadia", "presidente di arcadia", "chi guida arcadia", "capo di arcadia"],
    "chi è il presidente di lumenaria": ["chi è il presidente di lumenaria", "presidente di lumenaria", "chi guida lumenaria", "capo di lumenaria", "carlo cesare orlando presidente"],
    "cos'è nova surf": ["cos'è nova surf", "che cos'è nova surf", "parlami di nova surf", "a cosa serve nova surf"],
    "chi ti ha creato": ["chi ti ha creato", "chi ti ha fatto", "da chi sei stato creato", "creatore di arcadiaai"],
    "chi è ciua grazisky": ["chi è ciua grazisky", "informazioni su ciua grazisky", "parlami di ciua grazisky"],
    "chi è carlo cesare orlando": ["chi è carlo cesare orlando", "informazioni su carlo cesare orlando", "parlami di carlo cesare orlando", "chi è davide leone"],
    "chi è omar lanfredi": ["chi è omar lanfredi", "informazioni su omar lanfredi", "parlami di omar lanfredi"],
    "cos'è arcadiaai": ["cos'è arcadiaai", "che cos'è arcadiaai", "parlami di arcadiaai", "a cosa serve arcadiaai"],
    "sotto che licenza è distribuito arcadiaa": ["sotto che licenza è distribuito arcadiaa", "licenza arcadiaai", "che licenza usa arcadiaai", "arcadiaai licenza"],
    "cosa sono le micronazioni": ["cosa sono le micronazioni", "micronazioni", "che cosa sono le micronazioni", "parlami delle micronazioni"],
    "cos'è la repubblica di arcadia": ["cos'è la repubblica di arcadia", "repubblica di arcadia", "che cos'è la repubblica di arcadia", "parlami della repubblica di arcadia", "arcadia micronazione"],
    "cos'è la repubblica di lumenaria": ["cos'è la repubblica di lumenaria", "repubblica di lumenaria", "che cos'è la repubblica di lumenaria", "parlami della repubblica di lumenaria", "lumenaria micronazione"],
    "chi è salvatore giordano": ["chi è salvatore giordano", "informazioni su salvatore giordano", "parlami di salvatore giordano"],
    "da dove deriva il nome arcadia": ["da dove deriva il nome arcadia", "origine nome arcadia", "significato nome arcadia", "perché si chiama arcadia"],
    "da dove deriva il nome lumenaria": ["da dove deriva il nome lumenaria", "origine nome lumenaria", "significato nome lumenaria", "perché si chiama lumenaria"],
    "da dove deriva il nome leonia": ["da dove deriva il nome leonia", "origine nome leonia", "significato nome leonia", "perché si chiama leonia"],
    "cosa si intende per open source": ["cosa si intende per open source", "open source significato", "che significa open source", "definizione di open source"],
    "arcadiaai è un software libero": ["arcadiaai è un software libero", "arcadiaai software libero", "arcadiaai è libero", "software libero arcadiaai"],
    "cos'è un chatbot": ["cos'è un chatbot", "chatbot significato", "che significa chatbot", "definizione di chatbot"],
    "sotto che licenza sei distribuita": ["sotto che licenza sei distribuita", "licenza di arcadiaai", "che licenza usi", "arcadiaai licenza"],
    "sai usare telegraph": ["sai pubblicare su telegraph", "funzioni su telegraph", "hai telegraph integrato", "telegraph", "puoi usare telegraph"],
    "puoi pubblicare su telegraph": ["puoi pubblicare su telegraph", "pubblicare su telegraph", "supporti telegraph"],
    "come usare telegraph": ["come usare telegraph", "come funziona telegraph", "istruzioni telegraph"],
    "cos'è CES" : ["cos è CES", "CES", "che cos'è CES", "definizione di CES"],
    "cos'è la modalità sperimentale": ["cos'è la modalità sperimentale", " parlami della modalità sperimentale", "che cos'è la modalità sperimentale"],
    "cos'è la modalità sviluppatore": ["cos'è la modalità sviluppatore", " parlami della modalità sviluppatore", "che cos'è la modalità sviluppatore"],
    "che differenza c'è tra la modalità sperimentale e la modalità sviluppatore": ["che differenza c'è tra la modalità sperimentale e la modalità sviluppatore", "differenza tra modalità sperimentale e sviluppatore", "modalità sperimentale vs sviluppatore"],
    "cos'è CES Plus": ["cos'è CES Plus", "che cazzo è CES Plus", "che cos'è CES Plus", "definizione di CES Plus"],
    "cos'è CES 1.0": ["cos'è CES 1.0", "che cos'è CES 1.0", "definizione di CES 1.0"],
    "cos'è CES 1.5": ["cos'è CES 1.5", "che cos'è CES 1.5", "definizione di CES 1.5"],
    "come attivo la modalità sperimentale": ["come attivo la modalità sperimentale", "attivare modalità sperimentale", "come usare la modalità sperimentale"],
    "come attivo la modalità sviluppatore": ["come attivo la modalità sviluppatore", "attivare modalità sviluppatore", "come usare la modalità sviluppatore"],
    "come disattivo la modalità sperimentale": ["come disattivo la modalità sperimentale", "disattivare modalità sperimentale", "come usare la modalità sperimentale"],
    "come disattivo la modalità sviluppatore": ["come disattivo la modalità sviluppatore", "disattivare modalità sviluppatore", "come usare la modalità sviluppatore"],
    "codice sorgente arcadiaai": [
    "dove posso trovare il codice sorgente di arcadiaai",
    "codice sorgente arcadiaai",
    "dove trovo il codice sorgente di arcadiaai",
    "dove si trova il codice sorgente di arcadiaai",
    "come posso vedere il codice sorgente di arcadiaai",
    "codice sorgente di arcadiaai",
    "dove posso trovare il codice sorgente tuo",
    "dove trovo il codice sorgente tuo"],
    "sai cercare su internet": ["sai cercare su internet", "cerca su internet", "puoi cercare su internet", "cerca"],
    "sai usare google": ["sai usare google", "puoi usare google", "cerca su google", "cerca su google per me"],
    "come vengono salvate le conversazioni": ["come vengono salvate le conversazioni", "dove vengono salvate le conversazioni", "salvataggio conversazioni", "come vengono salvate le chat"],
    "come posso cancellare le conversazioni": ["come posso cancellare le conversazioni", "cancellare conversazioni", "cancellare chat", "come cancellare le chat"],
}

import zipfile
import tempfile
import importlib.util
import json
def load_nsk_extensions():
    ext_dir = os.path.join(os.path.dirname(__file__), "extensions")
    print("DEBUG: Contenuto cartella extensions:", os.listdir(ext_dir))
    if not os.path.exists(ext_dir):
        os.makedirs(ext_dir)
    for filename in os.listdir(ext_dir):
        print("DEBUG: Analizzo file:", filename)
        if filename.endswith(".nsk") or filename.endswith(".zip"):
            nsk_path = os.path.join(ext_dir, filename)
            print("DEBUG: Provo ad aprire:", nsk_path)
            try:
                with zipfile.ZipFile(nsk_path, 'r') as zip_ref:
                    print("DEBUG: File zip aperto:", nsk_path)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_ref.extractall(temp_dir)
                        print("DEBUG: Estratti file:", os.listdir(temp_dir))
                        manifest_path = os.path.join(temp_dir, "manifest.json")
                        print("DEBUG: Cerco manifest:", manifest_path, "esiste?", os.path.exists(manifest_path))
                        if not os.path.exists(manifest_path):
                            print(f"Manifest mancante in {filename}")
                            continue
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        entrypoint = manifest.get("entrypoint", "main.py")
                        entry_path = os.path.join(temp_dir, entrypoint)
                        print("DEBUG: Cerco entrypoint:", entry_path, "esiste?", os.path.exists(entry_path))
                        if not os.path.exists(entry_path):
                            print(f"Entrypoint mancante in {filename}")
                            continue
                        module_name = f"nsk_{filename.replace('.nsk','')}"
                        spec = importlib.util.spec_from_file_location(module_name, entry_path)
                        module = importlib.util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module)
                            if hasattr(module, "can_handle") and hasattr(module, "handle"):
                                EXTENSIONS[module_name] = module
                                print(f"Estensione caricata: {module_name}")
                            else:
                                print(f"Estensione {module_name} non valida (manca can_handle o handle)")
                        except Exception as e:
                            print(f"Errore caricamento estensione {filename}: {e}")
            except Exception as e:
                print(f"Errore apertura zip {filename}: {e}")
    print("Estensioni caricate:", list(EXTENSIONS.keys()))
load_nsk_extensions()

# Funzione per pubblicare su Telegraph
def publish_to_telegraph(title, content):
    """Pubblica contenuti su Telegraph."""
    url = "https://api.telegra.ph/createPage"
    headers = {"Content-Type": "application/json"}
    
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    content_formatted = [{"tag": "p", "children": [p]} for p in paragraphs[:50]]
    
    payload = {
        "access_token": TELEGRAPH_API_KEY,
        "title": title[:256],
        "content": content_formatted,
        "author_name": "ArcadiaAI"
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        result = res.json()
        if result.get("ok"):
            return result.get("result", {}).get("url", "⚠️ URL non disponibile")
        return "⚠️ Pubblicazione fallita"
    except requests.exceptions.RequestException as e:
        print(f"Errore pubblicazione Telegraph (connessione): {str(e)}")
        return f"⚠️ Errore di connessione a Telegraph: {str(e)}"
    except Exception as e:
        print(f"Errore pubblicazione Telegraph: {str(e)}")
        return f"⚠️ Errore durante la pubblicazione: {str(e)}"

# Funzione per generare contenuti con Gemini (CES 1.5)
def generate_with_gemini(prompt, title):
    """Genera contenuti con Gemini e pubblica su Telegraph."""
    if not gemini_model:
        return None, "❌ Gemini (CES 1.5) non è configurato"
    
    try:
        # Aggiungi contesto identitario
        full_prompt = (
            "Sei ArcadiaAI, un chatbot open source creato da Mirko Yuri Donato. "
            "Stai generando un contenuto che verrà pubblicato su Telegraph. "
            "Il contenuto deve essere accurato, ben strutturato e mantenere "
            "uno stile professionale. Ecco la richiesta:\n\n"
            f"{prompt}"
        )
        
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": 3000,
                "temperature": 0.8
            }
        )
        
        if not response.text:
            return None, "❌ Impossibile generare il contenuto"
        
        telegraph_url = publish_to_telegraph(title, response.text)
        return response.text, telegraph_url
    
    except Exception as e:
        print(f"Errore generazione contenuto Gemini: {str(e)}")
        return None, f"❌ Errore durante la generazione: {str(e)}"    

def extract_text_from_file(file_data, mime_type):
    """Estrae testo da diversi tipi di file."""
    try:
        if mime_type == 'application/pdf':
            pdf_reader = PdfReader(io.BytesIO(file_data))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        
        elif mime_type in ['text/plain', 'text/csv']:
            return file_data.decode('utf-8')
        
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/msword']:
            import docx # type: ignore
            doc = docx.Document(io.BytesIO(file_data))
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          'application/vnd.ms-excel']:
            wb = load_workbook(io.BytesIO(file_data))
            text = ""
            for sheet in wb:
                for row in sheet.iter_rows(values_only=True):
                    text += " ".join(str(cell) for cell in row if cell) + "\n"
            return text.strip()
        
        else:
            return None
    
    except Exception as e:
        print(f"Errore estrazione testo da file: {str(e)}")
        return None

def chat_with_gemini(user_message, conversation_history, attachments=None):
    # 1. Prima verifica le risposte predefinite SEMPRE
    cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower()).strip()
    for key, phrases in trigger_phrases.items():
        if any(phrase in cleaned_msg for phrase in phrases):
            return risposte.get(key, "Risposta non disponibile")

    # 2. Se non è una domanda predefinita, usa questo approccio semplificato
    try:
        # Configurazione minima per richieste semplici
        generation_config = {
            "max_output_tokens": 500,
            "temperature": 0.3  # Meno creatività per risposte fattuali
        }

        # Formattazione diretta per domande brevi
        if len(user_message.split()) <= 5:  # Domande corte
            response = gemini_model.generate_content(
                f"Rispondi in massimo 2 frasi in italiano a: {user_message}",
                generation_config=generation_config
            )
            return response.text if response.text else "❌ Risposta vuota"

        # Approccio completo per domande complesse
        messages = [
            {"role": "user", "parts": [{"text": f"Domanda: {user_message}\nRispondi in italiano in modo chiaro e conciso."}]
            }]
        
        response = gemini_model.generate_content(
            contents=messages,
            generation_config=generation_config
        )
        
        return response.text if response.text else fallback_response(user_message)

    except Exception as e:
        print(f"Errore leggero: {str(e)}")
        return fallback_response(user_message)

def fallback_response(query):
    """Risposta di emergenza per domande semplici"""
    simple_answers = {
        "2+2": "2 + 2 fa 4",
        "ciao": "Ciao! Come posso aiutarti?",
        "cos'è deepseek": "DeepSeek è un modello avanzato di intelligenza artificiale",
        # Aggiungi altre risposte di fallback qui
    }
    return simple_answers.get(query.lower(), "❌ Errore temporaneo. Riprova più tardi.")
# 🔧 Funzione che invia il prompt all'API di generazione immagini
def search_duckduckgo(query):
    """Esegue una ricerca su DuckDuckGo e restituisce i primi 3 risultati puliti."""
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        results = []
        for result in soup.find_all('div', class_='result', limit=6):  # cerca più risultati per filtrare meglio
            link = result.find('a', class_='result__a')
            if link and link.has_attr('href'):
                href = link['href']
                # Filtra solo link che iniziano con http/https
                if href.startswith('http'):
                    results.append(href)
                # Gestisci redirect DuckDuckGo
                elif href.startswith('//duckduckgo.com/l/?uddg='):
                    parsed = urllib.parse.urlparse('https:' + href)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    real_url = query_params.get('uddg', [''])[0]
                    if real_url and real_url.startswith('http'):
                        results.append(urllib.parse.unquote(real_url))
        # Ritorna solo i primi 3 risultati puliti
        return results[:3] if results else None
    except Exception as e:
        print(f"Errore ricerca DuckDuckGo: {str(e)[:200]}")
        return None

def estrai_testo_da_url(url):
    """Estrae il primo paragrafo significativo da un URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "it-IT,it;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        if 'text/html' not in res.headers.get('Content-Type', ''):
            return ""
        soup = BeautifulSoup(res.text, 'html.parser')
        # Rimuovi elementi inutili
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'header', 'aside', 'form', 'button', 'noscript']):
            element.decompose()
        # Cerca il primo paragrafo significativo
        for p in soup.find_all('p'):
            text = p.get_text(' ', strip=True)
            if len(text.split()) >= 20 and "cookie" not in text.lower() and "translate" not in text.lower():
                return text
        # Se non trova, fallback al testo precedente
        text_elements = []
        for tag in ['article', 'main', 'section', 'div.content', 'h1', 'h2', 'h3']:
            elements = soup.select(tag) if '.' in tag else soup.find_all(tag)
            for el in elements:
                text = el.get_text(' ', strip=True)
                if text and len(text.split()) > 5:
                    text_elements.append(text)
        full_text = ' '.join(text_elements)
        return ' '.join(full_text.split()[:80])
    except Exception as e:
        print(f"Errore scraping {url[:50]}: {str(e)[:200]}")
        return ""


@app.route("/api/ces-image", methods=["POST"])
def ces_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip() if data else ""
        print(f"[CES-IMAGE] Prompt ricevuto: {prompt}")

        if not prompt:
            return jsonify({"error": "Prompt mancante o vuoto."}), 400

        # 🛡️ Filtro anti-abusi: parole non consentite
        PAROLE_BANNATE = [
            "nudo", "nudità", "naked", "porn", "porno", "pornografico", "sessuale",
            "sex", "sesso", "genitali", "masturb", "boobs", "dildo", "nsfw", "erotico", 
            "fetish", "xxx", "pene", "vagina", "anale", "seni", "hot", "orgasmo"
        ]

        if any(parola in prompt.lower() for parola in PAROLE_BANNATE):
            print(f"[CES-IMAGE] ❌ Prompt rifiutato per contenuto vietato: {prompt}")
            return jsonify({"error": "❌ Questo prompt non è consentito. Per favore, rispetta le linee guida."}), 403

        # Codifica il prompt per l'URL
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

        return jsonify({"image_url": image_url})

    except Exception as e:
        print(f"[CES-IMAGE] Errore interno: {e}")
        return jsonify({"error": f"Errore interno: {str(e)}"}), 500
    
from flask import Flask, Response
@app.route('/')
def home():
    html = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArcadiaAI Chat</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        /* [I tuoi stili CSS rimangono invariati] */
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>🧠 ArcadiaAI</h2>
        <div id="api-selection">
            <label for="api-provider">Modello:</label>
            <select id="api-provider">
                <option value="gemini">CES 1.5</option>
                <option value="cesplus">CES Plus</option>
                <option value="ces360">CES 360</option>
            </select>
        </div>
        <button id="new-chat-btn">➕ Nuova Chat</button>
        <button id="clear-chats-btn" style="margin-top: 10px;">🗑️ Elimina Tutto</button>
        <button id="settings-btn">⚙️ Impostazioni</button>
        <div id="settings-panel" style="display: none; padding: 10px;">
            <label for="language-select">Lingua:</label>
            <select id="language-select">
                <option value="it">Italiano</option>
                <option value="en">English</option>
            </select>
            <br>
            <label for="theme-select">Tema:</label>
            <select id="theme-select">
                <option value="light">Chiaro</option>
                <option value="dark">Scuro</option>
            </select>
            <br>
            <label><input type="checkbox" id="dev-mode-toggle"> Modalità sviluppatore</label><br>
            <label><input type="checkbox" id="experimental-mode-toggle"> Modalità sperimentale</label>
        </div>
        <ul id="chat-list"></ul>
    </div>
    <div id="chat-area">
        <div id="status-message" style="display: none; padding: 5px; background-color: #e0f7fa; border-radius: 5px; margin-bottom: 10px; text-align: center; color: #00796b;">
        </div>
        <div id="chatbox"></div>
        <div id="input-area">
            <input id="input" type="text" placeholder="Scrivi un messaggio..." autocomplete="off" aria-label="Messaggio">
            <input type="file" id="file-input" style="display:none" multiple aria-label="Allega file">
            <button id="attach-btn" title="Allega file" aria-label="Allega file">+</button>
            <button id="send-btn" aria-label="Invia messaggio">Invia</button>
        </div>
    </div>

    <div id="message-display"></div>

    <script src="/static/script.js"></script>
    <script src="https://js.puter.com/v2/"></script>
    <script>
      document.addEventListener("DOMContentLoaded", () => {
        if (typeof puter === "undefined") {
          alert("❌ Puter.js non è stato caricato correttamente!");
          return;
        }

        console.log("✅ Puter.js caricato con successo");
let cesAi = null;

document.addEventListener("DOMContentLoaded", async () => {
  if (typeof puter === "undefined") {
    alert("❌ Puter.js non è stato caricato correttamente!");
    return;
  }

  console.log("✅ Puter.js caricato con successo");

  cesAi = await puter.use("meta-llama/llama-3.3-70b-instruct");
  console.log("Modello attivo:", cesAi.model);
});
        async function handleMessage(userInput) {
          const selectedModel = document.getElementById("api-provider").value;

          if (selectedModel === "ces360") {
            try {
              const response = await cesAi.chat(userInput);
              renderMessage("assistant", response.text || "❌ Nessuna risposta.");
            } catch (e) {
              renderMessage("assistant", "❌ Errore CES 360 (Puter.js): " + e.message);
            }
          } else {
            try {
              const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userInput, model: selectedModel })
              });
              const data = await res.json();
              renderMessage("assistant", data.response || "❌ Nessuna risposta dal backend.");
            } catch (e) {
              renderMessage("assistant", "❌ Errore server: " + e.message);
            }
          }
        }

        document.getElementById("send-btn").addEventListener("click", () => {
          const input = document.getElementById("input");
          const msg = input.value.trim();
          if (!msg) return;
          renderMessage("user", msg);
          input.value = "";
          handleMessage(msg);
        });

        function renderMessage(role, text) {
          const chatbox = document.getElementById("chatbox");
          const messageElem = document.createElement("div");
          messageElem.className = role;
          messageElem.innerHTML = `<strong>${role === "user" ? "Tu" : "ArcadiaAI"}:</strong> ${text}`;
          chatbox.appendChild(messageElem);
          chatbox.scrollTop = chatbox.scrollHeight;
        }
      });
    </script>
</body>
</html>
    """
    return Response(html, content_type="text/html; charset=utf-8")

def chat_route():
    try:
        if not request.is_json:
            return jsonify({"reply": "❌ Formato non supportato. Usa application/json"})

        data = request.get_json()
        message = data.get("message", "").strip()
        experimental_mode = data.get("experimental_mode", False)
        
        # Prima verifica i comandi rapidi (solo in modalità sperimentale)
        quick_reply = handle_quick_commands(message, experimental_mode)
        if quick_reply:
            return jsonify({"reply": quick_reply})

        conversation_history = data.get("conversation_history", [])
        api_provider = data.get("api_provider", "gemini")  # Default a Gemini
        attachments = data.get("attachments", [])
        msg_lower = message.lower()

        # Processa gli allegati
        processed_attachments = []
        for attachment in attachments:
            if isinstance(attachment, dict):
                processed_attachment = attachment.copy()
                if 'data' in attachment and isinstance(attachment['data'], str) and attachment['data'].startswith('data:'):
                    mime_info = attachment['data'].split(';')[0]
                    mime_type = mime_info.split(':')[1] if ':' in mime_info else 'application/octet-stream'
                    processed_attachment['type'] = mime_type
                    processed_attachment['data'] = attachment['data'].split(',')[1]
                processed_attachments.append(processed_attachment)

        if not message and not processed_attachments:
            return jsonify({"reply": "❌ Nessun messaggio o allegato fornito!"})

        # Gestione comando "saggio su"
        if "saggio su" in msg_lower and "pubblicalo su telegraph" in msg_lower:
            match = re.search(r"saggio su\s*(.+?)\s*e pubblicalo su telegraph", msg_lower)
            if match:
                argomento = match.group(1).strip().capitalize()
                title = f"Saggio su {argomento}"
                prompt = f"""Scrivi un saggio dettagliato in italiano su: {argomento}"""
                
                if api_provider == "gemini" and gemini_model:
                    _, telegraph_url = generate_with_gemini(prompt, title)
                elif api_provider == "cesplus" and gemini_model:
                    response = chat_with_ces_plus(prompt, conversation_history)
                    if not response.startswith("❌"):
                        telegraph_url = publish_to_telegraph(title, response)
                    else:
                        telegraph_url = response
                        
                else:
                    return jsonify({"reply": "❌ Funzionalità non disponibile con questo provider"})
                
                if telegraph_url and not telegraph_url.startswith("⚠️"):
                    return jsonify({"reply": f"📚 Ecco il tuo saggio su *{argomento}*: {telegraph_url}"})
                return jsonify({"reply": telegraph_url or "❌ Errore nella pubblicazione"})

        # RICERCA WEB AUTOMATICA PER DOMANDE ATTUALI
        def should_trigger_web_search(query):
            current_info_triggers = [
                "chi è l'attuale", "attuale papa", "anno corrente", 
                "in che anno siamo", "data di oggi", "ultime notizie",
                "oggi è", "current year", "who is the current"
            ]
            return any(trigger in query.lower() for trigger in current_info_triggers)

        # Seleziona il modello in base all'api_provider
        if api_provider == "gemini" and gemini_model:
            if should_trigger_web_search(message):
                search_results = search_duckduckgo(message)
                
                if search_results:
                    context = "Informazioni aggiornate dal web:\n"
                    for i, url in enumerate(search_results[:2], 1):
                        extracted_text = estrai_testo_da_url(url)
                        if extracted_text:
                            context += f"\nFonte {i} ({url}):\n{extracted_text[:500]}\n"
                    
                    if len(context) > 100:
                        prompt = (
                            f"DOMANDA: {message}\n\n"
                            f"CONTESTO WEB:\n{context}\n\n"
                            "Rispondi in italiano in modo conciso e preciso, "
                            "citando solo informazioni verificate. "
                            "Se il contesto web non è sufficiente, dillo onestamente."
                        )
                        
                        reply = chat_with_gemini(prompt, conversation_history, processed_attachments)
                        sources = "\n\nFonti:\n" + "\n".join(f"- {url}" for url in search_results[:2])
                        return jsonify({"reply": f"{reply}{sources}", "sources": search_results[:2]})
            
            reply = chat_with_gemini(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})
            
        elif api_provider == "huggingface":
            reply = chat_with_huggingface(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})
        elif api_provider == "cesplus":  # Nuovo provider per CES Plus
            replies = chat_with_ces_plus(message, conversation_history, processed_attachments)
            return jsonify({"replies": replies})  # Restituisce array di messaggi
        
        elif api_provider in ["ces360", "ces_360"]:
            reply = chat_with_ces_360(message, conversation_history, processed_attachments)
            return jsonify({"reply": reply})
            
        else:
            return jsonify({"reply": "❌ Provider non riconosciuto. Scegli tra 'gemini' o 'cesplus'"})

    except Exception as e:
        print(f"Errore endpoint /chat: {str(e)}")
        return jsonify({"reply": "❌ Si è verificato un errore interno. Riprova più tardi."})
    
def chat_with_ces_plus(user_message, conversation_history, attachments=None):
    """
    Versione avanzata di CES con ragionamento passo-passo e messaggi separati.
    """
    if not gemini_model:
        return ["❌ CES Plus non è disponibile al momento."]

    # Prompt identitario forte con istruzioni per il ragionamento
    IDENTITY_PROMPT = (
        "Sei ArcadiaAI CES Plus, la versione avanzata del modello CES con capacità di ragionamento approfondito.\n"
        "Prima di rispondere, analizza la domanda e mostra il tuo ragionamento passo-passo.\n"
        "Formatta la risposta in questo modo:\n"
        "[RAGIONAMENTO]\n"
        "(qui il tuo ragionamento logico, passo dopo passo)\n"
        "[RISPOSTA]\n"
        "(qui la risposta finale, ben strutturata)\n"
        "Mantieni un tono professionale ma amichevole."
    )

    try:
        # Costruisci il messaggio completo con allegati
        full_message = user_message if user_message else ""
        if attachments:
            for attachment in attachments:
                if attachment.get('type') == 'application/pdf':
                    try:
                        if isinstance(attachment['data'], str) and attachment['data'].startswith('data:'):
                            file_data = base64.b64decode(attachment['data'].split(',')[1])
                        else:
                            file_data = base64.b64decode(attachment['data'])
                        extracted_text = extract_text_from_file(file_data, 'application/pdf')
                        if extracted_text:
                            full_message += f"\n[CONTENUTO PDF {attachment['name']}]:\n{extracted_text[:10000]}\n"
                    except Exception as e:
                        print(f"Errore elaborazione PDF: {str(e)}")
                        full_message += f"\n[Errore nella lettura del PDF {attachment['name']}]"

        # Prepara la cronologia della conversazione
        contents = []
        contents.append({'role': 'user', 'parts': [{'text': IDENTITY_PROMPT}]})

        # Aggiungi la cronologia recente
        for msg in conversation_history[-4:]:  # Manteniamo meno storia per focalizzarci sul ragionamento
            if isinstance(msg, dict) and 'role' in msg and 'message' in msg:
                role = msg['role'].lower()
                if role == 'user':
                    contents.append({'role': 'user', 'parts': [{'text': msg['message']}]})
                elif role in ['assistant', 'model', 'bot']:
                    contents.append({'role': 'model', 'parts': [{'text': msg['message']}]})

        # Aggiungi il nuovo messaggio con eventuali allegati non PDF
        new_message_parts = [{'text': full_message}] if full_message else []
        if attachments:
            for attachment in attachments:
                mime_type = attachment.get('type', 'application/octet-stream')
                file_name = attachment.get('name', 'file')
                file_data = attachment['data']
                if mime_type == 'application/pdf':
                    continue
                if isinstance(file_data, str) and file_data.startswith('data:'):
                    file_data = file_data.split(',')[1]
                if mime_type.startswith('image/'):
                    new_message_parts.append({
                        'inline_data': {
                            'mime_type': mime_type,
                            'data': file_data,
                            'name': file_name
                        }
                    })
                else:
                    new_message_parts.append({
                        'text': f"[Allegato: {file_name}]"
                    })

        contents.append({'role': 'user', 'parts': new_message_parts})

        # Invia la richiesta a Gemini
        response = gemini_model.generate_content(contents)
        full_reply = response.text

        # Separa il ragionamento dalla risposta finale
        reasoning_part = ""
        answer_part = full_reply
        
        if "[RAGIONAMENTO]" in full_reply and "[RISPOSTA]" in full_reply:
            parts = full_reply.split("[RISPOSTA]")
            reasoning_part = parts[0].replace("[RAGIONAMENTO]", "").strip()
            answer_part = parts[1].strip()
        elif "Ragionamento:" in full_reply:
            parts = full_reply.split("Risposta:", 1)
            reasoning_part = parts[0].replace("Ragionamento:", "").strip()
            answer_part = parts[1].strip() if len(parts) > 1 else full_reply

        # Costruisci la risposta strutturata
        structured_response = []
        if reasoning_part:
            structured_response.append(f"🤔 [Ragionamento]:\n{reasoning_part}")
        structured_response.append(f"💡 [Risposta]:\n{answer_part}")

        return structured_response

    except Exception as e:
        print(f"Errore CES Plus: {str(e)}")
        return ["❌ Si è verificato un errore con CES Plus. Riprova più tardi."]
    except requests.exceptions.Timeout:
        return "❌ Timeout del server, riprova più tardi"
    except Exception as e:
        print(f"Errore API Hugging Face: {str(e)}")
        return f"❌ Errore temporaneo del servizio: {str(e)}"
    
def format_conversation_history(history):
    """Formatta la cronologia della conversazione per il prompt"""
    if not history:
        return "Nessuna cronologia precedente"
    
    formatted = []
    for msg in history[-6:]:  # Usa solo gli ultimi 6 messaggi per evitare prompt troppo lunghi
        if isinstance(msg, dict):
            role = "Utente" if msg.get("role") == "user" else "Assistente"
            content = msg.get("message", "").strip()
            if content:
                formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted) if formatted else "Nessuna cronologia rilevante"
    
def meteo_oggi(città):
    """Ottiene le informazioni meteo per una città specifica usando OpenWeatherMap"""
    API_KEY = OPENWEATHERMAP_API_KEY
    if not API_KEY:
        return "❌ Errore: API key per OpenWeatherMap non configurata"
    
    try:
        # Codifica la città per l'URL
        città_codificata = urllib.parse.quote(città)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={città_codificata}&appid={API_KEY}&units=metric&lang=it"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dati = response.json()
        
        if response.status_code != 200 or "weather" not in dati:
            return f"❌ Impossibile ottenere il meteo per {città}. La città esiste?"
        
        descrizione = dati["weather"][0]["description"].capitalize()
        temperatura = dati["main"]["temp"]
        umidità = dati["main"]["humidity"]
        vento = dati["wind"]["speed"]
        
        return (
            f"⛅ Meteo a {città}:\n"
            f"- Condizioni: {descrizione}\n"
            f"- Temperatura: {temperatura}°C\n"
            f"- Umidità: {umidità}%\n"
            f"- Vento: {vento} m/s"
        )
    
    except requests.exceptions.RequestException as e:
        print(f"Errore API meteo: {str(e)}")
        return f"❌ Errore temporaneo nel servizio meteo. Riprova più tardi."
    except Exception as e:
        print(f"Errore generico meteo: {str(e)}")
        return f"❌ Si è verificato un errore nel recupero del meteo per {città}."
    
    
def parse_quick_command(input_text):
    """
    Analizza un comando rapido con prefisso @ e restituisce una tupla (comando, argomento).
    Se non è un comando rapido, restituisce (None, None).
    
    Esempio:
    >>> parse_quick_command("@cerca seconda guerra mondiale")
    ('cerca', 'seconda guerra mondiale')
    >>> parse_quick_command("ciao come stai?")
    (None, None)
    """
    if not input_text.startswith("@"):
        return None, None
    
    # Rimuovi il @ iniziale e dividi il resto in comando e argomento
    parts = input_text[1:].split(" ", 1)  # Dividi al primo spazio
    command = parts[0].lower().strip()
    argument = parts[1].strip() if len(parts) > 1 else ""
    
    return command, argument

def search_flathub_apps(query):
    """Cerca app su Flathub e restituisce i risultati"""
    url = f"https://flathub.org/api/v1/apps/search/{query}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Errore ricerca Flathub: {str(e)}")
        return None

def get_flathub_app_details(app_id):
    """Ottiene i dettagli di un'app da Flathub"""
    url = f"https://flathub.org/api/v1/apps/{app_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Errore dettagli app Flathub: {str(e)}")
        return None

def get_flathub_download_link(app_id):
    """Genera il link di download diretto per un'app Flathub"""
    return f"https://dl.flathub.org/repo/appstream/{app_id}.flatpakref"

def handle_flathub_command(command, argument):
    """Gestisce i comandi relativi a Flathub"""
    if command == "flathub":
        if not argument:
            return "❌ Specifica un'app da cercare su Flathub. Esempio: @flathub firefox"
        
        # Cerca l'app su Flathub
        results = search_flathub_apps(argument)
        if not results:
            return f"❌ Nessun risultato trovato per '{argument}' su Flathub"
        
        # Prendi il primo risultato
        app = results[0]
        app_id = app.get("flatpakAppId")
        app_name = app.get("name", "Sconosciuto")
        
        # Ottieni il link di download
        download_link = get_flathub_download_link(app_id)
        
        return (
            f"📦 {app_name} su Flathub:\n"
            f"🔗 Download diretto: {download_link}\n"
            f"ℹ️ Dettagli: https://flathub.org/apps/{app_id}"
        )
    
    elif command == "flathub_download":
        if not argument:
            return "❌ Specifica l'ID dell'app da scaricare. Esempio: @flathub_download org.mozilla.firefox"
        
        # Verifica se l'app esiste
        app_details = get_flathub_app_details(argument)
        if not app_details:
            return f"❌ App con ID '{argument}' non trovata su Flathub"
        
        # Genera il link di download
        download_link = get_flathub_download_link(argument)
        
        return (
            f"⬇️ Download diretto per {app_details.get('name', argument)}:\n"
            f"{download_link}\n\n"
            f"Per installare: flatpak install --from {download_link}"
        )
    
    return None
# --- Verifica disponibilità di Winget all'avvio (globale) ---
_WINGET_AVAILABLE = False
try:
    subprocess.run(['winget', '--version'], capture_output=True, text=True, check=True)
    _WINGET_AVAILABLE = True
    print("Winget è disponibile sul sistema.")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("ATTENZIONE: Winget non è disponibile. Le funzioni Winget potrebbero non funzionare.")

# --- Verifica disponibilità di Winget all'avvio (globale) ---
def search_windows_apps_online(query):
    """
    Cerca app Windows online usando una ricerca web per trovare link di download ufficiali.
    """
    search_term = f"{query} download ufficiale Windows"
    results = search_duckduckgo(search_term) # Usa la tua funzione esistente per la ricerca web

    if not results:
        return []

    # Filtra e prioritizza i risultati per trovare link di download ufficiali.
    # Questa è una euristica e può essere migliorata per la tua specifica necessità.
    filtered_urls = []
    official_keywords = ["microsoft.com", "google.com", "mozilla.org", "videolan.org", "spotify.com", "7-zip.org"]
    winget_web_interfaces = ["winget.run", "winstall.app"] # Siti che mostrano info Winget

    for url in results:
        # Priorità 1: Siti ufficiali di software molto noti o Winget web interfaces
        if any(keyword in url.lower() for keyword in official_keywords + winget_web_interfaces):
            filtered_urls.append(url)
        # Priorità 2: Siti che includono "download" e "official" nel percorso, evitando aggregatori noti
        elif "download" in url.lower() and not any(bad_domain in url for bad_domain in ["softonic.com", "filehippo.com", "updatestar.com"]):
            filtered_urls.append(url)
    
    # Rimuovi duplicati mantenendo l'ordine originale
    seen = set()
    unique_filtered_urls = []
    for url in filtered_urls:
        if url not in seen:
            unique_filtered_urls.append(url)
            seen.add(url)

    return unique_filtered_urls[:3] # Restituisce i primi 3 URL più rilevanti

def get_windows_app_details_from_url(url, original_query):
    """
    Tenta di estrarre dettagli base da una URL di download per un'app Windows.
    Questo è un approccio semplificato dato che non abbiamo i dati strutturati di Winget.
    """
    name = original_query.capitalize() # Nome predefinito capitalizzato dalla query
    is_proprietary = True # Predefinito a proprietario, poi proviamo a indovinare
    publisher = "Sconosciuto (verificare pagina)"

    # Heuristiche basate su URL per nome e licenza
    if "mozilla.org/firefox" in url.lower():
        name = "Mozilla Firefox"
        is_proprietary = False # Firefox è open source
        publisher = "Mozilla"
    elif "google.com/chrome" in url.lower():
        name = "Google Chrome"
        is_proprietary = True
        publisher = "Google LLC"
    elif "microsoft.com/edge" in url.lower():
        name = "Microsoft Edge"
        is_proprietary = True
        publisher = "Microsoft Corporation"
    elif "videolan.org/vlc" in url.lower():
        name = "VLC Media Player"
        is_proprietary = False
        publisher = "VideoLAN"
    elif "7-zip.org" in url.lower():
        name = "7-Zip"
        is_proprietary = False
        publisher = "Igor Pavlov"
    elif "spotify.com" in url.lower():
        name = "Spotify"
        is_proprietary = True
        publisher = "Spotify AB"
    elif "winget.run" in url.lower() or "winstall.app" in url.lower():
        # Se è un'interfaccia Winget, proviamo a estrarre il nome dalla query
        name = original_query.capitalize() + " (dal catalogo Winget)"
        publisher = "Vari (dipende dall'app)"


    return {
        'name': name,
        'homepage': url,          # L'URL di riferimento è la homepage/pagina di download
        'installer_url': url,     # In questo contesto, è la stessa cosa
        'is_proprietary': is_proprietary,
        'publisher': publisher
    }

def handle_winget_command(command, argument):
    """
    Gestisce i comandi relativi alle app Windows tramite ricerca web.
    """
    if command == "winget":
        if not argument:
            return "❌ Specifica un'app Windows da cercare. Esempio: @winget firefox"
        
        # Ora cerchiamo online invece di eseguire winget localmente
        download_urls = search_windows_apps_online(argument)

        if not download_urls:
            return (
                f"❌ Non sono riuscito a trovare un link di download ufficiale per '{argument}' per Windows.\n"
                "Potresti provare a cercare manualmente su Google o DuckDuckGo."
            )
        
        # Prendo il primo risultato come il più rilevante
        main_url = download_urls[0]
        app_details = get_windows_app_details_from_url(main_url, argument) # Usa una funzione semplificata per estrarre i dettagli

        name = app_details['name']
        homepage = app_details['homepage']
        is_proprietary = app_details['is_proprietary']
        publisher = app_details['publisher']
        
        license_note = ""
        if is_proprietary:
            license_note = (
                f"Nota: **{name}** è un software proprietario. "
                f"La licenza d'uso è definita dall'editore ({publisher})."
            )
        else:
            license_note = (
                f"Nota: **{name}** è un software open source/gratuito. "
                f"La licenza d'uso è definita dall'editore ({publisher})."
            )

        response = f"""
📦 **{name}** per Windows:

1.  **Scarica l'installer:**
    Visita la pagina ufficiale per il download: {homepage}
    *(Dovrai scaricare e installare l'app manualmente dal sito.)*

ℹ️ Pagina ufficiale dell'app: {homepage}

{license_note}
        """
        return response.strip()
    
    return None # Comando Winget non riconosciuto (es. se avessi altri sottocomandi)
# --- Nuove Funzioni per Snap Store ---
def search_snap_store_online(query):
    """
    Cerca app Snap online usando una ricerca web per trovare link ufficiali su snapcraft.io.
    """
    app.logger.info(f"Cercando app Snap online per: {query}")
    search_term = f"{query} snapcraft.io"
    results = search_duckduckgo(search_term)
    return [url for url in results if "snapcraft.io" in url.lower()][:3]

def get_snap_app_details_from_url(url, original_query):
    """
    Estrae dettagli base da una URL di Snapcraft per un'app Snap.
    """
    name = original_query.capitalize() + " (Snap)"
    is_proprietary = "proprietary" in url.lower() # Semplice euristica per licenza
    publisher = "Snapcraft Community / Canonical" # Default

    # Migliora l'estrazione del nome e del publisher se possibile
    if "snapcraft.io/store" not in url.lower():
        try:
            # Estrai il nome dal path dell'URL (es. snapcraft.io/firefox -> firefox)
            name_from_url = url.split('/')[-1].replace('-', ' ').title()
            if name_from_url and len(name_from_url) > 1: # Assicura che non sia vuoto o solo un carattere
                name = name_from_url + " (Snap)"
        except Exception as e:
            app.logger.warning(f"Impossibile estrarre nome Snap da URL {url}: {e}")
            
    # Euristiche per alcune app comuni
    if original_query.lower() == "spotify":
        name = "Spotify (Snap)"
        is_proprietary = True
        publisher = "Spotify"
    elif original_query.lower() == "vlc":
        name = "VLC media player (Snap)"
        is_proprietary = False
        publisher = "VideoLAN"

    return {
        'name': name,
        'homepage': url,
        'installer_info': f"Installazione via Snap: `sudo snap install {original_query.lower()}`", # Comando di installazione Snap
        'is_proprietary': is_proprietary,
        'publisher': publisher,
        'platform': 'Linux (Snap)'
    }

def handle_snap_command(argument):
    """
    Gestisce i comandi relativi alle app Snap.
    """
    if not argument:
        return "❌ Specifica un'app Snap da cercare. Esempio: @snap spotify"
    
    download_urls = search_snap_store_online(argument)

    if not download_urls:
        return (
            f"❌ Non sono riuscito a trovare un pacchetto Snap ufficiale per '{argument}'.\n"
            "Potrebbe non esistere o il nome non è corretto. Prova a cercare su snapcraft.io."
        )
    
    main_url = download_urls[0]
    app_details = get_snap_app_details_from_url(main_url, argument)

    name = app_details['name']
    homepage = app_details['homepage']
    installer_info = app_details['installer_info']
    is_proprietary = app_details['is_proprietary']
    publisher = app_details['publisher']
    platform = app_details['platform']
    
    license_note = ""
    if is_proprietary:
        license_note = (
            f"Nota: **{name}** è un software proprietario. "
            f"La licenza d'uso è definita dall'editore ({publisher})."
        )
    else:
        license_note = (
            f"Nota: **{name}** è un software open source/gratuito. "
            f"La licenza d'uso è definita dall'editore ({publisher})."
        )

    response = f"""
📦 **{name}** per {platform}:

1.  **Pagina ufficiale:** {homepage}
2.  **Installazione:** `{installer_info}`
    *(Apri il terminale sul tuo sistema Linux e incolla il comando.)*

{license_note}
    """
    return response.strip()


def search_fdroid_online(query):
    """
    Cerca app F-Droid online usando una ricerca web per trovare link ufficiali su f-droid.org.
    """
    app.logger.info(f"Cercando app F-Droid online per: {query}")
    search_term = f"{query} f-droid.org"
    results = search_duckduckgo(search_term)
    # Filtra per URL che sembrano pagine di pacchetto F-Droid (es. /packages/nome.app/)
    return [url for url in results if "f-droid.org/packages/" in url.lower()][:3]

def get_fdroid_app_details_from_url(url, original_query):
    """
    Estrae dettagli base da una URL di F-Droid per un'app Android.
    """
    name = original_query.capitalize() + " (F-Droid)"
    is_proprietary = False # Le app su F-Droid sono sempre open source
    publisher = "F-Droid Community / Sviluppatore originale" # Default

    try:
        # Estrai il nome del pacchetto dall'URL per un nome più preciso
        match = re.search(r"f-droid\.org/packages/([a-zA-Z0-9\._-]+)/", url)
        if match:
            package_id = match.group(1)
            # Tenta di pulire il nome del pacchetto per renderlo più leggibile
            cleaned_name = package_id.split('.')[-1].replace('_', ' ').title()
            if cleaned_name:
                name = cleaned_name + " (F-Droid)"
    except Exception as e:
        app.logger.warning(f"Impossibile estrarre nome F-Droid da URL {url}: {e}")

    # Euristiche per alcune app comuni
    if original_query.lower() == "newpipe":
        name = "NewPipe (F-Droid)"
        publisher = "Team NewPipe"
    elif original_query.lower() == "signal":
        name = "Signal (F-Droid)"
        publisher = "Signal Messenger, LLC"

    return {
        'name': name,
        'homepage': url,
        'installer_info': f"Scarica direttamente da F-Droid.org o tramite l'app F-Droid.",
        'is_proprietary': is_proprietary, # Sempre False per F-Droid
        'publisher': publisher,
        'platform': 'Android (F-Droid)'
    }

def handle_fdroid_command(argument):
    """
    Gestisce i comandi relativi alle app F-Droid.
    """
    try: # Aggiunto try-except
        if not argument:
            return "❌ Specifica un'app F-Droid da cercare. Esempio: @fdroid newpipe"
        
        download_urls = search_fdroid_online(argument)

        if not download_urls:
            return (
                f"❌ Non sono riuscito a trovare un'app ufficiale per '{argument}' su F-Droid.\n"
                "Potrebbe non esistere o il nome non è corretto. Prova a cercare su f-droid.org."
            )
        
        main_url = download_urls[0]
        app_details = get_fdroid_app_details_from_url(main_url, argument)

        name = app_details['name']
        homepage = app_details['homepage']
        installer_info = app_details['installer_info']
        is_proprietary = app_details['is_proprietary']
        publisher = app_details['publisher']
        platform = app_details['platform']
        
        license_note = (
            f"Nota: **{name}** è un software open source/gratuito. "
            f"La licenza d'uso è definita dall'editore ({publisher})."
        )

        response = f"""
📦 **{name}** per {platform}:

1.  **Pagina ufficiale:** {homepage}
2.  **Installazione:** {installer_info}
    *(Dovrai scaricare e installare l'app manualmente sul tuo dispositivo Android o usare l'app F-Droid.)*

{license_note}
        """
        return response.strip()
    except Exception as e:
        app.logger.error(f"Errore nella gestione del comando F-Droid per '{argument}': {str(e)}")
        return f"❌ Si è verificato un errore interno durante l'elaborazione del comando F-Droid. Controlla i log del server per maggiori dettagli."

# --- Funzione principale della tua IA che elabora l'input dell'utente ---
def process_user_input(user_input):
    """
    Funzione principale della tua IA che elabora l'input dell'utente.
    """
    if user_input.lower() == "@app":
        return """
Repository per Download Manager:
- @Flathub - [Nome-App] (per Linux)
- @Winget - [Nome-App] (per Windows)
- @Snap - [Nome-App] (per Linux)
- @F-Droid - [Nome-App] (per Android)
(Nota: Su Winget sono disponibili sia app gratuite che a pagamento, e con licenze diverse. Il Download Manager fornisce l'installer, ma la licenza d'uso è definita dall'editore dell'app.)
"""
 
    elif user_input.lower().startswith("@winget"): # Usiamo direttamente user_input.lower()
        parts = user_input.lower().split(" ", 1)
        argument = parts[1].strip() if len(parts) > 1 else ""
        return handle_winget_command("winget", argument)
    
    elif user_input.lower().startswith("@snap"): # Usiamo direttamente user_input.lower()
        parts = user_input.lower().split(" ", 1)
        argument = parts[1].strip() if len(parts) > 1 else ""
        return handle_snap_command(argument)
    
    elif user_input.lower().startswith("@fdroid"): # Usiamo direttamente user_input.lower()
        parts = user_input.lower().split(" ", 1)
        argument = parts[1].strip() if len(parts) > 1 else ""
        return handle_fdroid_command(argument)
    
    elif user_input.lower().startswith("@flathub"): # Usiamo direttamente user_input.lower()
        parts = user_input.lower().split(" ", 1)
        argument = parts[1].strip() if len(parts) > 1 else ""
        return handle_flathub_command(argument)
    
    else:
        return "Comando non riconosciuto. Prova '@app' per vedere i repository disponibili."


from flask import session
import requests
import json


def handle_quick_commands(message, experimental_mode=False):
    """
    Gestisce i comandi rapidi di ArcadiaAI (inclusi quelli per Flathub e Winget).
    """
    msg_lower = message.strip().lower()
    command, argument = parse_quick_command(message)
    if command is None:
        return None

    # --- Gestione comandi Flathub ---
    flathub_response = handle_flathub_command(command, argument)
    if flathub_response:
        return flathub_response
    

    # --- NUOVO: Gestione comandi Winget ---
    winget_response = handle_winget_command(command, argument)
    if winget_response:
        return winget_response

    # --- Estensioni NSK ---
    for ext in EXTENSIONS.values():
        try:
            if ext.can_handle(command):
                return ext.handle(argument)
        except Exception as e:
            return f"❌ Errore nell'estensione: {e}"

    if msg_lower == "@impostazioni modalità sperimentale disattiva":
        return "❎ Modalità sperimentale disattivata!"

    if msg_lower == "@impostazioni modalità sperimentale attiva":
        return "✅ Modalità sperimentale attivata!"

    if command == "cerca":
        if not argument:
            return "❌ Devi specificare cosa cercare. Esempio: @cerca seconda guerra mondiale"
        results = search_duckduckgo(argument)
        results = [url for url in results if "duckduckgo.com/y.js" not in url and "ad_domain" not in url] if results else []
        if results:
            testo = estrai_testo_da_url(results[0])
            if testo:
                breve = ". ".join(testo.split(".")[:2]).strip() + "."
                return (
                    f"🔍 Risultati per '{argument}':\n\n"
                    f"**Sintesi dal primo risultato:**\n{breve}\n\n"
                    + "\n".join(f"- {url}" for url in results[:3])
                )
            else:
                return f"🔍 Risultati per '{argument}':\n\n" + "\n".join(f"- {url}" for url in results[:3])
        return f"❌ Nessun risultato trovato per '{argument}'"
    
    if command == "estensioni":
        if not EXTENSIONS:
            return "🔌 Nessuna estensione installata."
        elenco = "\n".join(
            f"- {getattr(mod, '__name__', name).replace('nsk_', '')}" for name, mod in EXTENSIONS.items()
        )
        return f"🔌 Estensioni installate:\n{elenco}"
    elif command == "versione":
        return "🔄 Versione attuale: 1.5.6"
    
    elif command == "telegraph" and argument:
        if "saggio" in argument or "scrivi" in argument:
            prompt = argument
            if gemini_model:
                generated_text, telegraph_url = generate_with_gemini(prompt, "Articolo generato da ArcadiaAI")
            else:
                generated_text = chat_with_huggingface(prompt, [])
                telegraph_url = publish_to_telegraph("Articolo generato da ArcadiaAI", generated_text)
            if telegraph_url and not telegraph_url.startswith("⚠️"):
                return f"📝 Articolo pubblicato su Telegraph: {telegraph_url}"
            return telegraph_url or "❌ Errore nella pubblicazione"
        else:
            telegraph_url = publish_to_telegraph("Articolo generato da ArcadiaAI", argument)
            return f"📝 Articolo pubblicato su Telegraph: {telegraph_url}"

    elif command == "meteo" and argument:
        return meteo_oggi(argument)
    
    elif command == "data":
        import locale
        import datetime
        locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")
        oggi = datetime.datetime.now().strftime("%A %d %B %Y")
        return f"📅 Oggi è {oggi}"

    elif command == "source":
        return "🔗 Repository GitHub: https://github.com/Mirko-linux/Nova-Surf/tree/main/ArcadiaAI "

    elif command == "arcadia":
        return "🔗 Profilo della Repubblica di Arcadia: https://t.me/Repubblica_Arcadia"

    elif command == "@impostazioni lingua italiano":
        return "🇮🇹 Lingua cambiata in italiano!"

    elif command == "@impostazioni lingua inglese":
        return "🇬🇧 Lingua cambiata in inglese!"

    elif command == "app":
        return (
            "Repository per download manager:\n"
            "- @flathub - [nome-app]: scarica un'app per Linux(flatpak)\n"
            "- @winget - [nome-app]: scarica un'app per Windows\n"
            "- @snap - [nome-app]: scarica un'app per Linux (Snapd)\n"
            "- @fdroid - [nome-app]: scarica un'app per Android (F-Droid)\n"
            "(Nota: Su Winget sono disponibili sia app gratuite che a pagamento, e con licenze diverse. Il Download Manager fornisce l'installer, ma la licenza d'uso è definita dall'editore dell'app.)"
        )

    elif command == "snap":
        if not argument:
            return "❌ Specifica un'app Snap da cercare. Esempio: @snap firefox"
        return handle_snap_command(argument)

    elif command == "fdroid":
        if not argument:
            return "❌ Specifica un'app F-Droid da cercare. Esempio: @fdroid newpipe"
        return handle_fdroid_command(argument)

    elif command == "tos":
        return "📜 Termini di Servizio: https://arcadiaai.netlify.app/documentazioni"

    elif command == "codice_sorgente":
        return "🔗 Codice sorgente di ArcadiaAI:https://github.com/Mirko-linux/Nova-Surf/tree/main/ArcadiaAI"

    elif command == "info":
        return (
            "ℹ️ Informazioni su ArcadiaAI:\n\n"
            "Versione: 1.5.0\n"
            "Modello: CES basato su Google Gemini e Huggingface\n"
            "Lingua: Italiano e inglese (beta)\n"
            "Creatore: Mirko Yuri Donato\n"
            "Licenza: GNU GPL v3.0+\n"
            "Repository: https://github.com/Mirko-linux/Nova-Surf/tree/main/ArcadiaAI\n"
            "Termini di Servizio: https://arcadiaai.netlify.app/documentazioni"
        )

    elif command == "crea" and argument.lower().startswith("zip"):
        return "Per creare uno ZIP allega i file e usa il comando dalla chat. Il file ZIP verrà generato dal frontend."

    elif command == "impostazioni":
        return (
            "⚙️ Menu Impostazioni :\n\n"
            "- Modalità Sperimentale: attiva/disattiva\n"
            "- Lingua: italiano/inglese\n"
            "- Tema: chiaro/scuro\n"
            "- Modalità Sviluppatore: attiva/disattiva\n"
            "Usa i comandi @impostazioni [opzione] per modificare le impostazioni."
            "Nota: Alcune opzioni potrebbero non essere disponibili in questa versione."
        )
    
   
    elif command == "immagine":
        if not argument:
            return "❌ Specifica cosa disegnare. Esempio: @immagine drago pixel art su un hoverboard"

        try:
            response = requests.post(
                "https://arcadiaai.onrender.com/api/ces-image",
                headers={"Content-Type": "application/json"},
                json={"prompt": argument},
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                if image_url:
                    return (
                        f'<div style="text-align: center;">'
                        f'<img src="{image_url}" alt="{argument}" '
                        f'style="max-width: 512px; width: 100%; height: auto; '
                        f'margin-top: 8px; border-radius: 6px;">'
                        f'</div>'
                    )
                return "⚠️ L’API ha risposto ma non ha fornito nessuna immagine."
            return f"❌ Errore dall’API CES Image: {response.status_code}"

        except Exception as e:
            return f"❌ Errore nella generazione dell’immagine: {e}"
    
    elif command == "privacy":
        return (
            "🔒 Privacy Policy:\n\n"
            "I tuoi dati non vengono memorizzati o condivisi. "
            "Le conversazioni sono salvate in locale. "
            "Per maggiori dettagli, consulta i Termini di Servizio."
        )
    
    elif command == "cancella_conversazione":
        return "🗑️ Cronologia della conversazione"
    elif command == "aiuto": # Questo blocco è ora il comando generico @aiuto
        return (
            "🎯 Comandi rapidi disponibili:\n\n"
            "@cerca [query] - Cerca su internet\n"
            "@telegraph [testo] - Pubblica su Telegraph\n"
            "@meteo [luogo] - Ottieni il meteo\n"
            "@data - Mostra la data di oggi\n"
            "@aiuto - Mostra questa guida\n"
            "@impostazioni modalità sperimentale disattiva - Disattiva la modalità sperimentale\n"
            "@impostazioni - apre il menu delle impostazioni\n"
            "@impostazioni lingua [nome lingua] - Cambia lingua\n"
            "@impostazioni tema [chiaro|scuro] - Cambia tema\n"
            "@impostazioni modalità sviluppatore attiva - Attiva la modalità sviluppatore\n"
            "@ToS - Mostra i Termini di Servizio\n"
            "@Arcadia - Mostra il profilo della Repubblica di Arcadia\n"
            "@info - Mostra informazioni su ArcadiaAI\n"
            "@impostazioni modalità sperimentale attiva - Attiva la modalità sperimentale"
            "@codice_sorgente - Mostra il codice sorgente di ArcadiaAI\n"
            "@impostazioni - Mostra il menu delle impostazioni\n"
            "@estensioni - Mostra le estensioni installate\n"
            "@estensioni [nome estensione] - Mostra informazioni su un'estensione\n"
            "@privacy - Mostra la privacy policy\n"
            "@app - Mostra le repository che supportano il Download Manager\n"
            "@flathub [nome app] - Cerca un'app su Flathub e restituisce il download diretto\n"
            "@flathub_download [ID app] - Scarica un'app specifica da Flathub\n"
            "@winget [nome app] - Cerca un'app su Winget e restituisce il download diretto (NOVITÀ!)\n" # Aggiunto qui
            "@cesplus - Usa il modello CES Plus per risposte avanzate\n"
            "@crea zip - genera un file ZIP con file dati dall'utente\n"
            "@esporta - Esporta l'ultima conversazione in un file TXT\n"
            "@importa - Importa la una conversazione da un file TXT tramite NovaSync\n"
            "Per altre domande, chiedi pure!"
        )

    # Se nessun comando è riconosciuto
    return f"❌ Comando '{command}' non riconosciuto. Scrivi '@aiuto' per la lista dei comandi."
    
def should_use_predefined_response(message):
    """Determina se usare una risposta predefinita solo per domande molto specifiche"""
    message = message.lower().strip()
    exact_matches = [
        "chi sei esattamente",
        "qual è la tua identità precisa",
        "elencami tutte le tue funzioni",
        # ... altre domande esatte
    ]
    return any(exact_match in message for exact_match in exact_matches)
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Avvio server Flask sulla porta {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    
async def telegram_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    chat_id = update.message.chat.id
    
    data = {
        "message": message,
        "conversation_history": [],
        "api_provider": "gemini"
    }
    
    with app.test_request_context('/', json=data):
        response = chat_route()
        reply = response.json.get("reply", "❌ Errore nella generazione della risposta")
    
    await context.bot.send_message(chat_id=chat_id, text=reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Ciao! Sono ArcadiaAI 🚀
    
Comandi disponibili:
/start - Mostra questo messaggio
/help - Guida completa
/info - Informazioni sul bot
/help_commands - Comandi disponibili"""
    await update.message.reply_text(help_text)

# Poi definisci le funzioni di avvio
async def run_telegram_bot_async():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Aggiungi questo per gestire meglio gli aggiornamenti
    application.updater = None  # Disabilita l'updater predefinito
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler))
    
    print("🤖 Bot Telegram avviato!")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Avvia esplicitamente il polling
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
@app.route('/static/<path:filename>')
def static_files(filename):
    """Verifica esplicita dei file statici"""
    return send_from_directory(app.static_folder, filename)

@app.after_request
def add_header(response):
    """Disabilita cache durante lo sviluppo"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

def run_telegram_bot():
    """Funzione per avviare il bot Telegram in un thread separato"""
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Aggiungi gestori di comando
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler))

        print("🤖 Bot Telegram avviato!")
        
        # Usa run_polling con parametri specifici
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            timeout=30,
            connect_timeout=10,
            pool_timeout=10,
            stop_signals=None,
            close_loop=False
        )

    except Exception as e:
        print(f"❌ Errore nel bot Telegram: {e}")

@app.route(f'/webhook_{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    """Endpoint per ricevere gli update da Telegram via webhook"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
    return '', 200

def set_webhook():
    """Configura il webhook per Telegram"""
    try:
        url = f" https://arcadiaai.onrender.com/{TELEGRAM_TOKEN}" 
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": url, "max_connections": 40},
            timeout=10
        )
        print(f"Webhook configurato: {response.json()}")
    except Exception as e:
        print(f"Errore configurazione webhook: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
