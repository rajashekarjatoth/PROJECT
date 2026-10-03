/**
 * COGNITIVE ASSISTANCE & INTERVIEW PREPARATION BOT
 * Socratic Conversational Mentor & NLP Dialogue Controller
 */

const ChatState = {
  mode: 'mentor',       // 'mentor' or 'direct'
  level: 'intermediate', // 'beginner', 'intermediate', 'advanced'
  useRag: true,
  isWaiting: false
};

function setChatMode(mode) {
  ChatState.mode = mode;
  document.getElementById('chatModeMentor').classList.toggle('active', mode === 'mentor');
  document.getElementById('chatModeDirect').classList.toggle('active', mode === 'direct');
  showToast(`Switched to ${mode === 'mentor' ? 'Socratic Mentor' : 'Direct Reference'} mode.`, 'info');
}

function setChatLevel(level) {
  ChatState.level = level;
  ['Beginner', 'Intermediate', 'Advanced'].forEach(lvl => {
    const el = document.getElementById(`chatLevel${lvl}`);
    if (el) el.classList.toggle('active', lvl.toLowerCase() === level);
  });
  showToast(`Explanation depth set to: ${level.toUpperCase()}`, 'info');
}

function handleChatKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const inputEl = document.getElementById('chatInputText');
  const message = inputEl.value.trim();
  if (!message || ChatState.isWaiting) return;

  // Clear input
  inputEl.value = '';

  // Append user message bubble
  appendChatBubble('user', message);

  // Loading indicator bubble
  ChatState.isWaiting = true;
  const loadingBubble = appendChatBubble('assistant', '<i class="fa-solid fa-spinner fa-spin"></i> Consulting cognitive knowledge base...');

  const useRag = document.getElementById('chatUseRagToggle')?.checked ?? true;

  try {
    const res = await apiRequest('/chat', 'POST', {
      message: message,
      mode: ChatState.mode,
      level: ChatState.level,
      use_rag: useRag
    });

    // Replace loading bubble with formatted response
    loadingBubble.innerHTML = formatMarkdownReply(res.reply);

    // If ambiguous question was detected, append quick clarification options
    if (res.is_ambiguous && res.clarification_question) {
      const clarifyBox = document.createElement('div');
      clarifyBox.style.marginTop = '0.75rem';
      clarifyBox.style.display = 'flex';
      clarifyBox.style.flexWrap = 'wrap';
      clarifyBox.style.gap = '0.4rem';

      const options = [
        "Focus on system architecture & trade-offs",
        "Give a practical code example",
        "Explain memory & performance implications"
      ];

      options.forEach(opt => {
        const chip = document.createElement('button');
        chip.className = 'btn btn-secondary btn-sm';
        chip.style.fontSize = '0.75rem';
        chip.innerText = opt;
        chip.onclick = () => {
          inputEl.value = `${message} — ${opt}`;
          sendChatMessage();
        };
        clarifyBox.appendChild(chip);
      });

      loadingBubble.appendChild(clarifyBox);
    }

  } catch (err) {
    loadingBubble.innerHTML = `<span style="color: var(--accent-rose);"><i class="fa-solid fa-circle-exclamation"></i> Error: ${err.message}</span>`;
  } finally {
    ChatState.isWaiting = false;
  }
}

function appendChatBubble(role, content) {
  const container = document.getElementById('chatMessagesArea');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;
  bubble.innerHTML = role === 'user' ? escapeHtml(content) : content;
  container.appendChild(bubble);

  // Auto-scroll
  container.scrollTop = container.scrollHeight;
  return bubble;
}

function clearChatMessages() {
  const container = document.getElementById('chatMessagesArea');
  container.innerHTML = `
    <div class="chat-bubble assistant">
      <strong>👨‍🏫 Cognitive Technical Mentor:</strong><br>
      History cleared! What technical challenge or interview topic would you like to explore next?
    </div>
  `;
}

function formatMarkdownReply(text) {
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; font-family: var(--font-code); color: var(--accent-cyan); font-size: 0.85em;">$1</code>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');

  return formatted;
}
