// Script para exibir subitens no tooltip ao passar o mouse em cards no fullscreen

document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.fullscreen-card[data-children]');
    
    cards.forEach(card => {
        try {
            const childrenData = JSON.parse(card.dataset.children);
            
            if (childrenData && childrenData.length > 0) {
                const tooltip = generateTooltip(childrenData);
                // Criar elemento de tooltip
                const tooltipEl = document.createElement('div');
                tooltipEl.className = 'card-tooltip';
                tooltipEl.textContent = tooltip;
                card.appendChild(tooltipEl);
                
                card.style.cursor = 'pointer';
                
                // Events de hover
                card.addEventListener('mouseenter', function() {
                    tooltipEl.style.display = 'block';
                });
                
                card.addEventListener('mouseleave', function() {
                    tooltipEl.style.display = 'none';
                });
            }
        } catch (e) {
            console.error('Erro ao parsear subitens:', e);
        }
    });
    
    // Adicionar clique para navegar ao item
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const cardId = this.dataset.cardId;
            if (cardId) {
                window.location.href = `/kanban/card/${cardId}`;
            }
        });
    });
});

// Gera o tooltip formatado com os subitens
function generateTooltip(children) {
    if (!children || children.length === 0) {
        return '';
    }
    
    // Contar status
    const done = children.filter(c => c.status === 'done').length;
    const doing = children.filter(c => c.status === 'doing').length;
    const todo = children.filter(c => c.status === 'todo').length;
    const percentage = Math.round((done / children.length) * 100);
    
    // Mapear ícones de status
    const statusIcons = {
        'done': '✅',
        'doing': '⚡',
        'todo': '📋'
    };
    
    const statusLabels = {
        'done': 'feito',
        'doing': 'fazendo',
        'todo': 'a fazer'
    };
    
    let tooltip = percentage + '% concluído\n\n';
    
    // Listar subitens agrupados por status: done, doing, todo
    const statuses = ['done', 'doing', 'todo'];
    
    statuses.forEach(status => {
        const itemsWithStatus = children.filter(c => c.status === status);
        if (itemsWithStatus.length > 0) {
            itemsWithStatus.forEach(child => {
                const icon = statusIcons[status];
                const label = statusLabels[status];
                tooltip += `${icon} ${label} → ${child.title}\n`;
            });
            tooltip += '\n';
        }
    });
    
    return tooltip.trim();
}
