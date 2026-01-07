// Atualizar contadores de cards
function updateCardCounts() {
    const todoCount = document.querySelectorAll('#todo-container .fullscreen-card').length;
    const doingCount = document.querySelectorAll('#doing-container .fullscreen-card').length;
    const doneCount = document.querySelectorAll('#done-container .fullscreen-card').length;

    console.log('📊 Contando cards:', {todo: todoCount, doing: doingCount, done: doneCount});

    const todoElement = document.getElementById('todo-count');
    const doingElement = document.getElementById('doing-count');
    const doneElement = document.getElementById('done-count');

    if (todoElement) todoElement.textContent = todoCount;
    if (doingElement) doingElement.textContent = doingCount;
    if (doneElement) doneElement.textContent = doneCount;
    
    console.log('✅ Contadores atualizados');
}

// Gerenciamento de tema
function initTheme() {
    const savedTheme = localStorage.getItem('fullscreen-theme');
    const themeToggle = document.getElementById('themeToggle');
    
    // Se não houver tema salvo, usa escuro como padrão
    if (!savedTheme) {
        localStorage.setItem('fullscreen-theme', 'dark');
    }
    
    // Aplicar tema
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggle.textContent = '☀️';
    } else {
        document.body.classList.remove('light-theme');
        themeToggle.textContent = '🌙';
    }
}

function toggleTheme() {
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');
    
    if (body.classList.contains('light-theme')) {
        // Mudar para escuro
        body.classList.remove('light-theme');
        themeToggle.textContent = '🌙';
        localStorage.setItem('fullscreen-theme', 'dark');
        console.log('🌙 Tema escuro ativado');
    } else {
        // Mudar para claro
        body.classList.add('light-theme');
        themeToggle.textContent = '☀️';
        localStorage.setItem('fullscreen-theme', 'light');
        console.log('☀️ Tema claro ativado');
    }
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        window.location.href = document.getElementById('exitButton').dataset.url;
    }
    if (e.key === 'F5') {
        e.preventDefault();
        location.reload();
    }
});

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tema antes de tudo
    initTheme();
    
    // Adicionar listener ao botão de tema
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Atualizar contadores
    updateCardCounts();
    
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c🖥️  MODO TELA CHEIA - QUADRO KANBAN', 'font-size: 16px; font-weight: bold; color: #667eea;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c⌨️  Atalhos de Teclado:', 'font-size: 14px; font-weight: bold; color: #48bb78;');
    console.log('%c   • ESC - Sair da tela cheia', 'font-size: 13px; color: #666;');
    console.log('%c   • F5  - Atualizar manualmente', 'font-size: 13px; color: #666;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c🔄 Atualização automática: A CADA 60 SEGUNDOS', 'font-size: 14px; font-weight: bold; color: #48bb78;');
    console.log('%c🎨 Tema: ' + (document.body.classList.contains('light-theme') ? 'CLARO ☀️' : 'ESCURO 🌙'), 'font-size: 14px; font-weight: bold; color: #667eea;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
});

