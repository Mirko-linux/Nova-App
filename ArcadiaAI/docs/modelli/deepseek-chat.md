# DeepSeek Chat

**Origine:** DeepSeek AI  
**Accesso tramite:** [OpenRouter](https://openrouter.ai)  
**Licenza:** MIT  
**Usato da:** ArcadiaAI per interazioni linguistiche avanzate  
**Modalità:** R1 (default), V3 (fallback)

---

## Descrizione

DeepSeek Chat è una combinazione di due modelli AI avanzati — **R1** e **V3** — entrambi sviluppati da DeepSeek AI.  
ArcadiaAI integra DeepSeek Chat tramite le API di [OpenRouter](https://openrouter.ai), utilizzando **R1 come modello principale** e **V3 come modello di riserva** nel caso di errori, timeout o blocchi temporanei.

---

## DeepSeek R1

- **Architettura:** Large Language Model da 671B parametri (37B attivi)  
- **Funzione:** dialogo contestuale, ragionamento e comprensione semantica  
- **Contesto supportato:** fino a 32.000 token  
- **Licenza:** MIT  
- **Endpoint API:** `deepseek/deepseek-r1:free`

---

## DeepSeek V3

- **Architettura:** Mixture-of-Experts con 685B parametri  
- **Funzione:** generazione multi-turn, istruzioni complesse, contesti estesi  
- **Contesto supportato:** fino a 131.072 token  
- **Licenza:** MIT  
- **Endpoint API:** `deepseek/deepseek-chat-v3:free`

---

## Integrazione in ArcadiaAI

- **SDK compatibile:** OpenAI Python SDK  
- **Endpoint API:** `https://openrouter.ai/api/v1/chat/completions`  
- **Priorità logica:** R1 è il modello predefinito, V3 agisce come fallback intelligente  
- **Monitoraggio:** logging semantico e metrico su modello attivo  

DeepSeek Chat è **perfettamente integrato** in ArcadiaAI e supporta nativamente tutte le funzionalità previste dal chatbot in italiano, tra cui:

- **SAC** per svolgere compiti avanzati
- **Comandi Rapidi** per azioni immediate e interazione proattiva  
- Modalità colloquiale ottimizzata per utenti italiani  

La perfetta sinergia tra DeepSeek Chat e ArcadiaAI garantisce un’esperienza utente fluida, efficace e profondamente personalizzata.

---

## Note

- I modelli **non sono inclusi direttamente nel codice sorgente** di ArcadiaAI, ma sono **accessibili tramite API esterne**.  
