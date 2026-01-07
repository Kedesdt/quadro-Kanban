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
    updateCardCounts();
    
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c🖥️  MODO TELA CHEIA - QUADRO KANBAN', 'font-size: 16px; font-weight: bold; color: #667eea;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c⌨️  Atalhos de Teclado:', 'font-size: 14px; font-weight: bold; color: #48bb78;');
    console.log('%c   • ESC - Sair da tela cheia', 'font-size: 13px; color: #666;');
    console.log('%c   • F5  - Atualizar manualmente', 'font-size: 13px; color: #666;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
    console.log('%c🔄 Atualização automática: A CADA 60 SEGUNDOS', 'font-size: 14px; font-weight: bold; color: #48bb78;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #667eea;');
});

