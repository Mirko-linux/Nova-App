/**
 * ArcadiaAI - Gestione Chat
 * Script principale per l'interfaccia chat
 */

// Stato applicazione
// Debug iniziale obbligatorio (inserisci in cima a script.js)
console.log("[INIT] Script caricato");
console.log("Elementi critici:", {
    chatbox: !!document.getElementById("chatbox"),
    input: !!document.getElementById("input"),
    sendBtn: !!document.getElementById("send-btn")
});

// --- Elemento per il messaggio di stato ---
const statusMessageElement = document.getElementById('status-message');

// Funzione per mostrare un messaggio di stato
function showStatus(message) {
    if (statusMessageElement) { // Assicurati che l'elemento esista
        statusMessageElement.textContent = message;
        statusMessageElement.style.display = 'block'; // Rendi visibile
    }
}

// Funzione per nascondere il messaggio di stato
function hideStatus() {
    if (statusMessageElement) { // Assicurati che l'elemento esista
        statusMessageElement.style.display = 'none'; // Nascondi
        statusMessageElement.textContent = ''; // Pulisci il testo
    }
}


const state = {
    conversations: JSON.parse(localStorage.getItem("arcadia_chats")) || [],
    activeConversationIndex: null,
    isWaitingForResponse: false,
    attachedFiles: [] // Spostiamo gli allegati nello stato principale
};

document.addEventListener("DOMContentLoaded", () => {
    console.log("[INIT] DOM completamente caricato");
    // Forza la creazione di una prima conversazione se non ce ne sono
    if(state.conversations.length === 0) {
        console.log("[INIT] Creazione conversazione iniziale");
        newConversation();
    }
    // Se ci sono conversazioni, attiva l'ultima
    else if (state.activeConversationIndex === null) {
        state.activeConversationIndex = state.conversations.length - 1;
    }
    renderUI(); // Rendi l'UI dopo il caricamento del DOM e l'inizializzazione dello stato
});


// Elementi DOM
const DOM = {
    newChatBtn: document.getElementById("new-chat-btn"),
    clearChatsBtn: document.getElementById("clear-chats-btn"), // Corretto da "clear-chat-btn"
    sendBtn: document.getElementById("send-btn"),
    input: document.getElementById("input"),
    chatbox: document.getElementById("chatbox"),
    chatList: document.getElementById("chat-list"),
    apiProvider: document.getElementById("api-provider"),
    fileInput: document.getElementById("file-input"),
    attachBtn: document.getElementById("attach-btn"),
    // filesPreview verrà creato dinamicamente in initFilesPreview()
    tosRead: document.getElementById("tos-read"), // Assicurati che questi elementi esistano nel tuo HTML
    tosAcceptBtn: document.getElementById("tos-accept-btn") // Assicurati che questi elementi esistano nel tuo HTML
};

// Funzioni per gestire messaggi e conferme personalizzati (sostituiscono alert/confirm)
// DEVONO essere implementati con elementi HTML per i modali.
function displayMessage(message, type = 'info') {
    // Esempio rudimentale: in un'app reale, si userebbe un modale o un toast.
    // Assumi l'esistenza di un elemento HTML con id="message-display"
    const messageDisplay = document.getElementById("message-display");
    if (messageDisplay) {
        messageDisplay.textContent = message;
        messageDisplay.className = `message-display ${type}`; // Aggiungi classi per styling (e.g., success, error, info)
        messageDisplay.style.display = 'block';
        setTimeout(() => {
            messageDisplay.style.display = 'none';
        }, 4000); // Nascondi dopo 4 secondi
    } else {
        console.warn("Elemento #message-display non trovato per visualizzare il messaggio:", message);
        // Fallback: visualizza in console se l'elemento non esiste
        // Non usare alert() in produzione, ma per i test iniziali può essere utile
        // alert(message); 
    }
}

function displayConfirm(message) {
    return new Promise(resolve => {
        // Assumi l'esistenza di un modale HTML con id="confirm-modal", un elemento per il testo
        // con id="confirm-message-text", e due bottoni con id="confirm-yes" e id="confirm-no".
        const confirmModal = document.getElementById("confirm-modal");
        const confirmMessageText = document.getElementById("confirm-message-text");
        const confirmYesBtn = document.getElementById("confirm-yes");
        const confirmNoBtn = document.getElementById("confirm-no");

        if (confirmModal && confirmMessageText && confirmYesBtn && confirmNoBtn) {
            confirmMessageText.textContent = message;
            confirmModal.style.display = 'block';

            const onYes = () => {
                confirmModal.style.display = 'none';
                confirmYesBtn.removeEventListener('click', onYes);
                confirmNoBtn.removeEventListener('click', onNo);
                resolve(true);
            };
            const onNo = () => {
                confirmModal.style.display = 'none';
                confirmYesBtn.removeEventListener('click', onYes);
                confirmNoBtn.removeEventListener('click', onNo);
                resolve(false);
            };

            confirmYesBtn.addEventListener('click', onYes);
            confirmNoBtn.addEventListener('click', onNo);
        } else {
            console.warn("Elementi #confirm-modal o correlati non trovati. Usando window.confirm come fallback.");
            resolve(window.confirm(message));
        }
    });
}


