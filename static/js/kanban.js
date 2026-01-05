// Conectar ao WebSocket usando o caminho configurado
const socket = io({
    path: window.SOCKET_PATH || '/socket.io/',
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 10
});

let draggedCard = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    setupCreateCardForm();
    updateCardCounts();
});

// Socket.IO Events
socket.on('connect', function() {
    console.log('Conectado ao servidor');
});

socket.on('card_created', function(data) {
    addCardToBoard(data);
    updateCardCounts();
});

socket.on('card_updated', function(data) {
    updateCardOnBoard(data);
    updateCardCounts();
});

socket.on('card_deleted', function(data) {
    removeCardFromBoard(data.id);
    updateCardCounts();
});

socket.on('user_connected', function(data) {
    console.log('Usuário conectado:', data.username);
});

// Formulário de criação de cards
function setupCreateCardForm() {
    const form = document.getElementById('createCardForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const title = document.getElementById('cardTitle').value.trim();
        const description = document.getElementById('cardDescription').value.trim();
        const color = document.getElementById('cardColor').value;
        
        if (title) {
            socket.emit('create_card', {
                title: title,
                description: description,
                status: 'todo',
                position: 0,
                color: color
            });
            
            // Limpar formulário
            form.reset();
        }
    });
}

// Adicionar card ao quadro
function addCardToBoard(cardData) {
    const container = document.getElementById(`${cardData.status}-container`);
    
    // Verificar se o card já existe
    if (document.querySelector(`[data-id="${cardData.id}"]`)) {
        return;
    }
    
    const cardElement = createCardElement(cardData);
    container.appendChild(cardElement);
}

// Criar elemento de card
function createCardElement(cardData) {
    const card = document.createElement('div');
    card.className = 'kanban-card';
    card.draggable = true;
    card.dataset.id = cardData.id;
    card.style.borderLeft = `5px solid ${cardData.color}`;
    card.style.background = `linear-gradient(135deg, ${cardData.color}15, white)`;
    
    let assignedBadge = '';
    if (cardData.assigned_to) {
        assignedBadge = `<span class="assigned-badge" style="background: ${cardData.color};">👤 ${escapeHtml(cardData.assigned_to)}</span>`;
    }
    
    card.innerHTML = `
        <div class="card-header">
            <h4>${escapeHtml(cardData.title)}</h4>
            <button class="delete-btn" onclick="deleteCard(${cardData.id})">×</button>
        </div>
        ${cardData.description ? `<p>${escapeHtml(cardData.description)}</p>` : ''}
        <div class="card-footer">
            <small>Criado: ${escapeHtml(cardData.creator)}</small>
            ${assignedBadge}
        </div>
    `;
    
    // Adicionar eventos de drag
    setupCardDragEvents(card);
    
    return card;
}

// Atualizar card no quadro
function updateCardOnBoard(cardData) {
    const cardElement = document.querySelector(`[data-id="${cardData.id}"]`);
    
    if (cardElement) {
        // Se o status mudou, mover para a nova coluna
        const currentContainer = cardElement.parentElement;
        const newContainer = document.getElementById(`${cardData.status}-container`);
        
        if (currentContainer !== newContainer) {
            newContainer.appendChild(cardElement);
        }
        
        // Atualizar conteúdo
        const titleElement = cardElement.querySelector('.card-header h4');
        if (titleElement) {
            titleElement.textContent = cardData.title;
        }
        
        // Atualizar badge de responsável
        const footer = cardElement.querySelector('.card-footer');
        if (footer && cardData.assigned_to) {
            const existingBadge = footer.querySelector('.assigned-badge');
            if (existingBadge) {
                existingBadge.textContent = `👤 ${cardData.assigned_to}`;
                existingBadge.style.background = cardData.color;
            } else {
                const badge = document.createElement('span');
                badge.className = 'assigned-badge';
                badge.style.background = cardData.color;
                badge.textContent = `👤 ${cardData.assigned_to}`;
                footer.appendChild(badge);
            }
        }
    }
}

// Remover card do quadro
function removeCardFromBoard(cardId) {
    const cardElement = document.querySelector(`[data-id="${cardId}"]`);
    if (cardElement) {
        cardElement.remove();
    }
}

// Deletar card
function deleteCard(cardId) {
    if (confirm('Tem certeza que deseja deletar este card?')) {
        socket.emit('delete_card', { id: cardId });
    }
}

// Drag and Drop
function initializeDragAndDrop() {
    const cards = document.querySelectorAll('.kanban-card');
    cards.forEach(card => setupCardDragEvents(card));
    
    const containers = document.querySelectorAll('.card-container');
    containers.forEach(container => setupContainerDragEvents(container));
}

function setupCardDragEvents(card) {
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
}

function setupContainerDragEvents(container) {
    container.addEventListener('dragover', handleDragOver);
    container.addEventListener('drop', handleDrop);
    container.addEventListener('dragenter', handleDragEnter);
    container.addEventListener('dragleave', handleDragLeave);
}

function handleDragStart(e) {
    draggedCard = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Remover classe de todos os containers
    document.querySelectorAll('.card-container').forEach(container => {
        container.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    if (e.target === this) {
        this.classList.remove('drag-over');
    }
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    this.classList.remove('drag-over');
    
    if (draggedCard) {
        const newStatus = this.closest('.kanban-column').dataset.status;
        const cardId = parseInt(draggedCard.dataset.id);
        
        // Adicionar à nova coluna
        this.appendChild(draggedCard);
        
        // Atualizar no servidor
        socket.emit('update_card', {
            id: cardId,
            status: newStatus
        });
        
        updateCardCounts();
    }
    
    return false;
}

// Atualizar contadores de cards
function updateCardCounts() {
    document.querySelectorAll('.kanban-column').forEach(column => {
        const count = column.querySelectorAll('.kanban-card').length;
        const countElement = column.querySelector('.card-count');
        if (countElement) {
            countElement.textContent = count;
        }
    });
}

// Escapar HTML para prevenir XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
