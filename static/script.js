const chatArea = document.getElementById('chatArea');
const messageInput = document.getElementById('messageInput');
const composer = document.getElementById('composer');
const typing = document.getElementById('typing');
const themeToggle = document.getElementById('themeToggle');
const suggestionsEl = document.getElementById('suggestions');
const menuBtn = document.getElementById('menuBtn');
const sidebar = document.getElementById('sidebar');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPop = document.getElementById('emojiPop');
const exportBtn = document.getElementById('exportBtn');
const healthDot = document.getElementById('healthDot');

const STORAGE_KEY = 'ai_chatbot_history_v1';

function formatTime(d = new Date()) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) || [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

function renderMessage(item) {
  const row = document.createElement('div');
  row.className = 'bubble-row ' + (item.role === 'user' ? 'user' : 'bot');

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = item.role === 'user' ? '🧑' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'bubble' + (item.role === 'user' ? ' user' : '');

  const text = document.createElement('div');
  text.className = 'msg-text';
  text.textContent = item.message;

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.innerHTML = `<span>${item.role === 'user' ? 'You' : 'Assistant'}</span><span>${item.time || formatTime()}</span>`;

  bubble.appendChild(text);
  bubble.appendChild(meta);

  if (item.role === 'user') {
    row.appendChild(bubble);
    row.appendChild(avatar);
  } else {
    row.appendChild(avatar);
    row.appendChild(bubble);
  }

  return row;
}

function renderHistory(history) {
  chatArea.innerHTML = '';
  history.forEach((m) => chatArea.appendChild(renderMessage(m)));
  scrollToBottom();
}

function setTyping(on) {
  typing.hidden = !on;
}

async function checkHealth() {
  try {
    const r = await fetch('/api/health');
    healthDot.style.background = r.ok ? 'rgba(46,233,166,0.95)' : 'rgba(255,77,109,0.95)';
  } catch {
    healthDot.style.background = 'rgba(255,77,109,0.95)';
  }
}

async function loadSuggestions() {
  try {
    const r = await fetch('/api/quick_suggestions');
    const data = await r.json();
    suggestionsEl.innerHTML = '';
    (data.suggestions || []).forEach((s) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'suggestion';
      btn.textContent = s;
      btn.addEventListener('click', () => {
        messageInput.value = s;
        messageInput.focus();
      });
      suggestionsEl.appendChild(btn);
    });
  } catch {
    // silent
  }
}

function autoGrow() {
  messageInput.style.height = 'auto';
  messageInput.style.height = messageInput.scrollHeight + 'px';
}

function getTheme() {
  return localStorage.getItem('theme') || 'dark';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme === 'light' ? 'light' : 'dark');
}

function toggleTheme() {
  const cur = getTheme();
  const next = cur === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', next);
  applyTheme(next);
}

function addEmoji(e) {
  const start = messageInput.selectionStart || messageInput.value.length;
  const end = messageInput.selectionEnd || messageInput.value.length;
  const before = messageInput.value.slice(0, start);
  const after = messageInput.value.slice(end);
  messageInput.value = before + e + after;
  messageInput.selectionStart = messageInput.selectionEnd = start + e.length;
  messageInput.focus();
  autoGrow();
}

function exportChat() {
  const history = loadHistory();
  const payload = {
    exportedAt: new Date().toISOString(),
    history
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'chat-export.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

let history = loadHistory();
renderHistory(history);
applyTheme(getTheme());

checkHealth();
loadSuggestions();

themeToggle?.addEventListener('click', () => toggleTheme());

menuBtn?.addEventListener('click', () => {
  sidebar.classList.toggle('open');
});

window.addEventListener('click', (e) => {
  if (emojiPop && !emojiPop.hidden && !emojiPop.contains(e.target) && e.target !== emojiBtn) {
    emojiPop.hidden = true;
  }
});

emojiBtn?.addEventListener('click', () => {
  emojiPop.hidden = !emojiPop.hidden;
});

emojiPop?.querySelectorAll('button')?.forEach((b) => {
  b.addEventListener('click', () => addEmoji(b.textContent));
});

exportBtn?.addEventListener('click', () => exportChat());

document.querySelectorAll('[data-action="new"]').forEach((btn) => {
  btn.addEventListener('click', () => {
    history = [];
    saveHistory(history);
    renderHistory(history);
  });
});

composer.addEventListener('submit', async (e) => {
  e.preventDefault();

  const message = (messageInput.value || '').trim();
  if (!message) return;

  const userMsg = { role: 'user', message, time: formatTime() };
  history.push(userMsg);
  saveHistory(history);
  chatArea.appendChild(renderMessage(userMsg));
  scrollToBottom();

  messageInput.value = '';
  autoGrow();

  // Typing indicator
  setTyping(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history })
    });
    const data = await res.json();

    const botMsg = { role: 'assistant', message: data.reply || 'No response.', time: formatTime() };
    history.push(botMsg);
    saveHistory(history);

    setTyping(false);
    chatArea.appendChild(renderMessage(botMsg));
    scrollToBottom();
  } catch {
    setTyping(false);
    const botMsg = {
      role: 'assistant',
      message: 'Network error. Please try again.',
      time: formatTime()
    };
    history.push(botMsg);
    saveHistory(history);
    chatArea.appendChild(renderMessage(botMsg));
    scrollToBottom();
  }
});

messageInput.addEventListener('input', autoGrow);

// Enter to send (Shift+Enter for newline)
messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});

