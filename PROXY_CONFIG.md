# Configuração do Proxy Reverso para WebSocket

Este documento descreve como configurar o proxy reverso para permitir que o WebSocket funcione corretamente.

## Como funciona

O servidor Flask envia o caminho do Socket.IO através da variável `socket_path` no template HTML:
- Valor padrão: `/socket.io`
- O proxy reverso pode modificar este valor conforme necessário

## Configuração do Nginx

### Exemplo 1: Socket.IO no mesmo caminho
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Configuração específica para WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Exemplo 2: Socket.IO em um subcaminho (ex: /app/socket.io)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /app/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Modificar o caminho do socket no HTML
        sub_filter '/socket.io' '/app/socket.io';
        sub_filter_once off;
        sub_filter_types text/html;
    }

    # Configuração específica para WebSocket no subcaminho
    location /app/socket.io/ {
        proxy_pass http://localhost:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuração do Apache

### Exemplo 1: Socket.IO no mesmo caminho
```apache
<VirtualHost *:80>
    ServerName seu-dominio.com

    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    # Configuração para WebSocket
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule /(.*)           ws://localhost:5000/$1 [P,L]
    RewriteCond %{HTTP:Upgrade} !=websocket [NC]
    RewriteRule /(.*)           http://localhost:5000/$1 [P,L]

    ProxyPass /socket.io/ http://localhost:5000/socket.io/
    ProxyPassReverse /socket.io/ http://localhost:5000/socket.io/
</VirtualHost>
```

### Exemplo 2: Socket.IO em um subcaminho
```apache
<VirtualHost *:80>
    ServerName seu-dominio.com

    # Módulos necessários
    LoadModule proxy_module modules/mod_proxy.so
    LoadModule proxy_http_module modules/mod_proxy_http.so
    LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
    LoadModule substitute_module modules/mod_substitute.so

    ProxyPreserveHost On
    
    # Modificar o caminho do socket no HTML
    AddOutputFilterByType SUBSTITUTE text/html
    Substitute "s|/socket.io|/app/socket.io|ni"

    ProxyPass /app/ http://localhost:5000/
    ProxyPassReverse /app/ http://localhost:5000/

    # WebSocket no subcaminho
    ProxyPass /app/socket.io/ ws://localhost:5000/socket.io/
    ProxyPassReverse /app/socket.io/ ws://localhost:5000/socket.io/
</VirtualHost>
```

## Testando a Configuração

1. **Verificar se o WebSocket está conectando:**
   - Abra o Console do navegador (F12)
   - Procure por mensagens como "✅ Conectado ao servidor via WebSocket"

2. **Verificar a URL do WebSocket:**
   - No Console, digite: `window.SOCKET_PATH`
   - Deve retornar o caminho correto (ex: `/socket.io` ou `/app/socket.io`)

3. **Testar a funcionalidade:**
   - Crie um novo card
   - Verifique se ele aparece em tempo real em outra aba/navegador
   - Mova um card entre colunas e verifique a sincronização

## Modificando o Caminho do Socket

Se você precisar alterar o caminho do socket, edite o arquivo:
`routes/kanban.py`

Procure pelas linhas:
```python
socket_path="/socket.io"
```

E altere para o caminho desejado, por exemplo:
```python
socket_path="/meu-app/socket.io"
```

## Problemas Comuns

### WebSocket não conecta
- Verifique se o proxy está passando os headers `Upgrade` e `Connection`
- Certifique-se de que `proxy_http_version 1.1` está configurado (Nginx)
- Verifique se `mod_proxy_wstunnel` está habilitado (Apache)

### Erro 404 no socket.io
- Verifique se o caminho no proxy corresponde ao `socket_path` configurado
- Confirme que o `sub_filter` (Nginx) ou `Substitute` (Apache) está modificando o HTML corretamente

### Conexão cai frequentemente
- Aumente o timeout do proxy
- Nginx: adicione `proxy_read_timeout 300s;`
- Apache: adicione `ProxyTimeout 300`

### HTTPS/WSS
Se você estiver usando HTTPS, certifique-se de:
- Usar `wss://` ao invés de `ws://` na configuração do proxy
- Configurar SSL corretamente no proxy reverso
- O Socket.IO detectará automaticamente se precisa usar `wss://` baseado no protocolo da página
