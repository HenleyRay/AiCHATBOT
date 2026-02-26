// Chat functionality for Mental Health Chatbot

const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const resetButton = document.getElementById('reset-button');
const quickActionButtons = document.querySelectorAll('[data-quick-message]');

// Wellness Tips Data
const wellnessTips = [
    "🌟 Take a 5-minute break every hour. Step away from your screen, stretch, and breathe deeply.",
    "💧 Drink water regularly throughout the day. Staying hydrated improves mood and focus.",
    "🚶 Go for a short walk today, even if it's just around your home. Movement helps reduce anxiety.",
    "😴 Aim for 7-9 hours of sleep tonight. Sleep is essential for mental health and recovery.",
    "📱 Put your phone away 30 minutes before bed. Better sleep starts with less screen time.",
    "🎵 Listen to your favorite music or a calming playlist. Music is a powerful mood booster.",
    "☕ Practice a morning routine that calms you. Start your day with intention and mindfulness."
];

let currentTipIndex = 0;

// Initialize wellness carousel
function initWellnessCarousel() {
    const prevBtn = document.getElementById('prev-tip');
    const nextBtn = document.getElementById('next-tip');
    
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => showPreviousTip());
        nextBtn.addEventListener('click', () => showNextTip());
        
        // Display first tip
        displayTip(0);
        
        // Auto-rotate tips every 8 seconds
        setInterval(() => {
            showNextTip();
        }, 8000);
    }
}

function displayTip(index) {
    const tipElement = document.getElementById('wellness-tip');
    const counterElement = document.getElementById('tip-counter');
    
    if (tipElement) {
        tipElement.textContent = wellnessTips[index];
        counterElement.textContent = `${index + 1} / ${wellnessTips.length}`;
    }
}

function showNextTip() {
    currentTipIndex = (currentTipIndex + 1) % wellnessTips.length;
    displayTip(currentTipIndex);
}

function showPreviousTip() {
    currentTipIndex = (currentTipIndex - 1 + wellnessTips.length) % wellnessTips.length;
    displayTip(currentTipIndex);
}

// Add user message to chat
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    const safe = escapeHtml(message).replace(/\n/g, '<br>');
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${safe}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message, isCrisis = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const crisisClass = isCrisis ? 'crisis-message' : '';
    
    // Convert newlines to <br> and format the message
    const formattedMessage = formatMessage(message);
    
    messageDiv.innerHTML = `
        <div class="message-content ${crisisClass}">
            ${formattedMessage}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format message with markdown-like formatting
function formatMessage(text) {
    // Convert newlines to <br>
    let formatted = escapeHtml(text).replace(/\n/g, '<br>');
    
    // Convert **text** to <strong>text</strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *text* to <em>text</em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return formatted;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typing-indicator';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to backend
async function sendMessage(message) {
    try {
        showTypingIndicator();
        disableInput();
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        removeTypingIndicator();
        
        if (data.success) {
            addBotMessage(data.response, data.is_crisis);
            
            // Show suggestions if available
            if (data.suggestions && data.suggestions.length > 0) {
                const suggestionsText = 'Suggestions:\n' + data.suggestions.map(s => `• ${s}`).join('\n');
                addBotMessage(suggestionsText);
            }
            
            // Show interventions if available
            if (data.interventions) {
                addBotMessage(data.interventions);
            }
        } else {
            addBotMessage('I apologize, but I encountered an error. Please try again.');
        }
    } catch (error) {
        removeTypingIndicator();
        console.error('Error:', error);
        addBotMessage('I\'m having trouble connecting right now. Please try again in a moment.');
    } finally {
        enableInput();
        userInput.focus();
    }
}

// Disable input during processing
function disableInput() {
    userInput.disabled = true;
    sendButton.disabled = true;
}

// Enable input
function enableInput() {
    userInput.disabled = false;
    sendButton.disabled = false;
}

// Reset conversation
async function resetConversation() {
    if (!confirm('Are you sure you want to reset the conversation? This will clear all chat history.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear chat messages
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        <p>Welcome. You can type a message (even one sentence is enough), or use a quick option below.</p>
                        <ul>
                            <li><strong>Support chat</strong> for what you’re going through</li>
                            <li><strong>PHQ-9 screening</strong> (type “screening” or click “Start screening”)</li>
                            <li><strong>Practical coping steps</strong> you can try today</li>
                        </ul>
                        <p class="hint">Tip: Press <strong>Enter</strong> to send • <strong>Shift + Enter</strong> for a new line</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Error resetting conversation. Please refresh the page.');
    }
}

function autosizeTextarea() {
    if (!userInput) return;
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
}

// Event listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message) {
        addUserMessage(message);
        sendMessage(message);
        userInput.value = '';
        autosizeTextarea();
    }
});

resetButton.addEventListener('click', resetConversation);

// Allow Enter key to send (but Shift+Enter for new line)
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

userInput.addEventListener('input', autosizeTextarea);

// Quick action chips
quickActionButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
        const msg = btn.getAttribute('data-quick-message');
        if (!msg) return;
        userInput.value = msg;
        autosizeTextarea();
        userInput.focus();
        chatForm.dispatchEvent(new Event('submit'));
    });
});

// Philippine Time Clock (PHT = UTC+8)
function updatePhilippineTime() {
    const phTimeElement = document.getElementById('ph-time');
    if (phTimeElement) {
        // Get current time in Philippine timezone (UTC+8)
        const now = new Date();
        const phTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Manila' }));
        
        // Format time as HH:MM:SS
        const hours = String(phTime.getHours()).padStart(2, '0');
        const minutes = String(phTime.getMinutes()).padStart(2, '0');
        const seconds = String(phTime.getSeconds()).padStart(2, '0');
        
        phTimeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
}

// Update time immediately and then every second
updatePhilippineTime();
setInterval(updatePhilippineTime, 1000);

// Gather chat messages as plain text
function gatherChatText() {
    const container = document.getElementById('chat-messages');
    if (!container) return '';
    const messages = container.querySelectorAll('.message');
    const lines = [];
    messages.forEach(msg => {
        const contentEl = msg.querySelector('.message-content');
        const text = contentEl ? contentEl.innerText.trim() : '';
        let role = 'Bot';
        if (msg.classList.contains('user-message')) role = 'User';
        // Normalize newlines
        const normalized = text.replace(/\u00A0/g, ' ');
        lines.push(`[${role}] ${normalized}`);
    });
    return lines.join('\n\n');
}

// Export chat as TXT file
function exportChatAsTXT() {
    const text = gatherChatText();
    if (!text) {
        alert('No chat messages to export.');
        return;
    }
    const header = `Mental Health Chat Export - ${new Date().toLocaleString()}\n\n`;
    const blob = new Blob([header + text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0,19)}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

// Export chat as printable PDF via print window
function exportChatAsPDF() {
    const container = document.getElementById('chat-messages');
    if (!container || container.children.length === 0) {
        alert('No chat messages to export.');
        return;
    }
    const printable = container.cloneNode(true);
    // Convert message structure into simple printable markup
    printable.querySelectorAll('.message').forEach(node => {
        const role = node.classList.contains('user-message') ? 'User' : 'Bot';
        const contentEl = node.querySelector('.message-content');
        const text = contentEl ? contentEl.innerText : '';
        node.innerHTML = `<div style="margin-bottom:12px;"><strong>${role}:</strong><div style="white-space:pre-wrap;margin-top:6px;">${escapeHtml(text)}</div></div>`;
    });

    const win = window.open('', '_blank');
    if (!win) {
        alert('Unable to open print window. Please allow pop-ups for this site.');
        return;
    }
    const title = `Mental Health Chat Export - ${new Date().toLocaleString()}`;
    win.document.write(`<!doctype html><html><head><title>${title}</title><meta charset="utf-8"><style>body{font-family:Arial,Helvetica,sans-serif;padding:20px;color:#111} strong{color:#0f172a}</style></head><body><h2>${title}</h2>`);
    win.document.body.appendChild(printable);
    win.document.write('</body></html>');
    win.document.close();
    // Give the window a moment to render, then open print dialog
    setTimeout(() => {
        try { win.print(); } catch (e) { console.error(e); }
    }, 300);
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
    autosizeTextarea();
    initWellnessCarousel();

    const btnTxt = document.getElementById('export-txt');
    const btnPdf = document.getElementById('export-pdf');
    if (btnTxt) btnTxt.addEventListener('click', exportChatAsTXT);
    if (btnPdf) btnPdf.addEventListener('click', exportChatAsPDF);
});

