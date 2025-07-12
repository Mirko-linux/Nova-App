import os
import json
import zipfile
import shutil
import sys
import importlib.util

from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QFileDialog, QMessageBox, QWidget, QLineEdit, QAction
)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon

# Import necessari per il browser, che non ci sono in questo script autonomo.
# Li commento per far funzionare questo file da solo.
# from PyQt5.QtWebEngineWidgets import QWebEngineView


class GestoreEstensioni(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestore Estensioni Nova Surf")
        self.setFixedSize(400, 450) # Ho aumentato un po' l'altezza

        self.main_layout = QVBoxLayout()

        self.estensioni_list_label = QLabel("Estensioni caricate:")
        self.main_layout.addWidget(self.estensioni_list_label)

        self.estensioni_list = QListWidget()
        self.main_layout.addWidget(self.estensioni_list)
        self.estensioni_list.itemClicked.connect(self.mostra_info)

        self.carica_button = QPushButton("Carica estensione (.nsk)")
        self.carica_button.clicked.connect(self.carica_estensione)
        self.main_layout.addWidget(self.carica_button)

        self.rimuovi_button = QPushButton("Rimuovi estensione selezionata")
        self.rimuovi_button.clicked.connect(self.rimuovi_estensione)
        self.rimuovi_button.setEnabled(False) # Disabilita inizialmente
        self.main_layout.addWidget(self.rimuovi_button)
        self.estensioni_list.itemSelectionChanged.connect(self._toggle_remove_button)


        self.info_box = QLabel("Seleziona un'estensione per visualizzarne i dettagli.")
        self.info_box.setWordWrap(True)
        self.info_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info_box.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 4px; background-color: #f9f9f9;")
        self.main_layout.addWidget(self.info_box)

        self.setLayout(self.main_layout)

        self.percorso_estensioni = "estensioni"
        if not os.path.exists(self.percorso_estensioni):
            os.makedirs(self.percorso_estensioni)

        self.aggiorna_lista()

    def _toggle_remove_button(self):
        """Abilita/Disabilita il pulsante Rimuovi in base alla selezione."""
        self.rimuovi_button.setEnabled(len(self.estensioni_list.selectedItems()) > 0)


    def carica_estensione(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona estensione", "", "Estensioni Nova Surf (*.nsk);;Archivi ZIP (*.zip);;Tutti i file (*)"
        )

        if not file_path:
            return

        nome_estensione = os.path.splitext(os.path.basename(file_path))[0]
        est_dir = os.path.join(self.percorso_estensioni, nome_estensione)

        if os.path.exists(est_dir):
            reply = QMessageBox.question(self, 'Estensione esistente',
                                         f"L'estensione '{nome_estensione}' esiste già. Vuoi sovrascriverla?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            else:
                try:
                    shutil.rmtree(est_dir)
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile rimuovere la vecchia versione dell'estensione: {e}")
                    return

        try:
            os.makedirs(est_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Errore Creazione Cartella", f"Impossibile creare la cartella per l'estensione: {e}")
            return

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(est_dir)
            
            QMessageBox.information(self, "Successo", f"Estensione '{nome_estensione}' caricata con successo!")
            
        except zipfile.BadZipFile:
            QMessageBox.critical(self, "Errore Archivio", "Il file selezionato non è un archivio NSK/ZIP valido. Assicurati che sia un file ZIP corretto.")
            if os.path.exists(est_dir) and not os.listdir(est_dir):
                os.rmdir(est_dir)
            return
        
        except Exception as e:
            QMessageBox.critical(self, "Errore Caricamento", f"Si è verificato un errore inatteso durante il caricamento: {e}")
            if os.path.exists(est_dir) and not os.listdir(est_dir):
                os.rmdir(est_dir)
            return

        self.aggiorna_lista()
        # Se il gestore è autonomo, non ha un "parent" con carica_estensioni_nel_menu
        # if hasattr(self.parent(), "carica_estensioni_nel_menu"):
        #     self.parent().carica_estensioni_nel_menu()
            
        self.info_box.setText("Seleziona un'estensione per visualizzarne i dettagli.")


    def rimuovi_estensione(self):
        selected_items = self.estensioni_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nessuna selezione", "Seleziona un'estensione da rimuovere.")
            return

        item = selected_items[0]
        nome_estensione = item.text()
        est_dir = os.path.join(self.percorso_estensioni, nome_estensione)

        reply = QMessageBox.question(self, 'Conferma Rimozione',
                                     f"Sei sicuro di voler rimuovere l'estensione '{nome_estensione}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            shutil.rmtree(est_dir)
            QMessageBox.information(self, "Successo", f"Estensione '{nome_estensione}' rimossa con successo!")
            self.aggiorna_lista()
            self.info_box.setText("Seleziona un'estensione per visualizzarne i dettagli.")
            # Se il gestore è autonomo, non notifica il parent
            # if hasattr(self.parent(), "carica_estensioni_nel_menu"):
            #     self.parent().carica_estensioni_nel_menu()
        except Exception as e:
            QMessageBox.critical(self, "Errore Rimozione", f"Impossibile rimuovere l'estensione: {e}")

    def aggiorna_lista(self):
        self.estensioni_list.clear()
        
        # Non disconnettere e riconnettere il segnale qui, lo facciamo una volta nell'__init__
        # try:
        #     self.estensioni_list.itemClicked.disconnect(self.mostra_info)
        # except TypeError:
        #     pass

        if os.path.exists(self.percorso_estensioni):
            for nome in sorted(os.listdir(self.percorso_estensioni)):
                percorso_completo = os.path.join(self.percorso_estensioni, nome)
                if os.path.isdir(percorso_completo):
                    self.estensioni_list.addItem(nome)

        # self.estensioni_list.itemClicked.connect(self.mostra_info) # Connesso già nell'init
        
        if self.estensioni_list.count() == 0:
            self.info_box.setText("Nessuna estensione installata. Clicca su 'Carica estensione' per aggiungerne una.")
        
        # Dopo l'aggiornamento della lista, disabilita il bottone di rimozione
        self.rimuovi_button.setEnabled(False)


    def mostra_info(self, item):
        nome_estensione = item.text()
        info_path = os.path.join(self.percorso_estensioni, nome_estensione, "manifest.json")
        
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    dati = json.load(f)
                    
                    versione = dati.get("version", "N/D")
                    autore = dati.get("author", "Sconosciuto")
                    descrizione = dati.get("description", "Nessuna descrizione disponibile.")
                    
                    self.info_box.setText(
                        f"<b>Nome:</b> {nome_estensione}<br>"
                        f"<b>Versione:</b> {versione}<br>"
                        f"<b>Autore:</b> {autore}<br><br>"
                        f"<b>Descrizione:</b><br>{descrizione}"
                    )
            except json.JSONDecodeError:
                self.info_box.setText("Errore: il file manifest.json non è un JSON valido per questa estensione.")
            except Exception as e:
                self.info_box.setText(f"Errore durante la lettura del manifest.json: {e}")
        else:
            self.info_box.setText("Nessun file 'manifest.json' trovato per questa estensione. Le informazioni non sono disponibili.")

    def carica_estensioni_nel_menu(self):
        """Carica le estensioni nel menu del browser."""
        # Questo metodo dovrebbe essere implementato nel parent per caricare le estensioni nel menu
        # Se il gestore è autonomo, non lo implementiamo qui
        pass
# Punto di ingresso per eseguire il gestore estensioni come applicazione autonoma
if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = GestoreEstensioni()
    manager.show()
    sys.exit(app.exec_())
