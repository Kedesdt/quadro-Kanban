# Quadro Kanban - Documentação da Refatoração

## Nova Estrutura do Projeto

```
quadro_kanban/
├── app.py                 # Arquivo principal (Factory Pattern)
├── config.py              # Configurações da aplicação
├── models.py              # Modelos do banco de dados
├── requirements.txt       # Dependências do projeto
├── .env                   # Variáveis de ambiente (não versionar)
├── .env.example           # Template de variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── routes/               # Blueprints organizados por funcionalidade
│   ├── __init__.py
│   ├── auth.py           # Rotas de autenticação
│   ├── kanban.py         # Rotas do quadro Kanban
│   ├── team.py           # Rotas de gerenciamento de equipe
│   ├── export.py         # Rotas de exportação de dados
│   ├── history.py        # Rotas de histórico
│   └── websocket.py      # Eventos WebSocket
├── templates/            # Templates HTML
│   ├── kanban.html
│   ├── login.html
│   ├── register.html
│   ├── team.html
│   ├── export.html
│   └── history.html
├── static/              # Arquivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── kanban.js
└── instance/            # Banco de dados SQLite
```

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
# Flask Configuration
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
FLASK_ENV=development

# Database Configuration
DATABASE_URI=sqlite:///kanban.db

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True

# CORS Configuration
CORS_ALLOWED_ORIGINS=*
```

### 2. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## Mudanças Implementadas

### 1. **Configurações Centralizadas** (`config.py`)

- Carrega variáveis do arquivo `.env` usando `python-dotenv`
- Suporta múltiplos ambientes (development, production)
- Configurações organizadas em classes

### 2. **Separação de Rotas em Blueprints** (`routes/`)

#### `routes/auth.py`

- Rota index (`/`)
- Login (`/login`)
- Registro (`/register`)
- Logout (`/logout`)

#### `routes/kanban.py`

- Visualização do quadro Kanban (`/kanban`)
- Função de arquivamento automático de cards

#### `routes/team.py`

- Gerenciamento de equipe (`/team`)
- Adicionar/remover membros

#### `routes/export.py`

- Exportação de dados (`/export`)
- API JSON de exportação (`/api/export/json`)

#### `routes/history.py`

- Histórico de cards arquivados (`/history`)
- Estatísticas de produtividade

#### `routes/websocket.py`

- Eventos WebSocket para tempo real
- `connect`, `disconnect`, `create_card`, `update_card`, `delete_card`

### 3. **Factory Pattern** (`app.py`)

- Função `create_app()` para criar a aplicação
- Facilita testes e múltiplas instâncias
- Registro centralizado de blueprints e extensões

### 4. **Segurança**

- Arquivo `.env` adicionado ao `.gitignore`
- Template `.env.example` para compartilhar estrutura
- SECRET_KEY configurável por ambiente

## Benefícios da Refatoração

1. **Manutenibilidade**: Código organizado por funcionalidade
2. **Escalabilidade**: Fácil adicionar novas rotas e módulos
3. **Segurança**: Variáveis sensíveis em arquivo `.env`
4. **Flexibilidade**: Configurações por ambiente
5. **Testabilidade**: Factory pattern facilita testes
6. **Colaboração**: Estrutura clara para trabalho em equipe

## Próximos Passos Recomendados

1. **Testes Unitários**: Criar pasta `tests/` com testes para cada blueprint
2. **Validação de Dados**: Adicionar validação com Flask-WTF ou Marshmallow
3. **Logging**: Implementar sistema de logs estruturado
4. **Cache**: Adicionar Redis para sessões e cache
5. **Migração de Banco**: Usar Flask-Migrate para gerenciar schema
6. **API RESTful**: Expandir endpoints de API com versionamento
7. **Documentação de API**: Swagger/OpenAPI
8. **Docker**: Containerizar a aplicação

## Migração do Código Antigo

Se você já tinha um banco de dados, ele continuará funcionando normalmente. A estrutura dos modelos não foi alterada, apenas a organização do código.

## Troubleshooting

### Erro: "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Erro: "Blueprint name collision"

Certifique-se de que cada blueprint tem um nome único no primeiro argumento.

### Banco de dados não é criado

Execute uma vez com `python app.py` - o banco será criado automaticamente.
