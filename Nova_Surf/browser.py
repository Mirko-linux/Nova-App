import os
import json
import requests
import webbrowser
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QAction, QLineEdit,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDialog, QPushButton,
    QMessageBox, QMenuBar, QInputDialog, QSizePolicy
)
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTabBar
from PyQt5.QtWidgets import QListWidget, QTextEdit, QFileDialog
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setWindowTitle("Nova Surf")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurazione iniziale
        self.search_engine = "DuckDuckGo"
        self.theme = "light"
        self.arcadia_enabled = True
        self.adblock_enabled = True
        self.cookies_policy = "persistente"
        
        self.search_engines = {
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "Yahoo": "https://search.yahoo.com/search?p=",
            "Ecosia": "https://www.ecosia.org/search?q=",
            "Qwant": "https://www.qwant.com/?q="
        }
        
        self.init_ui()
        self.new_tab()
    
    def init_ui(self):
        # Configurazione della barra dei menu
        self.setup_menu_bar()
        
        # Barra degli strumenti principale
        self.setup_main_toolbar()
        
        # Barra delle estensioni
        self.setup_extensions_toolbar()
        
        # Configurazione delle schede
        self.setup_tabs()
        
        # Widget centrale
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Aggiungi le barre degli strumenti al layout
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
        
        # Menu File
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
        
        # Menu Visualizza
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
        
        # Menu Preferenze
        pref_menu = menu_bar.addMenu("Preferenze")
        
        settings_action = QAction(QIcon.fromTheme("preferences-system"), "Impostazioni", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        pref_menu.addAction(settings_action)
        
        # Menu Aiuto
        help_menu = menu_bar.addMenu("Aiuto")
        
        about_action = QAction(QIcon.fromTheme("help-about"), "Informazioni su Nova Surf", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
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
        
        # Pulsanti di navigazione
        back_btn = QAction(QIcon.fromTheme("go-previous"), "Indietro", self)
        back_btn.triggered.connect(self.navigate_back)
        self.main_toolbar.addAction(back_btn)
        
        forward_btn = QAction(QIcon.fromTheme("go-next"), "Avanti", self)
        forward_btn.triggered.connect(self.navigate_forward)
        self.main_toolbar.addAction(forward_btn)
        
        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Ricarica", self)
        reload_btn.triggered.connect(self.reload_page)
        self.main_toolbar.addAction(reload_btn)
        
        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.triggered.connect(self.load_home)
        self.main_toolbar.addAction(home_btn)
        
        # Barra degli indirizzi
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
        
        # Pulsante menu account
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
        """)
        
        # Pulsanti estensione di esempio
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
    
    def new_tab(self, url=None):
        # Rimuovi temporaneamente il tab "+" se esiste
        if self.tabs.count() > 0 and self.tabs.tabText(self.tabs.count() - 1) == "+":
            self.tabs.removeTab(self.tabs.count() - 1)

        browser = QWebEngineView()
        browser.setUrl(QUrl(url) if url else QUrl("about:blank"))
        
        index = self.tabs.addTab(browser, "Nuova scheda")
        self.tabs.setCurrentIndex(index)
        
        # Pulsante di chiusura personalizzato
        close_btn = QPushButton("×")
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0px;
                font-size: 14px;
                color: #777;
                min-width: 16px;
                max-width: 16px;
            }
            QPushButton:hover {
                color: #333;
                background-color: #e0e0e0;
                border-radius: 8px;
            }
        """)
        close_btn.clicked.connect(self.make_close_tab_handler(close_btn))
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, close_btn)
        
        # Aggiungi di nuovo il tab "+" alla fine
        plus_tab = QWidget()
        plus_index = self.tabs.addTab(plus_tab, "+")
        self.tabs.tabBar().setTabButton(plus_index, QTabBar.RightSide, None)
        self.tabs.tabBar().setTabText(plus_index, "+")
        
        # Connetti il segnale urlChanged per aggiornare la barra degli indirizzi
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        
        return browser
    
    def make_close_tab_handler(self, button):
        def handler():
            for i in range(self.tabs.count()):
                if self.tabs.tabBar().tabButton(i, QTabBar.RightSide) == button:
                    self.close_tab(i)
                    break
        return handler
    
    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == "+":
            self.new_tab()
        elif index >= 0:
            current_browser = self.tabs.widget(index)
            if current_browser:
                self.update_urlbar(current_browser.url(), current_browser)
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
    
    def update_urlbar(self, qurl, browser=None):
        if browser != self.tabs.currentWidget():
            return
        
        if qurl.toString() == "about:blank":
            self.address_bar.setText("")
        else:
            self.address_bar.setText(qurl.toString())
            self.address_bar.setCursorPosition(0)
    
    def navigate_to_url(self):
        url = self.address_bar.text()
        if not url:
            return
            
        if not url.startswith(("http://", "https://", "file://")):
            url = self.search_engines[self.search_engine] + url
            
        self.tabs.currentWidget().setUrl(QUrl(url))
    
    def navigate_back(self):
        self.tabs.currentWidget().back()
    
    def navigate_forward(self):
        self.tabs.currentWidget().forward()
    
    def reload_page(self):
        self.tabs.currentWidget().reload()
    
    def zoom_in(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() + 0.1)
    
    def zoom_out(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() - 0.1)
    
    def reset_zoom(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setZoomFactor(1.0)
    
    def load_home(self, browser=None):
        if browser is None or not isinstance(browser, QWebEngineView):
            self.new_tab()
            browser = self.tabs.currentWidget()

        search_url = self.search_engines[self.search_engine]
        news_content = self.fetch_news()

        home_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
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
                <img src="https://via.placeholder.com/120" class="logo" alt="Nova Surf">
                <div class="search-box">
                    <input class="search-input" type="text" placeholder="Cerca con {self.search_engine}..." 
                           id="searchBar" onkeydown="search(event)">
                </div>
                
                <div class="quick-links">
                    <a href="https://mail.google.com" class="quick-link" target="_blank">
                        <img src="https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_32dp.png" alt="Gmail">
                        <div>Gmail</div>
                    </a>
                    <a href="https://youtube.com" class="quick-link" target="_blank">
                        <img src="https://www.gstatic.com/youtube/img/branding/youtubelogo/svg/youtubelogo.svg" alt="YouTube" style="width:32px;height:32px;">
                        <div>YouTube</div>
                    </a>
                    <a href="https://maps.google.com" class="quick-link" target="_blank">
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
        browser.setHtml(home_html)
        self.tabs.setTabText(self.tabs.currentIndex(), "Nova Surf")
    
    def fetch_news(self):
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
                return "<p>Errore nel caricamento delle notizie.</p>"
        except Exception as e:
            return f"<p>Errore: {e}</p>"
    
    def open_arcadia_ai(self):
        url = "https://arcadiaai.onrender.com/"
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        index = self.tabs.addTab(browser, "ArcadiaAI")
        self.tabs.setCurrentIndex(index)
    
    def open_account_popup(self):
        if self.current_user:
            self.user_menu = UserMenuDialog(self, self.current_user)
            self.user_menu.exec_()
        else:
            self.account_dialog = AccountDialog(self)
            self.account_dialog.login_successful.connect(self.set_current_user)
            self.account_dialog.exec_()
    
    def set_current_user(self, email):
        self.current_user = email
    
    def open_settings(self):
        dialog = SettingsWindow(self)
        dialog.search_engine_combo.setCurrentText(self.search_engine)
        dialog.theme_combo.setCurrentText("Scuro" if self.theme == "dark" else "Chiaro")
        dialog.arcadia_checkbox.setChecked(self.arcadia_enabled)
        dialog.adblock_checkbox.setChecked(self.adblock_enabled)
        dialog.cookie_combo.setCurrentText(self.cookies_policy.capitalize())
        dialog.settings_applied.connect(self.apply_settings)
        dialog.exec_()
    
    def apply_settings(self, search_engine, theme, arcadia, adblock, cookies):
        self.search_engine = search_engine
        self.theme = theme.lower()
        self.arcadia_enabled = arcadia
        self.adblock_enabled = adblock
        self.cookies_policy = cookies.lower()
        
        # Applica il tema
        self.apply_theme()
        
        QMessageBox.information(self, "Impostazioni", "Impostazioni applicate correttamente.")
    
    def apply_theme(self):
        if self.theme == "dark":
            # Imposta il tema scuro
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            QApplication.setPalette(dark_palette)
            
            # Aggiorna gli stili
            self.main_toolbar.setStyleSheet("""
                QToolBar {
                    background-color: #333;
                    border-bottom: 1px solid #444;
                    padding: 2px;
                }
                QToolButton {
                    padding: 4px;
                    border-radius: 4px;
                    color: white;
                }
                QToolButton:hover {
                    background-color: #555;
                }
                QToolButton:pressed {
                    background-color: #666;
                }
            """)
            
            self.address_bar.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #444;
                    border-radius: 15px;
                    padding: 5px 15px;
                    font-size: 14px;
                    min-width: 400px;
                    background: #252525;
                    color: white;
                    selection-background-color: #4d90fe;
                }
                QLineEdit:focus {
                    border: 1px solid #4d90fe;
                    background: #252525;
                }
            """)
        else:
            # Ripristina il tema chiaro
            QApplication.setPalette(QApplication.style().standardPalette())
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
    
    def show_about(self):
        QMessageBox.about(self, "Informazioni su Nova Surf",
                         "<b>Nova Surf</b><br>"
                         "Versione 1.7.0<br><br>"
                         "Un browser moderno e veloce basato su PyQt5 e QtWebEngine.<br><br>"
                         "GNU GPL v3.0, Mirko Yuri Donato")
    
    def nuova_finestra(self):
        nuova_finestra = Browser()
        nuova_finestra.show()
class GestoreEstensioni(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestore Estensioni")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.estensioni_list = QListWidget()
        layout.addWidget(QLabel("Estensioni caricate:"))
        layout.addWidget(self.estensioni_list)

        self.carica_button = QPushButton("Carica estensione (.nsk)")
        self.carica_button.clicked.connect(self.carica_estensione)
        layout.addWidget(self.carica_button)

        self.info_box = QLabel("")
        self.info_box.setWordWrap(True)
        layout.addWidget(self.info_box)

        self.setLayout(layout)

        self.percorso_estensioni = "estensioni"
        self.aggiorna_lista()

    def carica_estensione(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona estensione", "", "Estensioni NSK (*.nsk)"
        )

        if file_path:
            nome_estensione = os.path.splitext(os.path.basename(file_path))[0]
            est_dir = os.path.join(self.percorso_estensioni, nome_estensione)

            if not os.path.exists(est_dir):
                os.makedirs(est_dir)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    target_path = os.path.join(est_dir, member)

                    if member.endswith('/'):
                        os.makedirs(target_path, exist_ok=True)
                        continue

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        target.write(source.read())

            self.aggiorna_lista()

            # 🔁 AGGIORNA il menu del gestore se esiste
            if hasattr(self.parent(), "aggiungi_estensione_menu"):
                self.parent().aggiungi_estensione_menu(nome_estensione)

    def aggiorna_lista(self):
        self.estensioni_list.clear()

        if os.path.exists(self.percorso_estensioni):
            for nome in os.listdir(self.percorso_estensioni):
                percorso_completo = os.path.join(self.percorso_estensioni, nome)
                if os.path.isdir(percorso_completo):  # solo cartelle
                    self.estensioni_list.addItem(nome)

        self.estensioni_list.itemClicked.connect(self.mostra_info)

    def mostra_info(self, item):
        nome_estensione = item.text()
        info_path = os.path.join(self.percorso_estensioni, nome_estensione, "manifest.json")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                dati = json.load(f)
                descrizione = dati.get("description", "Nessuna descrizione disponibile.")
                self.info_box.setText(f"Nome: {nome_estensione}\n\nDescrizione:\n{descrizione}")
        else:
            self.info_box.setText("Nessun manifest.json trovato.")

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setGeometry(400, 200, 300, 300)

        layout = QVBoxLayout()

        # Motore di ricerca
        layout.addWidget(QLabel("Motore di Ricerca:"))
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems([
            "DuckDuckGo", "Google", "Bing", "Yahoo", "Ecosia", "Qwatu"
        ])
        layout.addWidget(self.search_engine_combo)

        # Tema
        layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Chiaro", "Scuro"])
        layout.addWidget(self.theme_combo)

        # Estensione Arcadia
        self.arcadia_checkbox = QPushButton("🧠 Attiva Arcadia")
        self.arcadia_checkbox.setCheckable(True)
        layout.addWidget(self.arcadia_checkbox)

        # Adblock
        self.adblock_checkbox = QPushButton("🚫 Attiva Adblock")
        self.adblock_checkbox.setCheckable(True)
        layout.addWidget(self.adblock_checkbox)

        # Gestione Cookie
        layout.addWidget(QLabel("Politica Cookie:"))
        self.cookie_combo = QComboBox()
        self.cookie_combo.addItems(["Persistente", "Sessione", "Blocca"])
        layout.addWidget(self.cookie_combo)

        # Pulsante Salva
        salva_button = QPushButton("💾 Applica")
        salva_button.clicked.connect(self.apply_settings)
        layout.addWidget(salva_button)

        self.setLayout(layout)

    def apply_settings(self):
        search_engine = self.search_engine_combo.currentText()
        theme = self.theme_combo.currentText().lower()
        arcadia_enabled = self.arcadia_checkbox.isChecked()
        adblock_enabled = self.adblock_checkbox.isChecked()
        cookies_policy = self.cookie_combo.currentText().lower()

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
    window = Browser()
    window.show()
    app.exec_()