// Inizializza il preview degli allegati
function initFilesPreview() {
    if (!DOM.filesPreview) { // Controlla se è già stato creato
        DOM.filesPreview = document.createElement("div");
        DOM.filesPreview.id = "files-preview";
        // Inserisci filesPreview sotto l'input o prima della chatbox, a seconda del layout desiderato
        const inputContainer = DOM.input.parentNode;
        if (inputContainer) {
            inputContainer.parentNode.insertBefore(DOM.filesPreview, inputContainer.nextSibling);
        } else {
            // Fallback se la struttura del DOM è diversa
            document.body.appendChild(DOM.filesPreview);
        }
    }
    DOM.filesPreview.style.display = "none";
}

// Modifica la funzione setupFileHandling
async function setupFileHandling() {
    if (!DOM.attachBtn || !DOM.fileInput) {
        console.error("Elementi DOM per la gestione dei file non trovati");
        return;
    }

    // Pulsante di allegato
    DOM.attachBtn.addEventListener("click", (e) => {
        e.preventDefault();
        DOM.fileInput.value = ''; // Resetta il valore dell'input file per poter ricaricare gli stessi file
        DOM.fileInput.click();
    });

    // Gestione selezione file
    DOM.fileInput.addEventListener("change", async function(event) {
        if (!event.target.files || event.target.files.length === 0) return;

        const files = Array.from(event.target.files);
        const validTypes = [
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png',
            'image/webp'
        ];

        const validFiles = files.filter(file => {
            if (!validTypes.includes(file.type)) {
                displayMessage(`Tipo file non supportato: ${file.name}`, 'error');
                return false;
            }
            if (file.size > 10 * 1024 * 1024) { // Max 10MB per file
                displayMessage(`File troppo grande (max 10MB): ${file.name}`, 'error');
                return false;
            }
            return true;
        });

        if (validFiles.length === 0) {
            DOM.fileInput.value = ''; // Pulisci l'input anche se nessun file valido
            return;
        }

        DOM.attachBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; // Icona di caricamento
        DOM.attachBtn.disabled = true;

        try {
            state.attachedFiles = await Promise.all(validFiles.map(file => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve({
                        file: file, // Salva l'oggetto File originale
                        name: file.name,
                        type: file.type,
                        size: file.size,
                        // data: reader.result.split(',')[1] // Non è più necessario salvare base64 qui per ZIP service
                    });
                    reader.onerror = () => reject(new Error(`Errore lettura file ${file.name}`));
                    reader.readAsDataURL(file); // Ancora utile se il backend AI processa allegati
                });
            }));

            showFilesPreview(validFiles); // Mostra l'anteprima dei file validi
        } catch (error) {
            console.error("Errore nel caricamento:", error);
            displayMessage("Si è verificato un errore durante il caricamento dei file.", 'error');
            state.attachedFiles = []; // Resetta gli allegati in caso di errore
        } finally {
            DOM.attachBtn.innerHTML = '<i class="fas fa-paperclip"></i>'; // Ripristina l'icona
            DOM.attachBtn.disabled = false;
            DOM.fileInput.value = ''; // Pulisci l'input file dopo l'elaborazione
        }
    });
}

// Funzione per mostrare l'anteprima dei file allegati
function showFilesPreview(filesToDisplay) {
    if (!DOM.filesPreview) {
        console.error("Elemento DOM filesPreview non inizializzato.");
        return;
    }

    DOM.filesPreview.innerHTML = ''; // Pulisci l'anteprima esistente
    if (filesToDisplay.length === 0) {
        DOM.filesPreview.style.display = 'none';
        return;
    }

    filesToDisplay.forEach(file => {
        const preview = document.createElement('div');
        preview.className = 'file-preview-item';
        preview.innerHTML = `
            <span>${file.name} (${formatFileSize(file.size)})</span>
            <button class="remove-file" data-name="${file.name}">×</button>
        `;
        DOM.filesPreview.appendChild(preview);
    });

    // Aggiungi event listener per rimuovere i file
    document.querySelectorAll('.remove-file').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fileName = e.target.getAttribute('data-name');
            removeFile(fileName);
        });
    });

    DOM.filesPreview.style.display = 'block';
}

// Funzione per rimuovere un file dall'elenco degli allegati
function removeFile(fileName) {
    state.attachedFiles = state.attachedFiles.filter(f => f.name !== fileName);
    showFilesPreview(state.attachedFiles.map(f => f.file)); // Aggiorna la UI con gli oggetti File
}

// Formatta dimensione file
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}


