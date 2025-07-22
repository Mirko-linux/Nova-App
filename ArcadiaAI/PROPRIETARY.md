# Elenco Componenti Proprietari

In questo documento sono riportati tutti i componenti proprietari utilizzati da **ArcadiaAI**.

---

## Tabella Riassuntiva

| Componente                | Libreria / Metodo                      | File coinvolto             | Note                                                  |
|--------------------------|-----------------------------------------|----------------------------|-------------------------------------------------------|
| Google Gemini            | `google.generativeai`                   | `ArcadiaAI/sr/app.py`      | Modelli Gemini 2.0 flash lite & 2.5 flash             |
| Google Cloud TTS         | `google.cloud.texttospeech_v1`          | `ArcadiaAI/sr/app.py`      | Sintesi vocale                                        |
| OpenWeatherMap API       | API HTTP                                | `ArcadiaAI/sr/app.py`      | Richiesta meteo con API Key                           |
| DuckDuckGo Search Scraper| `requests`, `BeautifulSoup`             | `ArcadiaAI/sr/app.py`      | Motore di ricerca principale, scraping HTML non ufficiale |
| Brave Search Scraper     | `requests`, `BeautifulSoup`             | `ArcadiaAI/sr/app.py`      | Fallback per DuckDuckGo, scraping HTML                |
| Meta Llama 3.3-70B       | [`Puter.js`](https://js.puter.com/v2/)  | `ArcadiaAI/sr/app.py`    | Accesso via API Puter, licenza Meta, modello proprietario |

---

## Dettagli dei Componenti

### 1. Google Gemini API  
**File:** `ArcadiaAI/sr/app.py`  
**Libreria:** `google.generativeai`  
**Modelli utilizzati:**
```python
import google.generativeai as genai
gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
ces_plus_model = genai.GenerativeModel('gemini-2.5-flash')
```
> Modelli proprietari di Google. Licenza commerciale.

---

### 2. Google Cloud Text-to-Speech  
**File:** `ArcadiaAI/sr/app.py`  
**Libreria:** `google.cloud.texttospeech_v1`  
```python
from google.cloud import texttospeech_v1 as texttospeech
```
> Servizio di sintesi vocale proprietario di Google Cloud.

---

### 3. OpenWeatherMap API  
**File:** `ArcadiaAI/sr/app.py`  
**Funzione:** `meteo_oggi(città)`  
```python
url = f"http://api.openweathermap.org/data/2.5/weather?q={città_codificata}&appid={API_KEY}&units=metric&lang=it"
```
> API proprietaria. Richiede chiave per l'accesso.

---

### 4. DuckDuckGo Search Scraper  
**File:** `ArcadiaAI/sr/app.py`  
**Funzione:** `search_duckduckgo(query, lang)`  
```python
res = requests.get(url, headers=headers, timeout=12)
soup = BeautifulSoup(res.text, 'html.parser')
```
> DuckDuckGo è il motore di ricerca predefinito.  
> Utilizza scraping HTML non ufficiale, potenzialmente soggetto a restrizioni.

---

### 5. Brave Search Scraper  
**File:** `ArcadiaAI/sr/app.py`  
**Funzione:** `search_brave(query, lang)`  
```python
res = requests.get(url, headers=headers, timeout=12)
soup = BeautifulSoup(res.text, 'html.parser')
```
> Utilizzato come fallback se DuckDuckGo non restituisce risultati.  
> Anche questo modulo usa scraping HTML non ufficiale.

---

### 6. Meta Llama 3.3-70B via Puter.js  
**File:** `ArcadiaAI/app/app.py`  
**Libreria:** [`https://js.puter.com/v2/`](https://js.puter.com/v2/)  
**Modello:** Meta Llama 3.3-70B  
> Modello LLM proprietario di Meta. Accesso tramite API di Puter. Licenza commerciale.

---

## Note sulla Licenza

ArcadiaAI è un progetto **open source** che integra componenti e servizi **proprietari** per l’accesso a modelli avanzati e fonti esterne.  
Tutti gli elementi elencati sono utilizzati nel rispetto delle loro licenze. Per distribuzioni più restrittive (es. F-Droid), si consiglia di sviluppare una variante più libera.

---

**Ultimo aggiornamento:** 20 luglio 2025  

```
