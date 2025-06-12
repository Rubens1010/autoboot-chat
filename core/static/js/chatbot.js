const chatArea = document.getElementById('chat-area');
const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question-input');
const loading = document.getElementById('loading');

function addBubble(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + sender;
    bubble.textContent = text;
    chatArea.appendChild(bubble);
    chatArea.scrollTop = chatArea.scrollHeight;
}

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const question = questionInput.value.trim();
    if (!question) return;
    addBubble(question, 'user');
    questionInput.value = '';
    loading.style.display = 'block';
    fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    })
    .then(res => res.json())
    .then(data => {
        loading.style.display = 'none';
        if (data.answer) {
            addBubble(data.answer, 'bot');
        } else {
            addBubble('Erro: ' + (data.error || 'Resposta inválida.'), 'bot');
        }
    })
    .catch(() => {
        loading.style.display = 'none';
        addBubble('Erro ao conectar ao servidor.', 'bot');
    });
});

// Tema escuro/claro (opcional)
// Para alternar, adicione/remova a classe 'dark' no body 