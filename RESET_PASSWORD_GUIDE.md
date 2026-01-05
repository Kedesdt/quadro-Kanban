# 🔑 Sistema de Reset de Senha

## Funcionalidade Implementada

O administrador agora pode gerar links de redefinição de senha para membros da equipe que esqueceram suas credenciais.

## Como Usar

### Para o Administrador:

1. **Acesse o Gerenciamento de Equipe**

   - Faça login como administrador
   - Clique em "Gerenciar Equipe" no menu superior

2. **Gerar Link de Reset**

   - Na lista de membros, clique no botão "🔑 Reset Senha" ao lado do membro
   - Um link será gerado e exibido na tela
   - Clique no botão "📋 Copiar Link" para copiar automaticamente
   - Envie este link para o membro via e-mail, WhatsApp, etc.

3. **Link Gerado**
   - Formato: `http://seu-dominio/reset-password/TOKEN_UNICO`
   - Válido por 24 horas
   - Uso único (não pode ser reutilizado)

### Para o Membro da Equipe:

1. **Receber o Link**

   - O administrador enviará um link único de redefinição

2. **Acessar o Link**

   - Clique no link recebido
   - Você será redirecionado para a página de redefinição de senha

3. **Redefinir a Senha**

   - Digite a nova senha (mínimo 4 caracteres)
   - Confirme a nova senha
   - Clique em "Redefinir Senha"

4. **Fazer Login**
   - Após redefinir, faça login com a nova senha

## Características de Segurança

### ✅ Segurança do Token

- **Token único**: Gerado com `secrets.token_urlsafe(32)` - criptograficamente seguro
- **Validade**: 24 horas após a geração
- **Uso único**: Após usar, o token é marcado como usado e não pode ser reutilizado
- **Não reutilizável**: Cada reset precisa de um novo link

### ✅ Proteção

- Apenas administradores podem gerar links
- Links não podem ser gerados para outros administradores
- Token armazenado no banco de dados com timestamp
- Verificação de expiração automática

### ✅ Validações

- Senha mínima de 4 caracteres
- Confirmação de senha obrigatória
- Mensagens de erro claras
- Link inválido ou expirado gera erro

## Estrutura Técnica

### Nova Tabela no Banco de Dados

```python
PasswordResetToken
├── id (Integer, PK)
├── user_id (Integer, FK -> User)
├── token (String, Unique)
├── created_at (DateTime)
├── expires_at (DateTime)
└── used (Boolean)
```

### Rotas Adicionadas

#### Rota de Geração (Admin)

```
POST /team/reset-password/<user_id>
Blueprint: team
Acesso: Apenas administradores
```

#### Rota de Reset (Público com Token)

```
GET/POST /reset-password/<token>
Blueprint: auth
Acesso: Qualquer pessoa com token válido
```

### Templates Criados

- `templates/reset_password.html` - Página de redefinição de senha

### Templates Modificados

- `templates/team.html` - Adicionado botão de reset e script de cópia

## Fluxo Completo

```
1. Admin acessa /team
2. Admin clica em "🔑 Reset Senha" para membro
3. Sistema gera token único
4. Link é exibido: /reset-password/TOKEN
5. Admin copia e envia link para membro
6. Membro acessa o link
7. Sistema valida token (existe? expirado? usado?)
8. Membro preenche nova senha
9. Sistema atualiza senha e marca token como usado
10. Membro faz login com nova senha
```

## Melhorias Futuras Sugeridas

- [ ] Envio automático por e-mail
- [ ] Personalização do tempo de validade do token
- [ ] Histórico de resets por usuário
- [ ] Notificação ao membro quando senha for resetada
- [ ] Opção de auto-reset (enviar link via e-mail sem admin)
- [ ] Limite de tentativas de reset

## Mensagens de Erro Possíveis

| Erro                                       | Causa                                      | Solução                 |
| ------------------------------------------ | ------------------------------------------ | ----------------------- |
| "Link de redefinição inválido ou expirado" | Token não existe, expirou ou já foi usado  | Peça novo link ao admin |
| "Usuário não encontrado"                   | Membro não existe ou não pertence à equipe | Verifique o membro      |
| "Acesso negado"                            | Usuário não é admin                        | Faça login como admin   |
| "As senhas não coincidem"                  | Senha e confirmação diferentes             | Digite novamente        |
| "A senha deve ter pelo menos 4 caracteres" | Senha muito curta                          | Use senha mais longa    |

## Exemplo de Uso

### Cenário: João esqueceu a senha

1. **Admin (Maria):**

   ```
   - Acessa /team
   - Clica em "🔑 Reset Senha" ao lado de "João"
   - Copia o link gerado
   - Envia para João: "Olá João, use este link para redefinir sua senha: http://..."
   ```

2. **João:**
   ```
   - Recebe o link
   - Clica no link
   - Vê: "Redefinir Senha - Usuário: João"
   - Digite nova senha: ********
   - Confirma senha: ********
   - Clica em "Redefinir Senha"
   - Mensagem: "Senha redefinida com sucesso!"
   - Faz login com nova senha
   ```

## Código de Exemplo

### Gerar Token (Administrador)

```python
token = PasswordResetToken.create_token(user, hours=24)
reset_url = url_for('auth.reset_password', token=token, _external=True)
```

### Verificar Token (Usuário)

```python
user = PasswordResetToken.verify_token(token)
if user:
    # Token válido - permitir reset
else:
    # Token inválido/expirado
```

---

**Data de Implementação**: 2026-01-05  
**Status**: ✅ Implementado e Funcional  
**Compatibilidade**: Totalmente compatível com sistema existente