// Inizializzazione
async function init() {
    console.log("Inizializzazione dell'applicazione...");

    try {
        // Debug: verifica elementi DOM
        console.log("Elementi DOM trovati:", {
            newChatBtn: !!DOM.newChatBtn,
            sendBtn: !!DOM.sendBtn,
            input: !!DOM.input,
            chatbox: !!DOM.chatbox,
            fileInput: !!DOM.fileInput,
            attachBtn: !!DOM.attachBtn,
            statusMessageElement: !!statusMessageElement // Verifica anche l'elemento stato
        });

        // Gestione dei Termini di Servizio (TOS) - se presenti nel tuo HTML
        if (DOM.tosRead && DOM.tosAcceptBtn) {
            const tosModal = document.getElementById("tos-modal");
            if (localStorage.getItem("arcadiaai-tos-accepted") !== "true") {
                if (tosModal) tosModal.style.display = "block";
                DOM.tosAcceptBtn.addEventListener("click", () => {
                    localStorage.setItem("arcadiaai-tos-accepted", "true");
                    if (tosModal) tosModal.style.display = "none";
                    init(); // Re-inizializza l'app dopo l'accettazione
                });
                return; // Blocca l'inizializzazione se i TOS non sono accettati
            } else {
                if (tosModal) tosModal.style.display = "none";
            }
        }

        initFilesPreview();
        loadConversations();
        setupEventListeners();
        await setupFileHandling();
        renderUI();

        // Debug: verifica stato iniziale
        console.log("Stato iniziale:", {
            conversations: state.conversations,
            activeConversationIndex: state.activeConversationIndex
        });
    } catch (error) {
        console.error("Errore durante l'inizializzazione:", error);
        displayMessage("Si è verificato un errore durante l'inizializzazione dell'applicazione", 'error');
    }
}

// Carica le conversazioni
function loadConversations() {
    try {
        const saved = localStorage.getItem("arcadia_chats");
        if (saved) {
            state.conversations = JSON.parse(saved);
            if (!Array.isArray(state.conversations)) {
                throw new Error("Dati non validi in localStorage");
            }

            if (state.conversations.length === 0) {
                newConversation();
            } else {
                state.conversations = state.conversations.map(conv => ({
                    id: conv.id || Date.now().toString(),
                    title: conv.title || "Nuova Chat",
                    messages: Array.isArray(conv.messages) ? conv.messages : [],
                    createdAt: conv.createdAt || new Date().toISOString(),
                    updatedAt: conv.updatedAt || new Date().toISOString()
                }));

                state.activeConversationIndex = state.conversations.length - 1;
            }
        } else {
            newConversation();
        }
    } catch (e) {
        console.error("Errore caricamento chat:", e);
        localStorage.removeItem("arcadia_chats");
        state.conversations = [];
        newConversation();
    }
}

