import os
import json
import requests
import webbrowser
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QAction, QLineEdit,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDialog, QPushButton,
    QMessageBox, QMenuBar, QInputDialog, QSizePolicy, QListWidget, QTextEdit, QFileDialog, QComboBox, QTabBar, QCheckBox
)
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette

import os
import json
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar, QLineEdit,
    QAction, QTabWidget, QApplication, QMessageBox, QTabBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests

# Assicurati che queste classi siano importate o definite nel tuo codice
# Se queste classi sono in file separati, devono essere importate qui.
# Esempio:
# from .account_dialog import AccountDialog
# from .user_menu_dialog import UserMenuDialog
# from .settings_window import SettingsWindow
# from .gestore_estensioni import GestoreEstensioni
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setWindowTitle("Nova Surf")
        self.setGeometry(100, 100, 1200, 800)

        self.search_engine = "Brave Search"
        self.theme = "light"
        self.arcadia_enabled = True
        self.adblock_enabled = True
        self.cookies_policy = "persistente"

        self.search_engines = {
            "Brave Search": "https://search.brave.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "Yahoo": "https://search.yahoo.com/search?p=",
            "Ecosia": "https://www.ecosia.org/search?q=",
            "Qwant": "https://www.qwant.com/?q="
        }

        self.load_saved_settings() # Chiamata per caricare le impostazioni all'avvio

        self.init_ui()
        self.load_home(self.tabs.currentWidget())

    def init_ui(self):
        self.setup_menu_bar()
        self.setup_main_toolbar()
        self.setup_extensions_toolbar()
        self.setup_tabs()

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.main_toolbar)
        main_layout.addWidget(self.extensions_toolbar)
        main_layout.addWidget(self.tabs)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f8f8;
                padding: 2px;
                border-bottom: 1px solid #e0e0e0;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
                color: #333;
            }
            QMenuBar::item:selected {
                background: #e0e0e0;
                border-radius: 4px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #e6f2ff;
                color: #1a73e8;
            }
            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 5px 0;
            }
        """)

        file_menu = menu_bar.addMenu("File")

        new_tab_action = QAction(QIcon.fromTheme("tab-new"), "Nuova scheda", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)

        new_window_action = QAction(QIcon.fromTheme("window-new"), "Nuova finestra", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.nuova_finestra)
        file_menu.addAction(new_window_action)

        file_menu.addSeparator()

        close_action = QAction(QIcon.fromTheme("window-close"), "Chiudi", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        view_menu = menu_bar.addMenu("Visualizza")

        zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Ingrandisci", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Riduci", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction(QIcon.fromTheme("zoom-original"), "Dimensione predefinita", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)

        pref_menu = menu_bar.addMenu("Preferenze")

        settings_action = QAction(QIcon.fromTheme("preferences-system"), "Impostazioni", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        pref_menu.addAction(settings_action)

        self.extensions_menu = menu_bar.addMenu("Estensioni")
        self.setup_extensions_menu()

        help_menu = menu_bar.addMenu("Aiuto")

        about_action = QAction(QIcon.fromTheme("help-about"), "Informazioni su Nova Surf", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_extensions_menu(self):
        extension_manager_action = QAction(QIcon("icons/extension_manager.png"), "🧩 Gestore Estensioni", self)
        extension_manager_action.triggered.connect(self.open_extension_manager)
        self.extensions_menu.addAction(extension_manager_action)

        self.extensions_menu.addSeparator()

        self.carica_estensioni_nel_menu()

    def open_extension_manager(self):
        if 'GestoreEstensioni' in globals() and isinstance(GestoreEstensioni, type):
            dialog = GestoreEstensioni(self)
            dialog.exec_()
        else:
            QMessageBox.critical(self, "Errore", "La classe 'GestoreEstensioni' non è stata trovata. Assicurati di averla importata correttamente.")

    def carica_estensioni_nel_menu(self):
        actions_to_remove = []
        for action in self.extensions_menu.actions():
            if action.text() != "🧩 Gestore Estensioni" and not action.isSeparator():
                actions_to_remove.append(action)

        for action in actions_to_remove:
            self.extensions_menu.removeAction(action)

        percorso_estensioni = "estensioni"
        if not os.path.exists(percorso_estensioni):
            os.makedirs(percorso_estensioni)
            return

        for nome_estensione in sorted(os.listdir(percorso_estensioni)):
            est_dir = os.path.join(percorso_estensioni, nome_estensione)
            manifest_path = os.path.join(est_dir, "manifest.json")

            if os.path.isdir(est_dir) and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest_data = json.load(f)

                    action_data = manifest_data.get("action")

                    action = QAction(QIcon("icons/extension_default.png"), nome_estensione, self)
                    action.setStatusTip(manifest_data.get("description", "Estensione Nova Surf"))

                    if action_data and isinstance(action_data, dict):
                        action_type = action_data.get("type")
                        action_value = action_data.get("value")

                        if action_type == "open_url" and action_value:
                            action.triggered.connect(lambda checked, url=action_value: self.new_tab(url=QUrl(url)))
                        elif action_type == "run_python_script" and action_value:
                            action.triggered.connect(lambda checked, ext_name=nome_estensione, script=action_value:
                                                     self.esegui_script_estensione(ext_name, script))
                        else:
                            action.triggered.connect(lambda: QMessageBox.information(self, "Estensione",
                                                                                     f"Hai cliccato sull'estensione: {nome_estensione}\n"
                                                                                     f"Nessuna azione definita o azione sconosciuta nel manifest."))
                    else:
                        action.triggered.connect(lambda: QMessageBox.information(self, "Estensione",
                                                                                f"Hai cliccato sull'estensione: {nome_estensione}\n"
                                                                                f"Nessuna sezione 'action' specificata nel manifest."))

                    self.extensions_menu.addAction(action)

                except json.JSONDecodeError:
                    print(f"Errore: manifest.json per {nome_estensione} non è JSON valido.")
                except Exception as e:
                    print(f"Errore caricamento estensione {nome_estensione}: {e}")

    def esegui_script_estensione(self, nome_estensione, script_file):
        script_path = os.path.join("estensioni", nome_estensione, script_file)

        if not os.path.exists(script_path):
            QMessageBox.warning(self, "Errore Estensione",
                                f"Lo script '{script_file}' non è stato trovato per l'estensione '{nome_estensione}'.")
            return

        try:
            import importlib.util
            module_name = f"extension_module_{nome_estensione.replace('-', '_').replace(' ', '_')}_{os.path.basename(script_file).replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)

            import sys
            sys.path.insert(0, os.path.dirname(script_path))

            spec.loader.exec_module(module)

            sys.path.pop(0)

            if hasattr(module, 'activate'):
                module.activate(self)
                QMessageBox.information(self, "Estensione Eseguita",
                                        f"Estensione '{nome_estensione}' attivata con successo.")
            else:
                QMessageBox.information(self, "Estensione Eseguita",
                                        f"Script '{script_file}' dell'estensione '{nome_estensione}' eseguito (nessuna funzione 'activate' trovata).")

        except Exception as e:
            QMessageBox.critical(self, "Errore Esecuzione Script",
                                 f"Errore durante l'esecuzione dello script dell'estensione '{nome_estensione}':\n{e}")
        except ModuleNotFoundError as e:
            QMessageBox.critical(self, "Errore Import Estensione",
                                 f"Dipendenza mancante per l'estensione '{nome_estensione}': {e}")


    def setup_main_toolbar(self):
        self.main_toolbar = QToolBar("Navigation")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.main_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #e0e0e0;
                padding: 2px;
            }
            QToolButton {
                padding: 4px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)

        back_btn = QAction(QIcon.fromTheme("go-previous"), "◁", self)
        back_btn.triggered.connect(self.navigate_back)
        self.main_toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon.fromTheme("go-next"), "▷", self)
        forward_btn.triggered.connect(self.navigate_forward)
        self.main_toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "🔄", self)
        reload_btn.triggered.connect(self.reload_page)
        self.main_toolbar.addAction(reload_btn)

        home_btn = QAction(QIcon.fromTheme("go-home"), "🏠 ", self)
        home_btn.triggered.connect(self.load_home)
        self.main_toolbar.addAction(home_btn)

        settings_btn = QAction(QIcon.fromTheme("preferences-system"), "⚙️", self)
        settings_btn.triggered.connect(self.open_settings)
        self.main_toolbar.addAction(settings_btn)

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 14px;
                min-width: 400px;
                background: white;
                selection-background-color: #b3d7ff;
            }
            QLineEdit:focus {
                border: 1px solid #4d90fe;
                background: white;
            }
        """)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.main_toolbar.addWidget(self.address_bar)

        account_btn = QAction(QIcon.fromTheme("avatar-default"), "Account", self)
        account_btn.triggered.connect(self.open_account_popup)
        self.main_toolbar.addAction(account_btn)

    def setup_extensions_toolbar(self):
        self.extensions_toolbar = QToolBar("Extensions")
        self.extensions_toolbar.setMovable(False)
        self.extensions_toolbar.setIconSize(QSize(24, 24))
        self.extensions_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f1f1f1;
                border-bottom: 1px solid #ddd;
                padding: 2px;
            }
            QToolButton {
                padding: 2px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)

        adblock_action = QAction(QIcon("icons/adblock.png"), "AdBlock", self)
        adblock_action.setCheckable(True)
        adblock_action.setChecked(True)
        self.extensions_toolbar.addAction(adblock_action)

        dark_mode_action = QAction(QIcon("icons/darkmode.png"), "Dark Mode", self)
        dark_mode_action.setCheckable(True)
        self.extensions_toolbar.addAction(dark_mode_action)

        arcadia_action = QAction(QIcon("icons/ai.png"), "Arcadia AI", self)
        arcadia_action.triggered.connect(self.open_arcadia_ai)
        self.extensions_toolbar.addAction(arcadia_action)

    def setup_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.new_tab(initial_load_home=True)

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                margin: 0;
                padding: 0;
            }
            QTabBar::tab {
                background: #f1f1f1;
                border: 1px solid #ccc;
                border-bottom: none;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #555;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4d90fe;
                color: #333;
            }
            QTabBar::tab:hover {
                background: #e6e6e6;
            }
            QTabBar::close-button {
                subcontrol-origin: padding;
                subcontrol-position: right;
                padding: 2px;
                margin-left: 4px;
            }
            QTabBar::close-button:hover {
                background: #e0e0e0;
                border-radius: 4px;
            }
        """)

    def new_tab(self, url=None, initial_load_home=False):
        browser = QWebEngineView()

        if url is not None:
            browser.setUrl(QUrl(url))

        index = self.tabs.addTab(browser, "Nuova scheda")
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.titleChanged.connect(lambda title, browser=browser, index=index: self.update_tab_title(title, browser, index))

        if initial_load_home:
            self.load_home(browser)
        elif url is None:
            self.load_home(browser)

        self.add_new_tab_button()
        return browser

    def add_new_tab_button(self):
        for i in reversed(range(self.tabs.count())):
            if self.tabs.tabText(i) == "+":
                self.tabs.removeTab(i)

        plus_button_tab = QWidget()
        plus_index = self.tabs.addTab(plus_button_tab, "+")
        self.tabs.tabBar().setTabButton(plus_index, QTabBar.RightSide, None)
        self.tabs.tabBar().setTabEnabled(plus_index, True)

    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == "+":
            self.new_tab()
        elif index >= 0:
            current_browser = self.tabs.widget(index)
            if current_browser and isinstance(current_browser, QWebEngineView):
                self.update_urlbar(current_browser.url(), current_browser)
            else:
                self.address_bar.setText("")

    def close_tab(self, index):
        if self.tabs.tabText(index) == "+":
            return

        if self.tabs.count() == 2:
            self.close()
        else:
            self.tabs.removeTab(index)
            self.add_new_tab_button()

    def update_urlbar(self, qurl, browser=None):
        if browser != self.tabs.currentWidget():
            return

        if qurl.toString() == "about:blank" or qurl.toString() == "about:home":
            self.address_bar.setText("")
        else:
            self.address_bar.setText(qurl.toString())
            self.address_bar.setCursorPosition(0)

    def update_tab_title(self, title, browser, index):
        if self.tabs.widget(index) == browser:
            if title:
                self.tabs.setTabText(index, title)
            else:
                self.tabs.setTabText(index, "Nuova scheda")

    def navigate_to_url(self):
        url = self.address_bar.text()
        if not url:
            return

        if not url.startswith(("http://", "https://", "file://")):
            url = self.search_engines[self.search_engine] + url

        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.setUrl(QUrl(url))
        else:
            self.new_tab(url=QUrl(url).toString())

    def navigate_back(self):
        if isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().back()

    def navigate_forward(self):
        if isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().forward()

    def reload_page(self):
        if isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().reload()

    def zoom_in(self):
        if self.tabs.currentWidget() and isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() + 0.1)

    def zoom_out(self):
        if self.tabs.currentWidget() and isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() - 0.1)

    def reset_zoom(self):
        if self.tabs.currentWidget() and isinstance(self.tabs.currentWidget(), QWebEngineView):
            self.tabs.currentWidget().setZoomFactor(1.0)

    def load_home(self, browser=None):
        if browser is None or not isinstance(browser, QWebEngineView):
            found_browser = None
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, QWebEngineView) and self.tabs.tabText(i) != "+":
                    found_browser = widget
                    self.tabs.setCurrentIndex(i)
                    break
            if found_browser:
                browser = found_browser
            else:
                browser = self.new_tab(initial_load_home=False)

        search_url = self.search_engines[self.search_engine]
        news_content = self.fetch_news()

        local_logo_path = "icons/nova_surf_logo.png"

        home_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nova Surf - Home</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 50px auto;
                    text-align: center;
                }}
                .logo {{
                    width: 120px;
                    height: 120px;
                    margin-bottom: 20px;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .search-box {{
                    width: 80%;
                    max-width: 600px;
                    margin: 0 auto 40px;
                    position: relative;
                }}
                .search-input {{
                    width: 100%;
                    padding: 12px 20px;
                    font-size: 16px;
                    border: 1px solid #ddd;
                    border-radius: 24px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    outline: none;
                }}
                .search-input:focus {{
                    border-color: #4d90fe;
                    box-shadow: 0 2px 6px rgba(66,133,244,0.3);
                }}
                .quick-links {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 15px;
                    margin-bottom: 40px;
                }}
                .quick-link {{
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    width: 120px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                    text-decoration: none;
                    color: #333;
                }}
                .quick-link:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .quick-link img {{
                    width: 32px;
                    height: 32px;
                    margin-bottom: 8px;
                }}
                .news-container {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 30px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    text-align: left;
                }}
                .news-title {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    color: #4d90fe;
                }}
                .news-item {{
                    margin-bottom: 10px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .news-item:last-child {{
                    border-bottom: none;
                }}
                .news-item a {{
                    text-decoration: none;
                    color: #1a73e8;
                    font-size: 14px;
                }}
                .news-item a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="{local_logo_path}" class="logo" alt="Nova Surf Logo">
                <div class="search-box">
                    <input class="search-input" type="text" placeholder="Cerca con {self.search_engine}..."
                                 id="searchBar" onkeydown="search(event)">
                </div>

                <div class="quick-links">
                    <a href="https://mail.google.com" class="quick-link" target="_blank">
                        <img src="https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_32dp.png" alt="Gmail">
                        <div>Gmail</div>
                    </a>
                    <a href="https://www.youtube.com/" class="quick-link" target="_blank">
                        <img src="https://www.gstatic.com/youtube/img/branding/youtubelogo/svg/youtubelogo.svg" alt="YouTube" style="width:32px;height:32px;">
                        <div>YouTube</div>
                    </a>
                    <a href="https://maps.google.com" target="_blank" class="quick-link">
                        <img src="https://www.gstatic.com/images/branding/product/1x/maps_2020q4_32dp.png" alt="Maps">
                        <div>Maps</div>
                    </a>
                    <a href="https://drive.google.com" class="quick-link" target="_blank">
                        <img src="https://www.gstatic.com/images/branding/product/1x/drive_2020q4_32dp.png" alt="Drive">
                        <div>Drive</div>
                    </a>
                </div>

                <div class="news-container">
                    <div class="news-title">Leonia+ Notizie</div>
                    {news_content}
                </div>
            </div>

            <script>
                function search(event) {{
                    if (event.key === "Enter") {{
                        var query = document.getElementById("searchBar").value;
                        window.location.href = "{search_url}" + query;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        base_url = QUrl.fromLocalFile(current_script_dir + os.sep)

        browser.setHtml(home_html, base_url)
        self.tabs.setTabText(self.tabs.indexOf(browser), "Nova Surf - Home")
        self.update_urlbar(QUrl("about:home"), browser)

    def fetch_news(self):
        # NOTA: Questa API Key è visibile nel tuo codice e non dovrebbe essere usata per applicazioni pubbliche/distribuite.
        # Per un uso reale, le API Keys andrebbero gestite in modo più sicuro (es. variabili d'ambiente).
        api_key = 'fc89b08052684126a744651190bfdafa'
        url = f"https://newsapi.org/v2/everything?q=italia&sortBy=publishedAt&language=it&apiKey={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                if not articles:
                    return "<p>Nessuna notizia trovata al momento.</p>"
                news_content = ""
                for article in articles[:5]:
                    news_content += f'<div class="news-item"><a href="{article["url"]}" target="_blank">{article["title"]}</a></div>'
                return news_content
            else:
                return f"<p>Errore nel caricamento delle notizie. Codice: {response.status_code}</p>"
        except requests.exceptions.RequestException as e:
            return f"<p>Errore di rete: {e}</p>"
        except json.JSONDecodeError:
            return "<p>Errore nella decodifica delle notizie (risposta non valida).</p>"
        except Exception as e:
            return f"<p>Si è verificato un errore inatteso durante il recupero delle notizie: {e}</p>"

    def open_arcadia_ai(self):
        url = "https://arcadiaai.onrender.com/"
        self.new_tab(url=url)

    def open_account_popup(self):
        if 'AccountDialog' in globals() and 'UserMenuDialog' in globals() and isinstance(AccountDialog, type) and isinstance(UserMenuDialog, type):
            if self.current_user:
                self.user_menu = UserMenuDialog(self, self.current_user)
                self.user_menu.exec_()
            else:
                self.account_dialog = AccountDialog(self)

    def nuova_finestra(self):
        new_browser_window = Browser()
        new_browser_window.show()

    def open_settings(self):
        if 'SettingsWindow' in globals() and isinstance(SettingsWindow, type):
            current_settings = {
                'search_engine': self.search_engine,
                'theme': self.theme,
                'arcadia_enabled': self.arcadia_enabled,
                'adblock_enabled': self.adblock_enabled,
                'cookies_policy': self.cookies_policy
            }
            settings_dialog = SettingsWindow(current_settings, self)
            
            # Questa è la riga che prima causava l'errore se il metodo non c'era
            settings_dialog.settings_applied.connect(self.update_browser_settings)
            
            settings_dialog.exec_()
        else:
            QMessageBox.critical(self, "Errore", "La classe 'SettingsWindow' non è stata trovata. Assicurati di averla importata correttamente.")

    # NUOVO METODO: Questo deve essere presente nella classe Browser
    def update_browser_settings(self, search_engine, theme, arcadia_enabled, adblock_enabled, cookies_policy):
        self.search_engine = search_engine
        self.theme = theme
        self.arcadia_enabled = arcadia_enabled
        self.adblock_enabled = adblock_enabled
        self.cookies_policy = cookies_policy

        QMessageBox.information(self, "Impostazioni", "Impostazioni applicate con successo!")
        self.load_home(self.tabs.currentWidget()) # Ricarica la home per applicare il nuovo motore di ricerca
        self.save_settings() # Salva le impostazioni aggiornate su disco

    # NUOVO METODO: Questo deve essere presente nella classe Browser
    def save_settings(self):
        settings_data = {
            'search_engine': self.search_engine,
            'theme': self.theme,
            'arcadia_enabled': self.arcadia_enabled,
            'adblock_enabled': self.adblock_enabled,
            'cookies_policy': self.cookies_policy
        }
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            print("Impostazioni salvate.")
        except Exception as e:
            QMessageBox.warning(self, "Errore di salvataggio", f"Impossibile salvare le impostazioni: {e}")

    # NUOVO METODO: Questo deve essere presente nella classe Browser
    def load_saved_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                self.search_engine = settings_data.get('search_engine', "Brave Search")
                self.theme = settings_data.get('theme', "light")
                self.arcadia_enabled = settings_data.get('arcadia_enabled', True)
                self.adblock_enabled = settings_data.get('adblock_enabled', True)
                self.cookies_policy = settings_data.get('cookies_policy', "persistente")
                print("Impostazioni caricate.")
            else:
                print("File delle impostazioni non trovato. Caricando impostazioni di default.")
                self.save_settings() # Salva le impostazioni di default se il file non esiste
        except Exception as e:
            QMessageBox.warning(self, "Errore di caricamento", f"Impossibile caricare le impostazioni: {e}")
            # Se c'è un errore nel caricamento, assicurati che i valori siano comunque quelli di default
            self.search_engine = "Brave Search"
            self.theme = "light"
            self.arcadia_enabled = True
            self.adblock_enabled = True
            self.cookies_policy = "persistente"

    def show_about(self):
        QMessageBox.about(self, "Informazioni su Nova Surf",
                          "Nova Surf è un browser web moderno e sicuro, sviluppato con PyQt5 e QtWebEngine.")

class GestoreEstensioni(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestore Estensioni")
        self.setFixedSize(400, 300)

        self.main_layout = QVBoxLayout()

        self.estensioni_list_label = QLabel("Estensioni caricate:")
        self.main_layout.addWidget(self.estensioni_list_label)

        self.estensioni_list = QListWidget()
        self.main_layout.addWidget(self.estensioni_list)

        self.carica_button = QPushButton("Carica estensione (.nsk)")
        self.carica_button.clicked.connect(self.carica_estensione)
        self.main_layout.addWidget(self.carica_button)

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

        if hasattr(self.parent(), "carica_estensioni_nel_menu"):
            self.parent().carica_estensioni_nel_menu()
            
        self.info_box.setText("Seleziona un'estensione per visualizzarne i dettagli.")

    def aggiorna_lista(self):
        self.estensioni_list.clear()
        
        try:
            self.estensioni_list.itemClicked.disconnect(self.mostra_info)
        except TypeError:
            pass

        if os.path.exists(self.percorso_estensioni):
            for nome in sorted(os.listdir(self.percorso_estensioni)):
                percorso_completo = os.path.join(self.percorso_estensioni, nome)
                if os.path.isdir(percorso_completo):
                    self.estensioni_list.addItem(nome)

        self.estensioni_list.itemClicked.connect(self.mostra_info)
        
        if self.estensioni_list.count() == 0:
            self.info_box.setText("Nessuna estensione installata. Clicca su 'Carica estensione' per aggiungerne una.")

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

class SettingsWindow(QDialog):
    settings_applied = pyqtSignal(str, str, bool, bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()

        # Motore di ricerca
        search_engine_layout = QHBoxLayout()
        search_engine_layout.addWidget(QLabel("Motore di ricerca predefinito:"))
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(list(parent.search_engines.keys()))
        search_engine_layout.addWidget(self.search_engine_combo)
        layout.addLayout(search_engine_layout)

        # Tema
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Chiaro", "Scuro"])
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Opzioni estensioni
        self.arcadia_checkbox = QCheckBox("Abilita Arcadia AI")
        self.adblock_checkbox = QCheckBox("Abilita AdBlock")
        layout.addWidget(self.arcadia_checkbox)
        layout.addWidget(self.adblock_checkbox)

        # Politica cookie
        cookie_layout = QHBoxLayout()
        cookie_layout.addWidget(QLabel("Politica dei cookie:"))
        self.cookie_combo = QComboBox()
        self.cookie_combo.addItems(["Persistente", "Sessione", "Blocca"])
        cookie_layout.addWidget(self.cookie_combo)
        layout.addLayout(cookie_layout)

        apply_button = QPushButton("Applica Impostazioni")
        apply_button.clicked.connect(self.apply)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def apply(self):
        search_engine = self.search_engine_combo.currentText()
        theme = self.theme_combo.currentText()
        arcadia_enabled = self.arcadia_checkbox.isChecked()
        adblock_enabled = self.adblock_checkbox.isChecked()
        cookies_policy = self.cookie_combo.currentText()
        
        self.settings_applied.emit(search_engine, theme, arcadia_enabled, adblock_enabled, cookies_policy)
        self.accept()

class AccountDialog(QDialog):
    login_successful = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accedi o Registrati")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        # Login tradizionale
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("🔐 Login")
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton("📝 Registrati")
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(QLabel("Login/Registrazione Tradizionale"))
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        layout.addSpacing(20)

        # Login social
        layout.addWidget(QLabel("Oppure accedi con:"))
        login_google = QPushButton("🔵 Google")
        login_google.clicked.connect(lambda: self.auth_via("google"))
        layout.addWidget(login_google)

        login_github = QPushButton("⚫ GitHub")
        login_github.clicked.connect(lambda: self.auth_via("github"))
        layout.addWidget(login_github)

        login_telegram = QPushButton("🔷 Telegram")
        login_telegram.clicked.connect(lambda: self.auth_via("telegram"))
        layout.addWidget(login_telegram)

        self.setLayout(layout)

    def auth_via(self, provider):
        url = None
        if provider == "google":
            client_id = "71811104449-mh42pcltigitvee6t89agpt2d1a91i8n.apps.googleusercontent.com"
            redirect_uri = "http://localhost:5000/callback"
            scope = "email profile"
            url = (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"response_type=code&"
                f"scope={scope.replace(' ', '%20')}"
            )
        elif provider == "github":
            client_id = " Ov23liWs0Ftttoe12qTi"
            redirect_uri = "http://localhost:8000/callback"
            url = (
                f"https://github.com/login/oauth/authorize?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope=read:user"
            )

        elif provider == "telegram":
            bot_id = "8045325288:"
            origin = "https://yourdomain.com"
            url = "https://oauth.telegram.org/auth?bot_id=8045325288:&origin=http://localhost:8000"

        else:
            QMessageBox.warning(self, "Errore", "Bot ID non configurato.")
            return

        if url:
            webbrowser.open(url)
            self.close()
        else:
            QMessageBox.warning(self, "Errore", f"Provider sconosciuto: {provider}")

    def handle_register(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Errore", "Inserisci email e password")
            return

        users = self.load_users()
        if email in users:
            QMessageBox.warning(self, "Errore", "Utente già registrato")
            return

        users[email] = password
        self.save_users(users)
        QMessageBox.information(self, "Registrazione", "Registrazione completata!")
        self.login_successful.emit(email)
        self.close()

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        users = self.load_users()
        if email in users and users[email] == password:
            QMessageBox.information(self, "Login", "Login effettuato con successo!")
            self.close()
            self.login_successful.emit(email)
            self.close()
        else:
            QMessageBox.warning(self, "Errore", "Credenziali non valide")

    def load_users(self):
        if not os.path.exists("users.json"):
            return {}
        with open("users.json", "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
class UserMenuDialog(QDialog):
    def __init__(self, parent=None, user_email="Utente"):
        super().__init__(parent)
        self.setWindowTitle("Menu Utente")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"🎉 Benvenuto, {user_email}"))

        nickname_button = QPushButton("✏️ Modifica Nickname")
        nickname_button.clicked.connect(self.edit_nickname)
        layout.addWidget(nickname_button)

        vault_button = QPushButton("🔐 NovaVault")
        vault_button.clicked.connect(self.open_vault)
        layout.addWidget(vault_button)

        logout_button = QPushButton("🚪 Logout")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.setLayout(layout)
    def zoom_in(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() + 0.1)

    def edit_nickname(self):
        nickname, ok = QInputDialog.getText(self, "Modifica Nickname", "Inserisci nuovo nickname:")
        if ok and nickname:
            QMessageBox.information(self, "Nickname", f"Nickname aggiornato: {nickname}")
            # Qui potresti salvarlo in un file JSON legato all’utente

    def open_vault(self):
        vault_dialog = NovaVaultDialog(self)
        vault_dialog.exec_()

    def logout(self):
        self.parent().current_user = None
        QMessageBox.information(self, "Logout", "Sei stato disconnesso.")
        self.close()

class SettingsWindow(QDialog):
    settings_applied = pyqtSignal(str, str, bool, bool, str)

    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setGeometry(400, 200, 350, 400)

        self.current_settings = current_settings

        layout = QVBoxLayout()
        layout.setSpacing(15)

        layout.addWidget(QLabel("<b>Motore di Ricerca:</b>"))
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems([
            "Brave Search", "DuckDuckGo", "Google", "Bing", "Yahoo", "Ecosia", "Qwant"
        ])
        layout.addWidget(self.search_engine_combo)

        layout.addWidget(QLabel("<b>Tema:</b>"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        layout.addWidget(self.theme_combo)

        self.arcadia_checkbox = QPushButton("🧠 Attiva Arcadia AI")
        self.arcadia_checkbox.setCheckable(True)
        self.arcadia_checkbox.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #e6f2ff;
                border-color: #4d90fe;
            }
        """)
        layout.addWidget(self.arcadia_checkbox)

        self.adblock_checkbox = QPushButton("🚫 Attiva Adblock")
        self.adblock_checkbox.setCheckable(True)
        self.adblock_checkbox.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #e6f2ff;
                border-color: #4d90fe;
            }
        """)
        layout.addWidget(self.adblock_checkbox)

        layout.addWidget(QLabel("<b>Politica Cookie:</b>"))
        self.cookie_combo = QComboBox()
        self.cookie_combo.addItems(["persistente", "sessione", "blocca"])
        layout.addWidget(self.cookie_combo)

        salva_button = QPushButton("💾 Applica Impostazioni")
        salva_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        salva_button.clicked.connect(self.apply_settings)
        layout.addWidget(salva_button)

        self.setLayout(layout)
        self.load_settings_into_ui()

    def load_settings_into_ui(self):
        index = self.search_engine_combo.findText(self.current_settings['search_engine'])
        if index != -1:
            self.search_engine_combo.setCurrentIndex(index)

        index = self.theme_combo.findText(self.current_settings['theme'])
        if index != -1:
            self.theme_combo.setCurrentIndex(index)

        self.arcadia_checkbox.setChecked(self.current_settings['arcadia_enabled'])
        self.adblock_checkbox.setChecked(self.current_settings['adblock_enabled'])

        index = self.cookie_combo.findText(self.current_settings['cookies_policy'])
        if index != -1:
            self.cookie_combo.setCurrentIndex(index)

    def apply_settings(self):
        search_engine = self.search_engine_combo.currentText()
        theme = self.theme_combo.currentText()
        arcadia_enabled = self.arcadia_checkbox.isChecked()
        adblock_enabled = self.adblock_checkbox.isChecked()
        cookies_policy = self.cookie_combo.currentText()

        self.settings_applied.emit(
            search_engine, theme, arcadia_enabled, adblock_enabled, cookies_policy
        )
        self.accept()

class NovaVaultDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 NovaVault")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.passwords_list = QListWidget()
        layout.addWidget(QLabel("Password salvate:"))
        layout.addWidget(self.passwords_list)

        add_btn = QPushButton("➕ Aggiungi")
        add_btn.clicked.connect(self.aggiungi_password)
        layout.addWidget(add_btn)

        self.setLayout(layout)
        self.vault_path = "vault.json"
        self.carica_passwords()

    def carica_passwords(self):
        self.passwords_list.clear()
        if os.path.exists(self.vault_path):
            with open(self.vault_path, 'r') as f:
                data = json.load(f)
                for sito, info in data.items():
                    self.passwords_list.addItem(f"{sito} ➜ {info['utente']} / {info['password']}")

    def aggiungi_password(self):
        sito, ok1 = QInputDialog.getText(self, "Nuovo sito", "Nome del sito:")
        if not ok1 or not sito:
            return
        utente, ok2 = QInputDialog.getText(self, "Utente", "Nome utente:")
        if not ok2 or not utente:
            return
        password, ok3 = QInputDialog.getText(self, "Password", "Password:")
        if not ok3 or not password:
            return

        data = {}
        if os.path.exists(self.vault_path):
            with open(self.vault_path, 'r') as f:
                data = json.load(f)
        data[sito] = {"utente": utente, "password": password}
        with open(self.vault_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.carica_passwords()

if __name__ == '__main__':
    app = QApplication([])
    # Imposta un'icona per l'applicazione (opzionale)
    # app.setWindowIcon(QIcon("icons/nova_surf_app_icon.png")) # Assicurati di avere anche questa icona

    browser_window = Browser()
    browser_window.show()
    app.exec_()
