# Integration — SentinelCore

## Contrato de Integração

A integração entre `sentinelcore-frontend` e `sentinelcore-backend` é tratada como um contrato formal, não como um acoplamento implícito.

### Formato

- Protocolo: HTTPS.
- Formato de payload: JSON.
- Autenticação: Bearer token (`Authorization: Bearer <access_token>`) em toda rota protegida.
- Versionamento: prefixo `/api/v1` (ver ADR-005).
- Especificação: OpenAPI gerado automaticamente pelo FastAPI (ver ADR-006).

### Exemplo de Contrato

```
POST /api/v1/auth/login
```

Request:
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Response (200):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

Response (401):
```json
{
  "detail": "Invalid credentials"
}
```

### Tratamento de Erros no Frontend

| Código HTTP | Significado | Tratamento esperado no frontend |
|---|---|---|
| 400 | Requisição inválida | Exibir mensagem de validação |
| 401 | Não autenticado / token inválido ou expirado | Redirecionar para login, tentar refresh se aplicável |
| 403 | Autenticado, mas sem permissão | Exibir mensagem de acesso negado, nunca assumir que a ausência de um botão é suficiente |
| 404 | Recurso não encontrado | Exibir estado vazio/erro apropriado |
| 429 | Rate limit excedido | Exibir mensagem de limite de tentativas |
| 500 | Erro interno | Exibir estado de erro genérico e permitir nova tentativa |

### Consistência de Tipos

O backend define schemas Pydantic (request/response). O frontend define interfaces TypeScript equivalentes. Exemplo:

Backend:
```python
class UserResponse(BaseModel):
    id: UUID
    email: str
    status: str
```

Frontend:
```typescript
interface User {
  id: string;
  email: string;
  status: string;
}
```

A consistência entre esses dois lados é mantida manualmente nas fases iniciais do projeto. A geração automática de tipos a partir do OpenAPI é uma evolução futura em aberto (ver ADR-006).

## Fluxo de Desenvolvimento de uma Funcionalidade

```
Domínio
   ↓
Backend
   ↓
API
   ↓
Contrato
   ↓
Frontend
   ↓
Integração
   ↓
Testes
```

Uma funcionalidade só é considerada completa quando esse fluxo é percorrido por inteiro — um endpoint funcionando isoladamente ou uma tela sendo exibida sem estar integrada ao backend real não são considerados entregas completas.