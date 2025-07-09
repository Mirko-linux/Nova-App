from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import os
import uuid
# import shutil # Rimossa l'importazione di shutil perché non utilizzata
import time

app = FastAPI()

# Configura CORS per permettere richieste dal tuo frontend
# AGGIORNATO: Ora include l'URL esatto del tuo chatbot ArcadiaAI
origins = [
    "http://localhost:8000",  # Per i test in locale
    "https://arcadiaai.onrender.com", # <--- QUESTO È L'URL CORRETTO DEL TUO CHATBOT
    # Aggiungi altri domini se necessario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cartella per gli ZIP temporanei
ZIP_FOLDER = "temp_zips"
os.makedirs(ZIP_FOLDER, exist_ok=True)

# Pulisci vecchi file (esegue una volta per ogni richiesta)
def clean_old_files():
    now = time.time()
    # Scorre tutti i file nella cartella ZIP_FOLDER
    for filename in os.listdir(ZIP_FOLDER):
        file_path = os.path.join(ZIP_FOLDER, filename)
        # Controlla se il file esiste e se è più vecchio di 24 ore (86400 secondi)
        if os.path.exists(file_path) and os.path.getmtime(file_path) < now - 86400:
            try:
                os.remove(file_path) # Rimuove il file
                print(f"Pulito file vecchio: {filename}")
            except Exception as e:
                print(f"Errore nella pulizia del file {filename}: {e}")

@app.post("/create-zip/")
async def create_zip(files: list[UploadFile] = File(...)):
    # Pulisce i file vecchi ogni volta che viene chiamato l'endpoint per assicurare spazio
    clean_old_files()
    
    # Controlla il numero di file
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Troppi file (max 10).")
    
    zip_id = str(uuid.uuid4()) # Genera un ID univoco per il file ZIP
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip") # Costruisce il percorso del file ZIP

    try:
        # Crea il file ZIP e scrive i contenuti dei file caricati
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in files:
                # Controlla la dimensione massima per ogni singolo file (5MB)
                if file.size > 5 * 1024 * 1024:
                    print(f"File {file.filename} ignorato: troppo grande (>5MB).")
                    continue # Salta questo file e passa al prossimo
                contents = await file.read() # Legge il contenuto del file caricato
                zipf.writestr(file.filename, contents) # Aggiunge il file allo ZIP
        
        # Restituisce l'URL per il download del file ZIP
        return {"download_url": f"/download-zip/{zip_id}"}
    except Exception as e:
        # Cattura qualsiasi errore durante la creazione dello ZIP e restituisce un errore HTTP
        print(f"Errore durante la creazione ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante la creazione del file ZIP: {str(e)}")

@app.get("/download-zip/{zip_id}")
async def download_zip(zip_id: str):
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip") # Costruisce il percorso del file ZIP
    
    # Controlla se il file ZIP esiste
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File ZIP non trovato o scaduto.")
        
    # Restituisce il file ZIP per il download
    return FileResponse(path=zip_path, filename="archive.zip", media_type="application/zip")

# Monta la cartella degli ZIP come statica (questo non è strettamente necessario per il download diretto,
# ma non causa problemi e può essere utile per altre logiche se volessi servire i file in modo diverso)
app.mount("/temp_zips", StaticFiles(directory=ZIP_FOLDER), name="temp_zips")
