from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import os
import uuid
import shutil
import time

app = FastAPI()

# Configura CORS per permettere richieste dal tuo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cartella per gli ZIP temporanei
ZIP_FOLDER = "temp_zips"
os.makedirs(ZIP_FOLDER, exist_ok=True)

# Pulisci vecchi file ogni 24 ore
def clean_old_files():
    now = time.time()
    for filename in os.listdir(ZIP_FOLDER):
        file_path = os.path.join(ZIP_FOLDER, filename)
        if os.path.getmtime(file_path) < now - 86400:  # 24 ore
            os.remove(file_path)

@app.post("/create-zip/")
async def create_zip(files: list[UploadFile] = File(...)):
    clean_old_files()
    
    if len(files) > 10:
        raise HTTPException(400, "Troppi file (max 10)")
    
    zip_id = str(uuid.uuid4())
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip")

    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in files:
                if file.size > 5 * 1024 * 1024:  # 5MB max
                    continue
                contents = await file.read()
                zipf.writestr(file.filename, contents)
        
        return {"download_url": f"/download-zip/{zip_id}"}
    except Exception as e:
        raise HTTPException(500, f"Errore creazione ZIP: {str(e)}")

@app.get("/download-zip/{zip_id}")
async def download_zip(zip_id: str):
    zip_path = os.path.join(ZIP_FOLDER, f"{zip_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(404, "File non trovato")
    return FileResponse(zip_path, filename="archive.zip")

# Monta la cartella degli ZIP come statica
app.mount("/temp_zips", StaticFiles(directory=ZIP_FOLDER), name="temp_zips")
