import sys
import os
import json
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox, QCheckBox, QInputDialog, QLineEdit
)

VAULT_PATH = "dati/vault.json"

BANNED_PASSWORDS = {"123456", "password", "000000", "abcdef", "123123", "qwerty"}

def is_password_strong(password):
    return (
        6 <= len(password) <= 12
        and password not in BANNED_PASSWORDS
        and not password.isdigit()
    )

def derive_key(master_password: str) -> bytes:
    hashed = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

class NovaVault:
    def __init__(self, fernet: Fernet):
        self.fernet = fernet
        os.makedirs("dati", exist_ok=True)
        if not os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, "w") as f:
                json.dump({"cookies": {}, "passwords": {}}, f)
        with open(VAULT_PATH, "r") as f:
            self.dati = json.load(f)

    def salva(self):
        with open(VAULT_PATH, "w") as f:
            json.dump(self.dati, f, indent=4)

    def salva_password(self, dominio, password):
        if not is_password_strong(password):
            raise ValueError("Password troppo debole.")
        encrypted = self.fernet.encrypt(password.encode()).decode()
        self.dati["passwords"][dominio] = encrypted
        self.salva()

    def elimina_dato(self, categoria, chiave):
        if chiave in self.dati.get(categoria, {}):
            del self.dati[categoria][chiave]
            self.salva()

    def get_password(self, dominio):
        encrypted = self.dati["passwords"].get(dominio)
        if encrypted:
            try:
                return self.fernet.decrypt(encrypted.encode()).decode()
            except InvalidToken:
                return "[Password corrotta o master password errata]"
        return None

class NovaVaultUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione NovaVault")
        self.setFixedSize(450, 400)

        password, ok = QInputDialog.getText(
            self, "Master Password", "Inserisci la tua master password:", QLineEdit.Password)
        if not ok or not password:
            sys.exit()

        key = derive_key(password)
        self.vault = NovaVault(Fernet(key))

        layout = QVBoxLayout(self)

        self.lista_passwords = QListWidget()
        layout.addWidget(QLabel("Password salvate:"))
        layout.addWidget(self.lista_passwords)

        self.btn_elimina = QPushButton("Elimina password selezionata")
        self.btn_elimina.clicked.connect(self.elimina_password)
        layout.addWidget(self.btn_elimina)

        self.chk_cookie = QCheckBox("Salva automaticamente i cookie")
        self.chk_cookie.setChecked(True)
        layout.addWidget(self.chk_cookie)

        self.carica_passwords()

    def carica_passwords(self):
        self.lista_passwords.clear()
        for dominio in self.vault.dati.get("passwords", {}):
            self.lista_passwords.addItem(dominio)

    def elimina_password(self):
        item = self.lista_passwords.currentItem()
        if item:
            dominio = item.text()
            self.vault.elimina_dato("passwords", dominio)
            self.carica_passwords()
            QMessageBox.information(self, "Eliminato", f"Password per {dominio} eliminata.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    finestra = NovaVaultUI()
    finestra.show()
    sys.exit(app.exec_())
