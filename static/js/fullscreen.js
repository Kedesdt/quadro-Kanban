// Atualizar contadores de cards
function updateCardCounts() {
    const todoCount = document.querySelectorAll('#todo-container .fullscreen-card').length;
    const doingCount = document.querySelectorAll('#doing-container .fullscreen-card').length;
    const doneCount = document.querySelectorAll('#done-container .fullscreen-card').length;

    document.getElementById('todo-count').textContent = todoCount;
    document.getElementById('doing-count').textContent = doingCount;
    document.getElementById('done-count').textContent = doneCount;
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

    console.log('➕ Adicionando card ao quadro:', data);
    const container = document.getElementById(`${data.status}-container`);
    
    if (!container) {
        console.error('❌ Container não encontrado para status:', data.status);
        return;
    }
    
    const cardHtml = `
        <div class="fullscreen-card new-card" data-card-id="${data.id}" style="border-left: 5px solid ${data.color}; background: linear-gradient(135deg, ${data.color}15, white);">
            <div class="fullscreen-card-header">
                <h4>${data.title}</h4>
            </div>
            ${data.description ? `<p>${data.description}</p>` : ''}
            <div class="fullscreen-card-footer">
                <small>👤 ${data.creator}</small>
                ${data.assigned_to ? `<span class="fullscreen-assigned-badge" style="background: ${data.color};">✓ ${data.assigned_to}</span>` : ''}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', cardHtml);
    
    // Remover a classe new-card após a animação
    setTimeout(() => {
        const newCard = document.querySelector(`[data-card-id="${data.id}"]`);
        if (newCard) {
            newCard.classList.remove('new-card');
        }
    }, 600);
    
    updateCardCounts();
    showRefreshIndicator('Novo card criado');
    console.log('✅ Card adicionado com sucesso');
}

// Atualizar card existente no quadro com animação
function updateCardOnBoard(data) {
    console.log('🔄 Atualizando card no quadro:', data);
    const oldCard = document.querySelector(`[data-card-id="${data.id}"]`);
    
    if (oldCard) {
        console.log('📍 Card encontrado, processando atualização...');
        const oldContainer = oldCard.closest('.fullscreen-card-container');
        const newContainer = document.getElementById(`${data.status}-container`);
        
        if (!newContainer) {
            console.error('❌ Container não encontrado para status:', data.status);
            return;
        }
        
        // Verificar se mudou de coluna
        if (oldContainer.id !== newContainer.id) {
            console.log(`↔️ Movendo card de ${oldContainer.id} para ${newContainer.id}`);
            const statusOrder = ['todo', 'doing', 'done'];
            const oldStatus = oldContainer.id.replace('-container', '');
            const newStatus = data.status;
            
            const oldIndex = statusOrder.indexOf(oldStatus);
            const newIndex = statusOrder.indexOf(newStatus);
            
            const animationClass = newIndex > oldIndex ? 'moving-right' : 'moving-left';
            console.log(`🎬 Aplicando animação: ${animationClass}`);
            
            // Remover todas as classes de animação antigas
            oldCard.classList.remove('moving-left', 'moving-right', 'new-card', 'removing');
            
            // Forçar reflow para resetar a animação
            void oldCard.offsetWidth;
            
            // Aplicar animação de saída
            oldCard.classList.add(animationClass);
            
            // Aguardar animação e então mover o card
            setTimeout(() => {
                oldCard.remove();
                
                // Adicionar na nova posição com animação de entrada suave
                const cardHtml = `
                    <div class="fullscreen-card arrived" data-card-id="${data.id}" style="border-left: 5px solid ${data.color}; background: linear-gradient(135deg, ${data.color}15, white);">
                        <div class="fullscreen-card-header">
                            <h4>${data.title}</h4>
                        </div>
                        ${data.description ? `<p>${data.description}</p>` : ''}
                        <div class="fullscreen-card-footer">
                            <small>👤 ${data.creator || 'Usuário'}</small>
                            ${data.assigned_to ? `<span class="fullscreen-assigned-badge" style="background: ${data.color};">✓ ${data.assigned_to}</span>` : ''}
                        </div>
                    </div>
                `;
                
                newContainer.insertAdjacentHTML('beforeend', cardHtml);
                
                // Remover a classe arrived após a animação
                setTimeout(() => {
                    const newCard = document.querySelector(`[data-card-id="${data.id}"]`);
                    if (newCard) {
                        newCard.classList.remove('arrived');
                    }
                }, 400);
                
                updateCardCounts();
                showRefreshIndicator('Card movido');
                console.log('✅ Card movido com sucesso');
            }, 500);
        } else {
            console.log('📝 Atualizando conteúdo do card (mesma coluna)');
            // Apenas atualizar o conteúdo
            oldCard.querySelector('h4').textContent = data.title;
            const description = oldCard.querySelector('p');
            if (data.description && description) {
                description.textContent = data.description;
            }
            
            // Atualizar assigned_to
            const footer = oldCard.querySelector('.fullscreen-card-footer');
            footer.innerHTML = `
                <small>👤 ${data.creator || 'Usuário'}</small>
                ${data.assigned_to ? `<span class="fullscreen-assigned-badge" style="background: ${data.color};">✓ ${data.assigned_to}</span>` : ''}
            `;
            
            // Efeito visual de atualização
            oldCard.classList.add('new-card');
            setTimeout(() => {
                oldCard.classList.remove('new-card');
            }, 600);
            
            showRefreshIndicator('Card atualizado');
            console.log('✅ Card atualizado com sucesso');
        }
    } else {
        // Remover todas as classes de animação antigas
        card.classList.remove('moving-left', 'moving-right', 'new-card');
        
        // Forçar reflow
        void card.offsetWidth;
        
        console.log('⚠️ Card não encontrado, adicionando como novo');
        addCardToBoard(data);
    }
}

// Remover card do quadro com animação
function removeCardFromBoard(cardId) {
    const card = document.querySelector(`[data-card-id="${cardId}"]`);
    if (card) {
        card.classList.add('removing');
        
        setTimeout(() => {
            card.remove();
            updateCardCounts();
            showRefreshIndicator('Card removido');
        }, 300);
    }
}

// Mostrar indicador de atualização
function showRefreshIndicator(message = 'Atualizando...') {
    const indicator = document.getElementById('refreshIndicator');
    indicator.textContent = `🔄 ${message}`;
    indicator.classList.add('active');
    setTimeout(() => {
        indicator.classList.remove('active');
    }, 1500);
}

// Atualizar status de conexão
function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        status.classList.remove('disconnected');
        statusText.textContent = 'Conectado';
    } else {
        status.classList.add('disconnected');
        statusText.textContent = 'Desconectado';
    }
}

// Socket.IO Events
socket.on('connect', function() {
    console.log('✅ Conectado ao servidor via WebSocket');
    updateConnectionStatus(true);
    showRefreshIndicator('Conectado ao servidor');
});

socket.on('disconnect', function() {
    console.log('❌ Desconectado do servidor');
    updateConnectionStatus(false);
});

socket.on('reconnect', function() {
    console.log('🔄 Reconectado ao servidor');
    updateConnectionStatus(true);
    showRefreshIndicator('Reconectado');
    setTimeout(() => location.reload(), 1000);
});

socket.on('card_created', function(data) {
    console.log('📝 Novo card criado:', data);
    addCardToBoard(data);
});

socket.on('card_updated', function(data) {
    console.log('🔄 Card atualizado:', data);
    updateCardOnBoard(data);
});

socket.on('card_deleted', function(data) {
    console.log('🗑️ Card deletado:', data);
    removeCardFromBoard(data.id);
});

socket.on('user_connected', function(data) {
    console.log('👤 Usuário conectado:', data.username);
});

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
