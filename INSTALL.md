# Guia de Instalação - Quadro Kanban Refatorado

## Passo a Passo para Rodar o Projeto

### 1. Clone ou acesse o diretório do projeto

```bash
cd c:\Users\kdtorres\Documents\Programacao\quadro_kanban
```

### 2. (Opcional) Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

O arquivo `.env` já foi criado com valores padrão. Se necessário, edite:

```bash
notepad .env
```

**IMPORTANTE**: Antes de colocar em produção, altere a `SECRET_KEY`!

### 5. Execute a aplicação

```bash
python app.py
```

### 6. Acesse no navegador

```
http://localhost:5000
```

## Verificação de Instalação

Teste se todas as dependências foram instaladas:

```bash
pip list
```

Deve incluir:

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-SocketIO
- python-dotenv
- Werkzeug

## Comandos Úteis

### Atualizar dependências

```bash
pip install --upgrade -r requirements.txt
```

### Verificar versão do Python

```bash
python --version
```

Requer Python 3.7+

### Reinstalar tudo do zero

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Estrutura de Arquivos Criados

Arquivos novos criados na refatoração:

- ✅ `.env` - Variáveis de ambiente
- ✅ `.env.example` - Template de variáveis
- ✅ `config.py` - Configurações centralizadas
- ✅ `routes/__init__.py` - Pacote de rotas
- ✅ `routes/auth.py` - Autenticação
- ✅ `routes/kanban.py` - Quadro Kanban
- ✅ `routes/team.py` - Gerenciamento de equipe
- ✅ `routes/export.py` - Exportação
- ✅ `routes/history.py` - Histórico
- ✅ `routes/websocket.py` - WebSocket
- ✅ `REFACTORING.md` - Documentação da refatoração

Arquivos modificados:

- ✅ `app.py` - Refatorado para usar Factory Pattern
- ✅ `requirements.txt` - Adicionado python-dotenv
- ✅ `.gitignore` - Adicionado .env

## Próximos Passos

Após a instalação, você pode:

1. Criar sua primeira conta através de `/register`
2. Fazer login através de `/login`
3. Acessar o quadro Kanban em `/kanban`
4. Gerenciar sua equipe em `/team` (apenas admin)

## Problemas Comuns

### Erro: "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Erro: "Port 5000 already in use"

Edite o arquivo `.env` e mude a porta:

```
PORT=5001
```

### Erro: "Database is locked"

Feche todas as instâncias do aplicativo e tente novamente.

### WebSocket não funciona

Certifique-se de que a porta está aberta e que CORS está configurado corretamente no `.env`.
