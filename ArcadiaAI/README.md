<p align="center">
  <img src="sr/static/logo_arcadia_ai.jpg" alt="Logo ArcadiaAI" width="200"/>
</p>

<h1 align="center">ArcadiaAI</h1>
<p align="center"><em>L'IA democratica e libera per tutti</em></p>

**ArcadiaAI** è una piattaforma modulare per l’intelligenza artificiale conversazionale, progettata per essere libera, accessibile e sovrana.
Fondata da [Mirko Donato](https://github.com/Mirko-linux), ArcadiaAI unisce modelli principalmente open-source, interfacce leggere e backend distribuiti per offrire esperienze AI potenti e gratuite.

---

## 🧠 Visione

> “L’intelligenza artificiale deve essere un bene accessibile a tutti, ArcadiaAI nasce dal desiderio di democratizzare l'Intelligenza Artificiale"

ArcadiaAI nasce per sfidare i modelli proprietari e centralizzati.
Qui, ogni modulo è pensato per essere:

* **Open-source**
* **Senza barriere d’accesso**
* **Eseguibile dal browser**
* **Sostenibile e decentralizzato**

---

## 🧩 Modelli principali

| Modulo          | Descrizione                                           |
| :-------------- | :---------------------------------------------------- |
| **CES 1.5** | Modello predefinito di ArcadiaAI, basato su Google Gemini |
| **DeepSeek R1** | Modello linguistico open source gestito tramite Openrouter |
| **CES 360** | Interfaccia browser per LLaMA 3.3 70B, senza API key  |
| **CES Plus** | Variante di CES 360 e 1.5 progettata per i ragionamenti |
| **CES 360e** | Versione più leggera di 360 basato su LLaMA 3.1 8B    |

---

## 🚀 Inizia Subito

Benvenuto in ArcadiaAI! Sei pronto a esplorare il futuro dell'intelligenza artificiale conversazionale? Iniziare è semplice e non richiede alcuna configurazione complessa.

### 💻 Utilizza ArcadiaAI Direttamente dal Browser

Per un'esperienza immediata, puoi accedere ad ArcadiaAI direttamente tramite il tuo browser. Non è necessario installare nulla:

1.  **Visita il nostro sito web:** [qui](https://arcadiaai.netlify.app/)
2.  **Scegli il tuo modello preferito:** Seleziona tra i nostri moduli disponibili, come **CES 1.5** per un'esperienza generale o **CES 360** per interazioni più avanzate.
3.  **Inizia a chattare!** Digita le tue domande o richieste e scopri la potenza di ArcadiaAI.

### 🛠️ Esegui ArcadiaAI Localmente (per sviluppatori)

Se sei uno sviluppatore e desideri contribuire o personalizzare ArcadiaAI, puoi clonare il repository ed eseguirlo localmente.

#### Prerequisiti

Assicurati di avere installato:

* **Node.js** (versione 18 o superiore)
* **npm** (solitamente incluso con Node.js)
* **Git**

#### Passi per l'installazione e l'avvio

1.  **Clona il repository:**

    ```bash
    git clone [https://github.com/Mirko-linux/Nova-App.git](https://github.com/Mirko-linux/Nova-App.git)
    cd Nova-App/ArcadiaAI
    ```

2.  **Installa le dipendenze:**

    ```bash
    npm install
    ```

3.  **Avvia l'applicazione:**

    ```bash
    npm start
    ```

    Questo avvierà l'applicazione in modalità di sviluppo. Potrai accedere al chatbot tramite il tuo browser all'indirizzo `http://localhost:3000` (o la porta indicata).

---

## 🍴 Fork e Contribuisci

Se sei uno sviluppatore e desideri contribuire al progetto ArcadiaAI, personalizzare i moduli o integrare nuove funzionalità, ti invitiamo a effettuare il **fork del repository**.

### Prerequisiti per il Fork

Per poter lavorare efficacemente sul codice, assicurati di avere familiarità con:

* **Node.js** e **npm**: per gestire le dipendenze del progetto.
* **Git**: per clonare, committare e inviare le modifiche.
* **Concetti base di sviluppo web**: HTML, CSS, JavaScript per le interfacce e i backend.

### Come Effettuare il Fork e Iniziare

1.  **Effettua il Fork del Repository:**
    Naviga alla pagina GitHub di [ArcadiaAI](https://github.com/Mirko-linux/Nova-App/tree/main/ArcadiaAI) e clicca sul pulsante "**Fork**" in alto a destra. Questo creerà una copia del repository sul tuo account GitHub.

2.  **Clona il Tuo Fork Localmente:**
    Dal tuo terminale, clona la tua copia del repository.

    ```bash
    git clone https://github.com/Mirko-linux/Nova-App.git
    ```

    Poi naviga nella cartella di ArcadiaAI:

    ```bash
    cd Nova-App/ArcadiaAI
    ```

3.  **Installa le Dipendenze:**
    Una volta nella directory del progetto, installa tutte le dipendenze necessarie:

    ```bash
    npm install
    ```

### Gestione delle API Key

**Attenzione:** Le API key per i modelli principali (come Google Gemini o quelli gestiti tramite Openrouter) **non sono incluse** nel repository per motivi di sicurezza e sostenibilità.

**Dovrai ottenere e configurare le tue API key personali** dai rispettivi provider (es. Google AI Studio per Gemini, Openrouter per DeepSeek R1, ecc.).

Ti consigliamo di creare un file `.env` nella directory principale del progetto per gestire le tue API key in modo sicuro. Ecco un esempio di come potrebbe apparire il tuo file `.env`:
