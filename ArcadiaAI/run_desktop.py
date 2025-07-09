import threading
import webview
from sr.app import app  # Importa l'app Flask dal modulo sr.app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    webview.create_window("ArcadiaAI", "http://127.0.0.1:5000", width=1100, height=700)
    webview.start()