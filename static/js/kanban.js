let draggedCard = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    setupCreateCardForm();
    updateCardCounts();
    setupCardClickHandlers();
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
            // Se o formulário tiver um parent_id (data-parent-id), incluir no payload
            const parentId = form.dataset.parentId ? parseInt(form.dataset.parentId) : null;
            const payload = {
                title: title,
                description: description,
                status: 'todo',
                position: 0,
                color: color
            };
            if (parentId) payload.parent_id = parentId;

            fetch('/api/cards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Limpar formulário e recarregar página
                    form.reset();
                    location.reload();
                }
            })
            .catch(error => console.error('Erro ao criar card:', error));
        }
    });
}




// Deletar card
function deleteCard(cardId) {
    if (confirm('Tem certeza que deseja deletar este card?')) {
        fetch(`/api/cards/${cardId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => console.error('Erro ao deletar card:', error));
    }
}

// Configurar clique nos cards para abrir quadro do item
function setupCardClickHandlers() {
    const cards = document.querySelectorAll('.kanban-card');
    cards.forEach(card => {
        // Adicionar evento de clique, mas não em botões especiais
        card.addEventListener('click', function(e) {
            // Não abrir se clicar em botões de ação (delete, editar, etc)
            if (e.target.classList.contains('delete-btn') || e.target.classList.contains('edit-btn')) {
                return;
            }
            
            const cardId = this.dataset.id;
            // Sistema recursivo: sempre abre o quadro Kanban do item
            window.location.href = `/kanban/card/${cardId}`;
        });
        
        // Adicionar estilo de cursor
        card.style.cursor = 'pointer';
    });
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
        const oldContainer = draggedCard.parentElement;
        
        console.log('🔄 Movendo card:', cardId, 'para:', newStatus);
        
        // Adicionar à nova coluna
        this.appendChild(draggedCard);
        updateCardCounts();
        
        // Atualizar no servidor
        fetch(`/api/cards/${cardId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus
            })
        })
        .then(response => {
            console.log('📡 Resposta status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Resposta do servidor:', data);
            if (data.success) {
                console.log('✅ Card atualizado com sucesso!');
            } else {
                console.error('❌ Servidor retornou sucesso=false:', data);
                // Reverter mudança visual
                oldContainer.appendChild(draggedCard);
                updateCardCounts();
                alert('Erro ao mover card. Tente novamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao atualizar card:', error);
            // Reverter mudança visual
            oldContainer.appendChild(draggedCard);
            updateCardCounts();
            alert('Erro ao mover card: ' + error.message);
        });
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