// Setup event listeners
function setupEventListeners() {
    if (DOM.sendBtn) DOM.sendBtn.addEventListener("click", sendMessage);
    if (DOM.input) {
        DOM.input.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !state.isWaitingForResponse) {
                sendMessage();
            }
        });
    }
    if (DOM.newChatBtn) DOM.newChatBtn.addEventListener("click", newConversation);
    if (DOM.clearChatsBtn) DOM.clearChatsBtn.addEventListener("click", clearAllConversations);

    // Gestione dei menu delle chat - Aggiunto in setupEventListeners
    document.addEventListener('click', function(e) {
        // Chiudi tutti i menu aperti quando clicchi altrove
        if (!e.target.closest('.chat-menu')) {
            document.querySelectorAll('.chat-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}


// Render UI
function renderUI() {
    renderSidebar();
    renderMessages();
    renderInputState();
}

function renderSidebar() {
    if (!DOM.chatList) {
        console.error("Elemento chatList non trovato nel DOM");
        return;
    }
    DOM.chatList.innerHTML = "";

    state.conversations.forEach((conversation, index) => {
        const li = document.createElement("li");
        li.className = 'chat-item'; // Aggiungi la classe chat-item
        if (index === state.activeConversationIndex) {
            li.classList.add("active");
        }
        li.dataset.chatId = conversation.id; // Aggiungi l'id della chat

        li.innerHTML = `
            <div class="chat-item-content">
                <span class="chat-title">${conversation.title}</span>
                <span class="chat-date">${formatDate(conversation.updatedAt)}</span>
            </div>
            <div class="chat-menu">
                <button class="chat-menu-btn">⋮</button>
                <div class="chat-menu-content">
                    <button class="menu-action-rename" data-id="${conversation.id}">✏️ Rinomina</button>
                    <button class="menu-action-delete" data-id="${conversation.id}">🗑️ Elimina</button>
                    <button class="menu-action-export" data-id="${conversation.id}">📤 Esporta</button>
                </div>
            </div>
        `;
        
        // Event listener per aprire/chiudere il menu
        const menuBtn = li.querySelector('.chat-menu-btn');
        const chatMenu = li.querySelector('.chat-menu');
        if (menuBtn && chatMenu) {
            menuBtn.addEventListener('click', function(e) {
                e.stopPropagation(); // Evita che il click si propaghi al li principale
                document.querySelectorAll('.chat-menu').forEach(m => {
                    if (m !== chatMenu) { // Chiudi gli altri menu
                        m.classList.remove('show');
                    }
                });
                chatMenu.classList.toggle('show'); // Apri/chiudi questo menu
            });
        }

        // Event listener per la selezione della chat (solo se non si clicca sul menu)
        li.addEventListener("click", (e) => {
            if (!e.target.closest('.chat-menu')) {
                state.activeConversationIndex = index;
                renderUI();
                DOM.input.focus();
            }
        });

        DOM.chatList.appendChild(li);
    });

    if (state.conversations.length === 0) {
        DOM.chatList.innerHTML = '<li class="empty">Nessuna conversazione</li>';
    }

    // Aggiungi event listeners per le azioni del menu dopo che gli elementi sono nel DOM
    document.querySelectorAll('.menu-action-rename').forEach(btn => {
        btn.onclick = (e) => { e.stopPropagation(); renameChat(e.target.dataset.id); };
    });
    document.querySelectorAll('.menu-action-delete').forEach(btn => {
        btn.onclick = (e) => { e.stopPropagation(); deleteChat(e.target.dataset.id); };
    });
    document.querySelectorAll('.menu-action-export').forEach(btn => {
        btn.onclick = (e) => { e.stopPropagation(); exportChat(e.target.dataset.id); };
    });
}
function renderMessages() {
    if (!DOM.chatbox) {
        console.error("Elemento chatbox non trovato nel DOM");
        return;
    }

    DOM.chatbox.innerHTML = "";

    // Mostra messaggio di benvenuto se non ci sono conversazioni
    if (state.activeConversationIndex === null || !state.conversations[state.activeConversationIndex]) {
        const welcomeMsg = document.createElement("div");
        welcomeMsg.className = "welcome-message";
        welcomeMsg.textContent = "Crea una nuova chat per iniziare";
        DOM.chatbox.appendChild(welcomeMsg);
        return;
    }

    const conversation = state.conversations[state.activeConversationIndex];

    // Mostra messaggio se la conversazione è vuota
    if (!conversation.messages || conversation.messages.length === 0) {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Nessun messaggio in questa conversazione";
        DOM.chatbox.appendChild(emptyMsg);
        return;
    }

    // Renderizza tutti i messaggi
    conversation.messages.forEach(msg => {
        if (!msg || !msg.sender || !msg.text) {
            console.warn("Messaggio non valido:", msg);
            return;
        }

        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${msg.sender}-message`;

        // Contenitore principale del messaggio
        const messageContent = document.createElement("div");
        messageContent.className = "message-content";

        // Gestione allegati (se presenti)
        if (msg.text.includes("📎 Allegati:")) {
            const parts = msg.text.split("📎 Allegati:");
            
            // Parte testuale del messaggio
            if (parts[0].trim()) {
                const textPart = document.createElement("div");
                textPart.innerHTML = parts[0].trim().replace(/\n/g, '<br>');
                messageContent.appendChild(textPart);
            }
            
            // Sezione allegati
            const attachmentsPart = document.createElement("div");
            attachmentsPart.className = "attachments-info";
            
            const attachmentsIcon = document.createElement("span");
            attachmentsIcon.textContent = "📎";
            attachmentsPart.appendChild(attachmentsIcon);
            
            const attachmentsText = document.createElement("span");
            attachmentsText.textContent = "Allegati: " + parts[1].trim();
            attachmentsPart.appendChild(attachmentsText);
            
            messageContent.appendChild(attachmentsPart);
        } else {
            // Messaggio normale (conversazione)
            messageContent.innerHTML = msg.text.replace(/\n/g, '<br>');
        }

        // Aggiungi timestamp se disponibile
        if (msg.timestamp) {
            const timestampDiv = document.createElement("div");
            timestampDiv.className = "message-timestamp";
            timestampDiv.textContent = formatTime(msg.timestamp);
            messageDiv.appendChild(timestampDiv);
        }

        messageDiv.appendChild(messageContent);
        DOM.chatbox.appendChild(messageDiv);
    });

    // Scorri automaticamente in basso
    DOM.chatbox.scrollTop = DOM.chatbox.scrollHeight;
}

// Funzione helper per formattare l'ora
function formatTime(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    } catch (e) {
        console.error("Errore formattazione data:", e);
        return "";
    }
}
    DOM.chatbox.scrollTop = DOM.chatbox.scrollHeight;


function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function newConversation() {
    const newChat = {
        id: Date.now().toString(),
        title: `Chat ${state.conversations.length + 1}`,
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    state.conversations.push(newChat);
    state.activeConversationIndex = state.conversations.length - 1;

    saveToLocalStorage();
    renderUI();
    DOM.input.focus();
}
async function clearAllConversations() {
    const confirmed = await displayConfirm("Sei sicuro di voler cancellare tutte le conversazioni? Questa azione non può essere annullata.");
    if (confirmed) {
        state.conversations = [];
        state.activeConversationIndex = null;
        localStorage.removeItem("arcadia_chats");
        newConversation();
        renderUI();
        displayMessage("Tutte le conversazioni sono state cancellate.", 'info');
    }
}


// --- Funzione per creare ZIP (richiede un backend) ---
async function createZipFromFiles(files) {
    if (!files || files.length === 0) {
        return "❌ Nessun file selezionato";
    }

    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file); // files deve essere un array di oggetti File
    });

    try {
        // CORREZIONE CRUCIALE: Invio al servizio ZIP su Render, non al bot principale
        const response = await fetch('https://zip-service.onrender.com/create-zip/', { // <-- CORRETTO
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorDetail = response.statusText;
            try {
                const errorJson = await response.json();
                errorDetail = errorJson.detail || JSON.stringify(errorJson);
            } catch (e) {
                // Se non è JSON, usiamo il testo grezzo
                errorDetail = await response.text();
            }
            throw new Error(`Errore HTTP ${response.status}: ${errorDetail}`);
        }

        const data = await response.json();
        const downloadUrl = `https://zip-service.onrender.com${data.download_url}`; // Costruisci l'URL completo

        return `✅ ZIP creato con successo! <a href="${downloadUrl}" target="_blank" download>Scarica qui</a>`;
    } catch (error) {
        console.error("Errore creazione ZIP:", error);
        throw new Error(`❌ Errore durante la creazione dello ZIP: ${error.message}`); // Rilancia l'errore per gestirlo fuori
    }
}

// --- Modifica sendMessage per gestire comandi speciali e stato ---
async function sendMessage() {
    // 1. Verifica iniziale dello stato
    if (state.isWaitingForResponse) {
        console.warn("Attesa di una risposta già in corso");
        return;
    }
    const message = DOM.input.value.trim();
    if (!message && state.attachedFiles.length === 0) {
        console.warn("Nessun contenuto da inviare");
        return;
    }
    
    // 2. Verifica e inizializzazione conversazione
    if (state.conversations.length === 0 || state.activeConversationIndex === null) {
        console.log("Nessuna conversazione attiva, ne creo una nuova");
        newConversation();
    }

    const conversation = state.conversations[state.activeConversationIndex];
    if (!conversation) {
        console.error("Conversazione non valida");
        return;
    }

    // Aggiungi il messaggio utente alla conversazione e renderizza subito
    addUserMessageToConversation(message);
    DOM.input.value = "";
    renderMessages();

    // 3. Gestione comandi speciali con messaggi di stato
    state.isWaitingForResponse = true;
    renderInputState(); // Disabilita input e bottone

    try {
        const lowerCaseMessage = message.toLowerCase();
        
        if (lowerCaseMessage.startsWith("@crea zip")) {
            showStatus("In esecuzione Zip Service: creazione ZIP in corso...");
            await handleZipCommand(); 
        } 
        else if (lowerCaseMessage.startsWith("@winget") || 
                 lowerCaseMessage.startsWith("@app") || 
                 lowerCaseMessage.startsWith("@cerca")) {
            showStatus("Ricerca in corso..."); 
            await sendGeneralMessageToBackend(message, conversation);
        } 
        else if (lowerCaseMessage.startsWith("@impostazioni modalità sperimentale")) {
            showStatus("Aggiornamento impostazioni...");
            handleExperimentalModeSettings(message);
            setTimeout(hideStatus, 1000); 
        }
        else if (lowerCaseMessage.startsWith("@esporta")) {
            showStatus("Preparazione esportazione...");
            const chatId = conversation.id;
            const success = await exportChat(chatId);
            if (success) {
                addMessageToConversation("ai", "✅ Chat esportata con successo!");
            }
            setTimeout(hideStatus, 1000);
        }
        else if (lowerCaseMessage.startsWith("@importa")) {
            showStatus("Preparazione importazione...");
            await handleImportCommand();
            setTimeout(hideStatus, 1000);
        }
        else if (lowerCaseMessage.startsWith("@rinomina")) {
    showStatus("Preparazione rinomina chat...");
    
    // Estrai il nome automatico se presente nel formato @rinomina_nome:"Nuovo Nome"
    const autoRenameMatch = message.match(/@rinomina(?:_nome)?:"([^"]+)"/i);
    
    if (autoRenameMatch && autoRenameMatch[1]) {
        // Modalità automatica con nome incluso
        const newTitle = autoRenameMatch[1].trim();
        if (newTitle.length > 0) {
            conversation.title = newTitle;
            conversation.updatedAt = new Date().toISOString();
            saveToLocalStorage();
            renderSidebar();
            addMessageToConversation("ai", `✅ Chat rinominata in "${newTitle}"`);
        } else {
            addMessageToConversation("ai", "❌ Il nome della chat non può essere vuoto");
        }
    } 
    else {
        // Modalità interattiva
        const newTitle = prompt("Inserisci il nuovo nome per la chat:", conversation.title);
        if (newTitle !== null) { // L'utente non ha premuto Annulla
            if (newTitle.trim().length > 0) {
                conversation.title = newTitle.trim();
                conversation.updatedAt = new Date().toISOString();
                saveToLocalStorage();
                renderSidebar();
                addMessageToConversation("ai", `✅ Chat rinominata in "${newTitle.trim()}"`);
            } else {
                addMessageToConversation("ai", "❌ Il nome della chat non può essere vuoto");
            }
        }
    }
    
    setTimeout(hideStatus, 1000);
}
        else if (lowerCaseMessage.startsWith("@aiuto")) {
            showStatus("Mostro i comandi disponibili...");
            const helpMessage = `📚 Comandi disponibili:\n\n` +
                               `@esporta - Esporta la chat corrente\n` +
                               `@crea zip - Crea un ZIP dagli allegati\n` +
                               `@winget [app] - Cerca un'applicazione\n` +
                               `@app [nome] - Cerca informazioni su un'app\n` +
                               `@cerca [query] - Esegue una ricerca\n` +
                               `@impostazioni modalità sperimentale [attiva/disattiva]\n\n` +
                               `Puoi anche allegare file (max 10MB) cliccando sull'icona della graffetta.`;
            addMessageToConversation("ai", helpMessage);
            setTimeout(hideStatus, 1000);
        }
        else {
            showStatus("AI in elaborazione...");
            await sendGeneralMessageToBackend(message, conversation);
        }
    } catch (error) {
        console.error("Errore nel comando o nell'invio:", error);
        showStatus(`❌ Errore: ${error.message}.`);
        addMessageToConversation("ai", `❌ Si è verificato un errore: ${error.message}`);
        setTimeout(hideStatus, 5000); 
    } finally {
        resetSendState();
        // Garantisce che hideStatus sia chiamato dopo un breve ritardo per i percorsi di successo
        if (statusMessageElement && 
            statusMessageElement.style.display === 'block' && 
            !statusMessageElement.textContent.startsWith('❌')) {
            setTimeout(hideStatus, 1500);
        } else {
            hideStatus();
        }
    }
}

// Funzione separata per invio di messaggi generici al backend AI
async function sendGeneralMessageToBackend(message, conversation) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // Timeout dopo 30 secondi

        const response = await fetch("https://arcadiaai.onrender.com/chat", { // URL CORRETTO per il tuo bot principale
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                conversation_history: conversation.messages.map(m => ({
                    role: m.sender === 'user' ? 'user' : 'model',
                    message: m.text
                })),
                api_provider: DOM.apiProvider ? DOM.apiProvider.value : 'default',
                experimental_mode: localStorage.getItem("arcadiaai-experimental-mode") === "true",
                // Passa gli allegati come array di oggetti {name, type, data} se il backend li processa
                attachments: state.attachedFiles.map(f => ({
                    name: f.name,
                    type: f.type,
                    data: f.data // La parte base64 se il backend la richiede
                }))
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorDetails = await response.text();
            throw new Error(`Errore HTTP ${response.status}: ${errorDetails || response.statusText}`);
        }

        const data = await response.json();
        processBackendResponse(data, message, conversation);
    } catch (error) {
        const errorMessage = error.name === 'AbortError'
            ? "❌ Timeout: il server AI non ha risposto entro 30 secondi."
            : `❌ Errore durante l'invio al server AI: ${error.message}.`;
        addMessageToConversation("ai", errorMessage);
        throw error; // Rilancia l'errore per essere gestito dal blocco finally esterno
    } finally {
        // La logica hideStatus è centralizzata nella funzione sendMessage
    }
}


async function handleZipCommand() {
    // stato.attachedFiles ora contiene oggetti { file: File, name: string, type: string, size: number }
    if (state.attachedFiles.length === 0) {
        addMessageToConversation("ai", "❌ Nessun file allegato per creare lo ZIP.");
        return;
    }

    try {
        // Passa gli oggetti File originali a createZipFromFiles
        const filesToUpload = state.attachedFiles.map(f => f.file);
        
        const resultHTML = await createZipFromFiles(filesToUpload); // createZipFromFiles restituisce una stringa HTML
        addMessageToConversation("ai", resultHTML); // Inserisci la stringa HTML direttamente
    } catch (error) {
        console.error("Errore creazione ZIP:", error);
        addMessageToConversation("ai", error.message); // Usa il messaggio d'errore lanciato da createZipFromFiles
    } finally {
        resetAttachments(); // Pulisci gli allegati dopo il tentativo di creazione ZIP
        // La logica hideStatus è centralizzata nella funzione sendMessage
    }
}

function handleExperimentalModeSettings(message) {
    const msg = message.trim().toLowerCase();
    if (msg === "@impostazioni modalità sperimentale attiva") {
        localStorage.setItem("arcadiaai-experimental-mode", "true");
        updateExperimentalToggle(true);
        addMessageToConversation("ai", "✅ Modalità sperimentale attivata.");
    } else if (msg === "@impostazioni modalità sperimentale disattiva") {
        localStorage.setItem("arcadiaai-experimental-mode", "false");
        updateExperimentalToggle(false);
        addMessageToConversation("ai", "❌ Modalità sperimentale disattivata.");
    }
}

function addUserMessageToConversation(message) {
    const content = state.attachedFiles.length > 0
        ? `${message ? message + '\n\n' : ''}📎 Allegati: ${state.attachedFiles.map(f => f.name).join(', ')}`
        : message;

    addMessageToConversation("user", content);
}

function processBackendResponse(data, message, conversation) {
    const reply = data.reply || "❌ Nessuna risposta dal server.";

    if (reply.includes("Modalità sperimentale")) {
        const isActive = reply.includes("attivata");
        localStorage.setItem("arcadiaai-experimental-mode", isActive.toString());
        updateExperimentalToggle(isActive);
    }

    addMessageToConversation("ai", reply);

    if (conversation.messages.length === 2 && conversation.messages[0].sender === 'user') {
        updateConversationTitle(conversation, conversation.messages[0].text);
    }
}

function resetSendState() {
    state.isWaitingForResponse = false;
    resetAttachments();
    renderInputState();
}

function resetAttachments() {
    state.attachedFiles = [];
    if (DOM.fileInput) DOM.fileInput.value = '';
    if (DOM.filesPreview) {
        DOM.filesPreview.innerHTML = '';
        DOM.filesPreview.style.display = 'none';
    }
}

function updateExperimentalToggle(isEnabled) {
    const expToggle = document.getElementById("experimental-mode-toggle");
    if (expToggle) {
        expToggle.checked = isEnabled;
    }
}

function addMessageToConversation(sender, text) {
    if (state.activeConversationIndex === null) {
        newConversation();
    }

    const message = {
        sender,
        text,
        timestamp: new Date().toISOString()
    };

    const conversation = state.conversations[state.activeConversationIndex];
    if (conversation) {
        conversation.messages.push(message);
        conversation.updatedAt = new Date().toISOString();

        saveToLocalStorage();
        renderMessages();
    } else {
        console.error("Errore: conversazione attiva non trovata per aggiungere messaggio.");
    }
}

function updateConversationTitle(conversation, firstMessage) {
    const newTitle = firstMessage.length > 20
        ? firstMessage.substring(0, 20) + "..."
        : firstMessage;

    conversation.title = newTitle;
    saveToLocalStorage();
    renderSidebar();
}

function saveToLocalStorage() {
    localStorage.setItem("arcadia_chats", JSON.stringify(state.conversations));
}

function renderInputState() {
    if (DOM.input) {
        DOM.input.disabled = state.isWaitingForResponse;
        DOM.input.placeholder = state.isWaitingForResponse
            ? "In attesa di risposta..."
            : "Scrivi un messaggio...";
    }
    if (DOM.sendBtn) DOM.sendBtn.disabled = state.isWaitingForResponse;
    if (DOM.attachBtn) DOM.attachBtn.disabled = state.isWaitingForResponse; // Disabilita anche il bottone allegato
}

// Avvia l'applicazione quando il DOM è completamente caricato
document.addEventListener("DOMContentLoaded", init);

// --- Funzioni di gestione dei menu della chat (aggiunte al global scope o come parte di un oggetto) ---

async function renameChat(chatId) {
    const chatToRename = state.conversations.find(conv => conv.id === chatId);
    if (!chatToRename) {
        console.error(`Chat con ID ${chatId} non trovata.`);
        displayMessage("Errore: Chat non trovata per rinomina.", 'error');
        return;
    }

    const newTitle = prompt('Inserisci il nuovo nome per la chat:');
    if (newTitle && newTitle.trim() !== '') {
        chatToRename.title = newTitle.trim();
        saveToLocalStorage();
        renderSidebar(); // Aggiorna la sidebar per mostrare il nuovo titolo
        displayMessage("Chat rinominata con successo!", 'success');
    } else if (newTitle !== null) { // L'utente ha premuto OK ma ha lasciato vuoto
        displayMessage("Il nome della chat non può essere vuoto.", 'warning');
    }
}

async function deleteChat(chatId) {
    const confirmed = await displayConfirm('Sei sicuro di voler eliminare questa chat? Questa azione non può essere annullata.');
    if (confirmed) {
        const initialCount = state.conversations.length;
        state.conversations = state.conversations.filter(conv => conv.id !== chatId);
        
        if (state.conversations.length === initialCount) {
            console.error(`Chat con ID ${chatId} non trovata per eliminazione.`);
            displayMessage("Errore: Chat non trovata per eliminazione.", 'error');
            return;
        }

        // Aggiorna activeConversationIndex se la chat attiva è stata eliminata
        if (state.activeConversationIndex !== null && state.conversations[state.activeConversationIndex] && state.conversations[state.activeConversationIndex].id === chatId) {
            state.activeConversationIndex = null;
        }

        if (state.conversations.length === 0) {
            newConversation(); // Se non ci sono più chat, creane una nuova
        } else if (state.activeConversationIndex === null || state.activeConversationIndex >= state.conversations.length) {
            state.activeConversationIndex = state.conversations.length - 1; // Seleziona l'ultima
        }

        saveToLocalStorage();
        renderUI();
        displayMessage("Chat eliminata con successo!", 'info');
    }
}

async function exportChat(chatId) {
    try {
        const chatToExport = state.conversations.find(conv => conv.id === chatId);
        if (!chatToExport) {
            throw new Error(`Chat con ID ${chatId} non trovata`);
        }

        // Formatta meglio il contenuto della chat
        const chatContent = chatToExport.messages.map(msg => {
            const sender = msg.sender.toUpperCase();
            const timestamp = new Date(msg.timestamp).toLocaleString('it-IT');
            return `[${timestamp}] ${sender}:\n${msg.text}\n${'-'.repeat(50)}`;
        }).join('\n\n');

        // Aggiungi un'intestazione con i metadati della chat
        const header = `TITOLO CHAT: ${chatToExport.title}\n` +
                       `CREATA IL: ${formatDate(chatToExport.createdAt)}\n` +
                       `ULTIMO AGGIORNAMENTO: ${formatDate(chatToExport.updatedAt)}\n` +
                       `NUMERO MESSAGGI: ${chatToExport.messages.length}\n\n`;
        
        const fullContent = header + chatContent;
        const blob = new Blob([fullContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `ArcadiaAI_Chat_${chatToExport.title.replace(/[^a-z0-9]/gi, '_')}_${formatDate(chatToExport.createdAt).replace(/\//g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        
        // Pulizia
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);

        return true;
    } catch (error) {
        console.error("Errore durante l'esportazione:", error);
        displayMessage(`❌ Errore durante l'esportazione: ${error.message}`, 'error');
        return false;
    }
}
async function handleImportCommand() {
    return new Promise((resolve) => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.txt,.json';
        
        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return resolve(false);
            
            showStatus("Sto importando la chat...");
            
            try {
                const content = await file.text();
                const parsedChat = parseImportedChat(content);
                
                // Crea nuova conversazione
                const newChat = {
                    id: Date.now().toString(),
                    title: parsedChat.title || `Import-${file.name.replace(/\.[^/.]+$/, "")}`,
                    messages: parsedChat.messages,
                    createdAt: parsedChat.createdAt || new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };
                
                state.conversations.push(newChat);
                state.activeConversationIndex = state.conversations.length - 1;
                saveToLocalStorage();
                renderUI();
                
                addMessageToConversation("ai", `✅ Chat "${newChat.title}" importata con successo! (${parsedChat.messages.length} messaggi)`);
                resolve(true);
            } catch (error) {
                console.error("Errore importazione:", error);
                addMessageToConversation("ai", `❌ Errore durante l'importazione: ${error.message}\n\nFormati supportati:\n1. "USER: messaggio\\nAI: risposta"\n2. JSON strutturato`);
                resolve(false);
            }
        };
        
        fileInput.click();
    });
}
function parseImportedChat(content) {
    content = content.trim();
    if (!content) throw new Error("Il file è vuoto");

    // Prova a parsare come JSON
    if (content.startsWith('{') || content.startsWith('[')) {
        try {
            const data = JSON.parse(content);
            if (Array.isArray(data)) {
                return {
                    title: `Import-${formatDate(new Date())}`,
                    messages: data.map(msg => ({
                        sender: msg.sender?.toLowerCase() === 'ai' ? 'ai' : 'user',
                        text: msg.text || '',
                        timestamp: msg.timestamp || new Date().toISOString()
                    })),
                    createdAt: new Date().toISOString()
                };
            }
            if (data.messages) {
                return {
                    title: data.title || `Import-${formatDate(new Date())}`,
                    messages: data.messages.map(msg => ({
                        sender: msg.sender?.toLowerCase() === 'ai' ? 'ai' : 'user',
                        text: msg.text || '',
                        timestamp: msg.timestamp || new Date().toISOString()
                    })),
                    createdAt: data.createdAt || new Date().toISOString()
                };
            }
        } catch (e) {
            console.log("Non è un JSON valido, provo con formato testo");
        }
    }

    // Formato testo
    try {
        const lines = content.split('\n');
        const messages = [];
        let currentSender = null;
        let currentText = [];

        for (const line of lines) {
            const senderMatch = line.match(/^(USER|AI|ASSISTANT|CHATBOT):\s*(.*)$/i);
            
            if (senderMatch) {
                if (currentSender) {
                    messages.push({
                        sender: currentSender.toLowerCase() === 'ai' ? 'ai' : 'user',
                        text: currentText.join('\n').trim(),
                        timestamp: new Date().toISOString()
                    });
                }
                currentSender = senderMatch[1];
                currentText = [senderMatch[2]];
            } else {
                currentText.push(line);
            }
        }

        if (currentSender) {
            messages.push({
                sender: currentSender.toLowerCase() === 'ai' ? 'ai' : 'user',
                text: currentText.join('\n').trim(),
                timestamp: new Date().toISOString()
            });
        }

        if (messages.length === 0 && content) {
            return {
                title: `Import-${formatDate(new Date())}`,
                messages: [{
                    sender: 'user',
                    text: content,
                    timestamp: new Date().toISOString()
                }],
                createdAt: new Date().toISOString()
            };
        }

        return {
            title: `Import-${formatDate(new Date())}`,
            messages,
            createdAt: new Date().toISOString()
        };
    } catch (e) {
        console.error("Errore parsing chat:", e);
        throw new Error(`Formato file non riconosciuto. Usa:\nUSER: messaggio\nAI: risposta\n\nO esporta una chat dal sistema per ottenere un JSON valido`);
    }
}
