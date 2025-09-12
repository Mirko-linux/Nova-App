// accountManager.js
const accountManager = (() => {
  const USERS_KEY = 'arcadia:users';
  const SESSION_KEY = 'arcadia:session';
  const CONV_KEY_PREFIX = 'arcadia:conversations:';

  // 🔐 Hash password con SHA-256
  async function hashPassword(password) {
    const enc = new TextEncoder().encode(password);
    const buf = await crypto.subtle.digest('SHA-256', enc);
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
  }

  // 📦 Carica utenti
  function loadUsers() {
    try {
      const raw = localStorage.getItem(USERS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  // 💾 Salva utenti
  function saveUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }

  // 👤 Ottieni utente attivo
  function getCurrentUser() {
    const session = localStorage.getItem(SESSION_KEY);
    if (!session) return { id: 'guest', username: 'Guest' };
    try {
      return JSON.parse(session);
    } catch {
      return { id: 'guest', username: 'Guest' };
    }
  }

  // 🔐 Registrazione
  async function registerUser(username, password) {
    const users = loadUsers();
    if (users.find(u => u.username === username)) {
      throw new Error('Username già esistente');
    }
    const passwordHash = await hashPassword(password);
    const newUser = {
      id: crypto.randomUUID(),
      username,
      passwordHash,
      createdAt: Date.now()
    };
    users.push(newUser);
    saveUsers(users);
    localStorage.setItem(SESSION_KEY, JSON.stringify({ id: newUser.id, username }));
    return newUser;
  }

  // 🔓 Login
  async function loginUser(username, password) {
    const users = loadUsers();
    const user = users.find(u => u.username === username);
    if (!user) throw new Error('Utente non trovato');
    const hash = await hashPassword(password);
    if (hash !== user.passwordHash) throw new Error('Password errata');
    localStorage.setItem(SESSION_KEY, JSON.stringify({ id: user.id, username }));
    return user;
  }

  // 🚪 Logout
  function logoutUser() {
    localStorage.removeItem(SESSION_KEY);
  }

  // 💬 Salva conversazioni per utente
  function saveConversationsForUser(conversations) {
    const user = getCurrentUser();
    const key = CONV_KEY_PREFIX + user.id;
    localStorage.setItem(key, JSON.stringify(conversations));
  }

  // 📂 Carica conversazioni per utente
  function loadConversationsForUser() {
    const user = getCurrentUser();
    const key = CONV_KEY_PREFIX + user.id;
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  return {
    registerUser,
    loginUser,
    logoutUser,
    getCurrentUser,
    saveConversationsForUser,
    loadConversationsForUser
  };
})();
