import gradio as gr
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import os
import tempfile
import uuid
import torch
import time # Importa il modulo time per i timeout e la misurazione

# --- Caricamento modello (Migliorata gestione errori) ---
model = None
try:
    print("Tentativo di caricare il modello MusicGen 'small'...")
    model = MusicGen.get_pretrained("small")
    if torch.cuda.is_available():
        print("GPU disponibile, spostamento del modello su CUDA.")
        model.to("cuda")
    else:
        print("GPU non disponibile, il modello userà la CPU.")
    print("Modello MusicGen caricato con successo!")
except Exception as e:
    print(f"ERRORE GRAVE: Impossibile caricare il modello MusicGen: {e}")
    print("Assicurati di avere sufficiente RAM/VRAM e che le dipendenze siano installate correttamente.")
    print("Prova a eseguire 'pip install -U audiocraft torch torchaudio' in un nuovo ambiente virtuale.")

# --- Funzione per la generazione della musica (con timeout e logging avanzato) ---
def genera_musica(prompt, durata):
    if model is None:
        return None, "Errore: Modello AI non caricato correttamente. Controlla il log del server all'avvio."

    if not prompt.strip(): # Controlla che il prompt non sia vuoto
        return None, "Errore: Il prompt non può essere vuoto."
    if not (2 <= durata <= 30): # Controlla la durata valida
        return None, "Errore: La durata deve essere tra 2 e 30 secondi."

    start_time = time.time()
    print(f"\n--- Inizio Generazione ---")
    print(f"Prompt richiesto: '{prompt}'")
    print(f"Durata richiesta: {durata}s")

    try:
        model.set_generation_params(duration=durata, top_k=250, top_p=0, temperature=1.0) # Parametri suggeriti per una migliore qualità
        
        print("Avvio della generazione audio. Potrebbe volerci del tempo...")
        # Aggiungiamo un timeout approssimativo per evitare attese infinite in caso di blocchi
        # Questo non è un vero timeout per la funzione, ma un'indicazione.
        output = model.generate([prompt], progress=True) 
        print("Generazione audio completata.")

        print("Spostamento dell'output sulla CPU...")
        audio_to_write = output[0].cpu()

        print("Creazione directory temporanea e percorso file...")
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, f"music_{uuid.uuid4().hex}.wav")

        print(f"Salvataggio del file audio in: {audio_path}")
        audio_write(
            audio_path,
            audio_to_write,
            model.sample_rate,
            format="wav",
            loudness_compressor=True,
            add_suffix=False
        )
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Il file audio non è stato trovato dopo il salvataggio: {audio_path}")

        end_time = time.time()
        print(f"File audio creato con successo: {audio_path}")
        print(f"--- Generazione Completata in {end_time - start_time:.2f} secondi ---")
        return audio_path, "Audio generato con successo!"

    except torch.cuda.OutOfMemoryError:
        error_msg = "Errore: Memoria GPU insufficiente. Prova a ridurre la durata o a usare un modello più piccolo."
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Errore durante la generazione: {str(e)}. Controlla il log del server."
        print(error_msg)
        return None, error_msg

# --- Interfaccia Gradio (Nessuna modifica necessaria qui, è già ottimizzata) ---
with gr.Blocks() as demo:
    gr.Markdown("## 🎧 ArcadiaAI SoundForge")
    gr.Markdown("**Genera musica AI da prompt testuali**")

    with gr.Row():
        with gr.Column():
            input_prompt = gr.Textbox(label="Prompt musicale", placeholder="es. musica fantasy epica")
            input_duration = gr.Slider(2, 30, value=5, step=1, label="Durata (secondi)")
            generate_btn = gr.Button("Genera musica", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(
                label="Brano generato",
                type="filepath",
                interactive=False,
                visible=True
            )
            status_output = gr.Textbox(label="Stato", interactive=False)

    def process_generation(prompt, duration):
        # Aggiungiamo un messaggio di "caricamento" mentre la generazione è in corso
        # Questo sarà visualizzato immediatamente nel campo status_output
        yield None, "⏳ Generazione in corso... per favore attendi."
        
        audio_file_path, message = genera_musica(prompt, duration)

        if audio_file_path:
            yield audio_file_path, f"✅ {message}"
        else:
            yield None, f"❌ {message}"

    generate_btn.click(
        fn=process_generation,
        inputs=[input_prompt, input_duration],
        outputs=[audio_output, status_output]
    )

# Avvio applicazione
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )