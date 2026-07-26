# Vision — SentinelCore

## Declaração de Visão

SentinelCore é uma plataforma de identidade e segurança que trata autenticação, autorização, auditoria e detecção de ameaças como partes de um único sistema coerente, e não como funcionalidades isoladas. O sistema é projetado para demonstrar, de forma prática e auditável, como identidade comprometida pode ser detectada, contida e investigada — do evento bruto até a resposta automatizada.

## Para quem

Para times de engenharia e segurança que precisam de:

- um backend de identidade com autenticação e autorização robustas;
- visibilidade sobre eventos de segurança em tempo real;
- um mecanismo de detecção de ameaças explicável (não uma caixa-preta);
- um fluxo completo de gestão de incidentes, do evento à resolução.

## O que o SentinelCore é

- Um backend de domínio (Python/FastAPI) que centraliza as decisões de segurança do sistema.
- Um frontend (React/TypeScript) que consome esse backend como cliente, sem lógica de segurança própria.
- Uma demonstração de arquitetura: separação clara de repositórios, contratos de API versionados, e cada tecnologia justificada por um problema real que ela resolve.

## O que o SentinelCore não é

- Não é um produto SaaS pronto para produção multi-tenant.
- Não é uma ferramenta de pentest ou exploração de vulnerabilidades.
- Não é um substituto para soluções corporativas de SIEM/SOAR.

## Princípios Norteadores

1. **O backend é a autoridade.** Toda decisão de segurança (autenticação, autorização, risco, resposta) é tomada no backend. O frontend nunca decide se uma ação é permitida.
2. **Toda ação sensível é auditável.** Se uma sessão é revogada, uma permissão é alterada, ou uma resposta automatizada é executada, isso é registrado com contexto suficiente para reconstrução posterior.
3. **Detecção explicável antes de detecção sofisticada.** O Risk Score inicial é baseado em regras claras e documentadas, não em modelos opacos.
4. **Repositórios independentes, contrato explícito.** Backend e frontend evoluem separadamente, comunicando-se apenas através de uma API HTTP versionada e documentada.
5. **Cada tecnologia precisa de uma justificativa.** Nenhuma ferramenta é adicionada "porque é comum no mercado" sem que resolva um problema identificado do domínio.

## Glossário Inicial

| Termo | Definição |
|---|---|
| **Identity** | Representação de um usuário e suas credenciais no sistema. |
| **Session** | Contexto de acesso de um usuário autenticado, associado a um dispositivo e IP. |
| **Security Event** | Registro estruturado de um acontecimento relevante para segurança (ex.: `LOGIN_FAILED`). |
| **Risk Score** | Pontuação calculada a partir de fatores de risco explícitos, usada para decidir se um incidente deve ser aberto. |
| **Incident** | Agrupamento de eventos correlacionados que representam uma potencial ameaça, com timeline e severidade. |
| **Automated Response** | Ação executada automaticamente pelo sistema em resposta a um incidente (ex.: revogar sessão). |
| **RBAC** | Role-Based Access Control — modelo de autorização baseado em papéis e permissões. |