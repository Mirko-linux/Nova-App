# CES Image

CES Image è un SAC (_Strumento avanzato di CES_) che permette ad ArcadiaAI di interagire in modo sicuro, controllato e ottimizzato con il motore di generazione immagini esterno Pollinations.ai.

> CES Image NON è un modello di generazione immagini, ma un middleware intelligente che media la comunicazione tra ArcadiaAI e il modello _Pollinations.ai_
>

## Funzionamento di CES Image
  <img src="docs/images/ces-image-flow.png" alt="Diagramma CES Flow" width="900"/>
CES Image segue una pipeline rigorosa:

1. **Parsing del JSON**
Estrazione del campo prompt.
Rimozione degli spazi iniziali/finali e validazionealta qualità, realistico

2. **Filtro NSFW avanzato**
    CES Image blocca automaticamente prompt con contenuti espliciti.
    Parole chiave bannate:
    nudo, nudità, porn, sessuale, sex, sesso, nsfw, xxx
    Tolleranza ai tentativi di bypass:
    Il sistema normalizza il testo (rimozione numeri, simboli, spazi) prima del controllo:
        "nud0" → "nudo"
        "s3x" → "sex"
        "n u d i t à" → "nudita"
   > "CES Image non garantisce che il filtri Image non garantisce al 100% l’assenza di contenuti indesiderati, ma riduce drasticamente il rischio grazie al filtro proattivo.

3. **Miglioramento del prompt (Enhancement)**
   Il prompt originale viene arricchito per massimizzare la qualità visiva:

```text 
Masterpiece, 8K, ultra-detailed, high resolution, sharp focus, cinematic lighting,
professional photography, vibrant colors, no blur, no noise, no distortion.
Subject: [prompt originale]
``` 
4. **Codifica sicura per URL**
   Il prompt viene poi codificato con urllib.parse.quote per evitare errori di trasmissione

5. **Costruzione dell’URL di generazione**
   Il prompt viene poi costruito usando flux, modello di Pollinations.ai che genera immagini di alta qualità

6. **Risposta al client**
   Restituisce il JSON con image_url, prompt originale e metadati
   
