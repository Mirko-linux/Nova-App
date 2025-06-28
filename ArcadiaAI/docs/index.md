# 🌌 ArcadiaAI

> *Intelligenza artificiale modulare, trasparente e responsabile — costruita per pensare, non solo rispondere.*

**ArcadiaAI** è un framework conversazionale open source, progettato per integrare più modelli linguistici in un’architettura snella, adattabile e rispettosa della privacy. Nasce con un obiettivo preciso: offrire un assistente neurale libero da vincoli, interamente controllabile, costruito in Italia con tecnologie accessibili e documentate.

---

## 🇮🇹 Origine

ArcadiaAI è sviluppato e mantenuto in Italia. L’idea è semplice: creare un’AI che non imponga dipendenze, non raccolga dati inutili e possa essere compresa, adattata e migliorata da chiunque. Nessuna multinazionale, nessuna infrastruttura imposta: solo codice aperto, leggibile, funzionante.

---

## 🧭 Filosofia

- 🔐 **Rispetto dei dati**: non raccoglie né conserva conversazioni
- 🧠 **Motori multipli**, selezionabili e componibili (CES 1.5, CES 360, CES Plus)
- 🛠 **Routing flessibile**: ogni richiesta va al modello più adatto
- 🌐 **Nessun vendor lock-in**: l’uso di API esterne è opzionale
- 🧩 **Struttura modulare**: puoi spegnere o sostituire ogni componente

---

## 🔩 Componenti principali

| Modello     | Funzione principale                               | Provider              |
|-------------|---------------------------------------------------|------------------------|
| **CES 360** | Risposte standard, alta coerenza, no API esterne  | Meta LLaMA 3.3 via Puter.js |
| **CES 1.5** | Elaborazione rapida tramite LLM esterno           | Google Gemini API     |
| **CES Plus**| Output più creativo e ragionato                   | Google Gemini API     |

> CES 1.5 e CES Plus usano Gemini API (Google). Sono componenti opzionali.

---

## ⚙️ Architettura

- Backend **Flask/Python**
- API RESTful (`/chat`) multi-provider
- Interfaccia web inclusa
- Hosting su [Render](https://render.com) (gratuito)
- Ping automatico ogni 5 minuti con UpTimeRobot
- Nessuna dipendenza da database

---

## 🧪 Stato del progetto

- Versione: `v1.5.5`
- Licenza: [GNU GPL v3.0+](https://www.gnu.org/licenses/gpl-3.0.html)
- Hosting: Render (free tier)

---

## 📎 Requisiti minimi

- Python 3.10+
- Ambiente virtuale consigliato
- `.env` solo se usi provider esterni

---

## 📬 Contatti

Per segnalazioni o contributi:  
📧 **novasurf26@gmail.com**

> ArcadiaAI è una piattaforma libera — costruita in Italia, con l’idea che l’intelligenza vada spiegata, non nascosta.
