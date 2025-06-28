from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import os
import uuid
# import shutil # Rimossa l'importazione di shutil perché non utilizzata
import time

app = FastAPI()

# --- CONFIGURAZIONE CORS ---
# Inserisci qui l'URL esatto del tuo frontend ArcadiaAI su Render
# Assicurati che sia https://arcadiaai.onrender.com
origins = [
    "http://localhost:8000",  # Per i test in locale (comune)
    "http://192.168.178.52:10000", # <--- NUOVO: Indirizzo IP locale per i tuoi test
    "https://arcadiaai.onrender.com", # L'URL del tuo chatbot ArcadiaAI deployato
    # Puoi aggiungere altre origini se necessario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- FINE CONFIGURAZIONE CORS ---


# Cartella per gli ZIP temporanei
# Render riavvia periodicamente i servizi gratuiti, quindi questa cartella
# verrà ricreata ad ogni riavvio, pulendo automaticamente i vecchi ZIP.
ZIP_FOLDER = "temp_zips"
os.makedirs(ZIP_FOLDER, exist_ok=True)

# La funzione clean_old_files() è utile, ma in un ambiente serverless/free tier
# dove i servizi vanno in sleep/si riavviano, la pulizia dei file temporanei
# è gestita automaticamente dal ciclo di vita del container.
# La lasciamo comunque, ma il suo impatto potrebbe essere limitato.
def clean_old_files():
    now = time.time()
    for filename in os.listdir(ZIP_FOLDER):
        file_path = os.path.join(ZIP_FOLDER, filename)
        # 86400 secondi = 24 ore
        if os.path.exists(file_path) and os.path.getmtime(file_path) < now - 86400:
            try:
                os.remove(file_path)
                print(f"Pulito file vecchio: {filename}")
            except Exception as e:
                print(f"Errore nella pulizia del file {filename}: {e}")


@app.post("/create-zip/")
async def create_zip(files: list[UploadFile] = File(...)):
    # Esegui la pulizia all'inizio di ogni richiesta di creazione ZIP
    # per mantenere la directory pulita.
    clean_old_files()
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Errore: Troppi file (massimo 10 supportati).")
    
    zip_id = str(uuid.uuid4())
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip")

    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in files:
                # Salta i file troppo grandi per evitare problemi di memoria o timeout
                if file.size > 5 * 1024 * 1024:  # Limite di 5MB per singolo file
                    print(f"Avviso: File '{file.filename}' ignorato perché supera i 5MB.")
                    continue
                contents = await file.read()
                zipf.writestr(file.filename, contents)
        
        # Restituisce l'URL relativo per il download del file ZIP
        return {"download_url": f"/download-zip/{zip_id}"}
    except Exception as e:
        print(f"Errore critico durante la creazione ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Si è verificato un errore interno durante la creazione del file ZIP: {str(e)}")

@app.get("/download-zip/{zip_id}")
async def download_zip(zip_id: str):
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip")
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Errore: File ZIP non trovato o il link è scaduto.")
    
    # Assicurati che il percorso del file sia all'interno della cartella ZIP_FOLDER
    # per prevenire attacchi di path traversal.
    if not os.path.abspath(zip_path).startswith(os.path.abspath(ZIP_FOLDER)):
        raise HTTPException(status_code=400, detail="Errore: Percorso file non valido.")

    # Il nome del file per il download sarà "archive.zip"
    return FileResponse(path=zip_path, filename="archive.zip", media_type="application/zip")

# --- ENDPOINT DI BENVENUTO (FONDAMENTALE per verificare che il servizio sia attivo) ---
@app.get("/")
async def root():
    return {"message": "Servizio di creazione e download ZIP attivo!"}