/* Breathing exercise logic */
let breathInterval = null;
let breathPhase = 0; // 0=idle, 1=inhale, 2=exhale
let breathRunning = false;

function openBreathModal() {
    const modal = document.getElementById('breath-modal');
    if (!modal) return;
    modal.setAttribute('aria-hidden', 'false');
}

function closeBreathModal() {
    const modal = document.getElementById('breath-modal');
    if (!modal) return;
    modal.setAttribute('aria-hidden', 'true');
    stopBreathing();
}

function startBreathing() {
    if (breathRunning) return;
    breathRunning = true;
    breathPhase = 1; // start with inhale
    const circle = document.getElementById('breath-circle');
    const instr = document.getElementById('breath-instruction');
    if (!circle || !instr) return;

    const inhaleSec = 4;
    const exhaleSec = 6;

    function step() {
        if (breathPhase === 1) {
            // inhale
            circle.classList.remove('exhale');
            circle.classList.add('inhale');
            instr.textContent = `Inhale (${inhaleSec}s)`;
            // after inhale, switch to exhale
            breathPhase = 2;
            clearInterval(breathInterval);
            breathInterval = setTimeout(step, inhaleSec * 1000);
        } else if (breathPhase === 2) {
            // exhale
            circle.classList.remove('inhale');
            circle.classList.add('exhale');
            instr.textContent = `Exhale (${exhaleSec}s)`;
            breathPhase = 1;
            clearInterval(breathInterval);
            breathInterval = setTimeout(step, exhaleSec * 1000);
        }
    }

    // kick off
    step();
}

function stopBreathing() {
    breathRunning = false;
    breathPhase = 0;
    if (breathInterval) {
        clearTimeout(breathInterval);
        breathInterval = null;
    }
    const circle = document.getElementById('breath-circle');
    const instr = document.getElementById('breath-instruction');
    if (circle) {
        circle.classList.remove('inhale', 'exhale');
    }
    if (instr) instr.textContent = 'Press start to begin a 2-minute breathing exercise.';
}

// Bind breathing UI
document.addEventListener('click', (e) => {
    const target = e.target;
    if (!target) return;
    if (target.id === 'breath-btn') {
        openBreathModal();
    }
    if (target.id === 'close-breath') {
        closeBreathModal();
    }
    if (target.id === 'start-breath') {
        startBreathing();
    }
    if (target.id === 'stop-breath') {
        stopBreathing();
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeBreathModal();
});

