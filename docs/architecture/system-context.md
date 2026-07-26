# System Context — SentinelCore

## Visão Geral

```
┌────────────────────────────────────────────┐
│              SENTINELCORE                  │
└────────────────────────────────────────────┘

        ┌─────────────────────┐
        │ Frontend Repository │
        │                     │
        │ React + TypeScript  │
        │                     │
        │ Dashboard           │
        │ Interface           │
        │ Visualização        │
        └──────────┬──────────┘
                   │
                   │ HTTPS / REST API
                   │
                   ▼
        ┌─────────────────────┐
        │  Backend Repository │
        │                     │
        │ Python              │
        │ FastAPI             │
        │                     │
        │ Regras de negócio   │
        │ Segurança           │
        │ Autenticação        │
        │ Autorização         │
        │ Auditoria           │
        │ Threat Detection    │
        └──────────┬──────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   PostgreSQL   Redis      RabbitMQ
```

## Fronteira dos Repositórios

| Repositório | Responsabilidade | Não é responsável por |
|---|---|---|
| `sentinelcore-backend` | Domínio, regras de negócio, autenticação, autorização, auditoria, detecção de ameaças, persistência, mensageria, API | Renderização de UI, navegação, estado de tela |
| `sentinelcore-frontend` | Interface, dashboard, navegação, formulários, feedback visual, consumo da API | Decidir se uma ação é permitida, validar tokens, calcular risco |

Os repositórios não compartilham código. A única forma de comunicação é a API HTTP exposta pelo backend.

## Responsabilidades — Regra Fundamental

**O backend decide:**
- Se o usuário está autenticado.
- Se o token é válido.
- Se o usuário possui permissão para uma ação.
- Se um comportamento é suspeito.
- Se um incidente deve ser criado.

**O frontend decide:**
- Como uma informação é exibida.
- Como o usuário interage com o sistema.
- Qual tela é exibida.
- Como um erro é apresentado ao usuário.

O frontend pode ocultar um botão para melhorar a experiência do usuário, mas isso nunca substitui a validação de autorização no backend. Toda requisição sensível é revalidada no servidor, independentemente do que a interface exibe.

## Autenticação e Autorização — Visão de Alto Nível

- Autenticação: login por e-mail/senha retorna um par `access_token`/`refresh_token` (JWT). O `access_token` tem vida curta; o `refresh_token` é rotacionado a cada uso e pode ser revogado.
- Autorização: modelo RBAC (`User → Role → Permission`). Toda rota protegida declara as permissões exigidas; a verificação ocorre no backend antes de qualquer processamento de negócio.
- Sessões: cada login cria uma sessão associada a dispositivo, IP e user-agent, consultável e revogável.

## Comunicação

```
Frontend
    │
    │ HTTP (JSON, HTTPS)
    ▼
Backend API (/api/v1)
```

Toda comunicação segue o contrato definido no OpenAPI gerado pelo backend (ver ADR-006) e é versionada por URL (ver ADR-005).