# Funcionalidade: Editar e Atribuir Cards

## Descrição
Agora os administradores e membros do time podem editar cards existentes clicando diretamente neles no quadro Kanban.

## Como Usar

### Para Todos os Usuários:
1. **Editar um Card**: Clique em qualquer card no quadro Kanban
2. Você será redirecionado para a página de edição
3. Pode modificar:
   - Título do card
   - Descrição
   - Cor do card
4. Veja um preview em tempo real das suas alterações
5. Clique em "💾 Salvar Alterações" para confirmar

### Para Administradores:
Além das funcionalidades acima, administradores podem:
- **Atribuir cards** a membros específicos do time
- Ver quem está atribuído a cada card
- O sistema registra todas as atribuições no histórico

## Mudanças Implementadas

### Arquivos Criados:
- `templates/edit_card.html` - Template para editar cards

### Arquivos Modificados:
- `routes/kanban.py`:
  - Adicionada rota `/kanban/card/<id>/edit` (GET e POST)
  - Permite edição de título, descrição, cor e atribuição
  - Registra mudanças de atribuição no histórico

- `static/js/kanban.js`:
  - Adicionada função `setupCardClickHandlers()`
  - Cards agora são clicáveis (exceto o botão de deletar)
  - Redirecionam para a página de edição

- `static/css/style.css`:
  - Melhorado o cursor dos cards (pointer em vez de move)
  - Efeito hover mais destacado
  - Efeito de clique ativo

- `templates/kanban.html`:
  - Adicionado tooltip "Clique para editar" em todos os cards

## Recursos da Página de Edição:
- ✏️ Preview em tempo real das alterações
- 🎨 Seletor de cores visual
- 👤 Atribuição de membros (apenas admin)
- 📋 Informações sobre status atual
- 💾 Salvamento com validação
- ❌ Cancelamento fácil

## Permissões:
- **Todos os membros**: podem editar título, descrição e cor de qualquer card do time
- **Apenas Administradores**: podem atribuir cards a membros específicos

## Histórico:
Todas as alterações de atribuição são registradas no histórico do card para auditoria.
