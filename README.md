# Quadro Kanban em Tempo Real

Sistema completo de quadro Kanban com interação em tempo real, desenvolvido com Flask, WebSocket e design moderno.

## 🚀 Funcionalidades

- ✅ **Autenticação completa** - Login, registro e gerenciamento de usuários
- ✅ **Sistema de equipes** - Admin cria equipe e adiciona membros
- ✅ **Quadro Kanban interativo** - Drag-and-drop entre colunas (A Fazer, Fazendo, Concluído)
- ✅ **Tempo real** - Sincronização instantânea via WebSocket (Flask-SocketIO)
- ✅ **Persistência** - Todas as mudanças são salvas automaticamente no banco de dados
- ✅ **Cards coloridos** - 12 cores diferentes para organizar visualmente
- ✅ **Atribuição automática** - Ao arrastar um card, ele é automaticamente atribuído a você
- ✅ **Sistema de histórico** - Timeline completa de todas as ações em cada card
- ✅ **Arquivamento automático** - Cards concluídos há mais de 2 dias são arquivados automaticamente
- ✅ **Relatórios detalhados** - Tempo de conclusão, responsável, métricas completas
- ✅ **Exportação de dados** - Visualize e exporte em JSON, CSV ou PDF
- ✅ **Design moderno** - Interface responsiva com gradientes e animações

## 📋 Requisitos

- Python 3.8+
- pip

## 🔧 Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar a aplicação:**
```bash
python app.py
```

3. **Acessar no navegador:**
```
http://localhost:5000
```

## 👥 Como usar

### 1. Criar conta de Admin
- Acesse a página de registro
- Crie um nome de usuário, senha e nome da equipe
- Você será o administrador da equipe

### 2. Adicionar membros à equipe
- Faça login como admin
- Acesse "Gerenciar Equipe"
- Adicione novos membros com nome de usuário e senha
- Compartilhe as credenciais com sua equipe

### 3. Usar o Quadro Kanban
- Crie cards usando o formulário no topo da página
- **Escolha uma cor** para cada card (12 opções disponíveis)
- Arraste e solte cards entre as colunas (Todo, Doing, Done)
- **Ao arrastar um card, você se torna o responsável automaticamente**
- Todas as mudanças são sincronizadas em tempo real
- Cards na coluna "Concluído" são **arquivados automaticamente após 2 dias**
- Delete cards usando o botão × (apenas cards não arquivados)

### 4. Ver Histórico e Relatórios
- Acesse "Histórico" no menu
- Veja todos os cards arquivados
- **Relatório completo** com:
  - Tempo total de conclusão
  - Quem criou e quem foi o responsável
  - Timeline completa de todas as ações
  - Estatísticas e métricas
  - Data de criação, conclusão e arquivamento

### 5. Exportar dados
- Acesse "Exportar" no menu
- Visualize estatísticas e todos os cards ativos
- Exporte em JSON, CSV ou imprima/salve como PDF

## 🗂️ Estrutura do Projeto

```
quadro_kanban/
├── app.py                 # Aplicação Flask principal
├── models.py              # Modelos do banco de dados
├── requirements.txt       # Dependências Python
├── templates/             # Templates HTML
│   ├── login.html
│   ├── register.html
│   ├── kanban.html
│   ├── team.html
│   └── export.html
└── static/                # Arquivos estáticos
    ├── css/
    │   └── style.css      # Estilos
    └── js/
        └── kanban.js      # JavaScript + WebSocket
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-SocketIO
- **Frontend:** HTML5, CSS3, JavaScript
- **Tempo Real:** Socket.IO
- **Banco de Dados:** SQLite
- **Design:** CSS moderno com gradientes e animações

## 🔒 Segurança

- Senhas hashadas com Werkzeug
- Autenticação com Flask-Login
- Proteção contra XSS em cards
- Sessions seguras

## 📊 Banco de Dados

O sistema cria automaticamente um banco SQLite (`kanban.db`) com as seguintes tabelas:
- **User** - Usuários e administradores
- **Team** - Equipes
- **Card** - Cards do Kanban (com cor, responsável, datas)
- **CardHistory** - Histórico completo de ações em cada card

### Campos importantes dos Cards:
- `color` - Cor do card em hexadecimal
- `assigned_to_id` - Usuário responsável (atribuído ao arrastar)
- `completed_at` - Data/hora de conclusão
- `archived` - Se o card foi arquivado
- `archived_at` - Data/hora de arquivamento

## 🎨 Recursos Visuais

- Design responsivo (mobile-friendly)
- Gradientes modernos (roxo/azul)
- Animações suaves em drag-and-drop
- Feedback visual em tempo real
- Efeitos hover e transições

## 🌐 WebSocket Events

- `connect` - Conecta usuário ao room da equipe
- `create_card` - Cria novo card (com cor)
- `update_card` - Atualiza card (movimento, edição, atribuição automática)
- `delete_card` - Remove card (apenas não arquivados)
- Broadcast automático para toda a equipe

### Sistema de Arquivamento:
- Cards na coluna "Concluído" são verificados a cada acesso
- Se um card está há mais de 2 dias concluído, é arquivado automaticamente
- Cards arquivados vão para a página de "Histórico"
- O histórico mantém registro completo de todas as ações

## 📝 Notas

- A aplicação roda em modo debug por padrão
- Altere `SECRET_KEY` em produção
- O banco de dados é criado automaticamente na primeira execução
- Todas as mudanças no quadro são persistidas imediatamente

## 🤝 Suporte

Para problemas ou dúvidas, verifique:
1. Se todas as dependências foram instaladas
2. Se a porta 5000 está disponível
3. Se o Python 3.8+ está instalado

---

Desenvolvido com ❤️ usando Flask e WebSocket
