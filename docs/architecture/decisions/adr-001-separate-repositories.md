# ADR-001: Separate Backend and Frontend Repositories

## Status
Aceito

## Contexto
O SentinelCore é composto por um backend (Python/FastAPI) e um frontend (React/TypeScript). É necessário decidir se ambos vivem em um monorepo ou em repositórios independentes.

## Decisão
Backend e frontend serão mantidos em repositórios Git independentes: `sentinelcore-backend` e `sentinelcore-frontend`. A comunicação entre eles ocorre exclusivamente via API HTTP versionada. Nenhum código é compartilhado diretamente entre os repositórios.

## Justificativa
- Ciclos de vida diferentes: backend lida com regras de negócio e segurança; frontend lida com apresentação. Eles evoluem em ritmos distintos.
- Reforça a fronteira arquitetural: ao não compartilhar código, elimina-se a tentação de vazar lógica de segurança para o frontend.
- Facilita versionamento e deploy independentes de cada parte.
- Demonstra, na prática, que o contrato entre as partes é a API — não implementação compartilhada.

## Alternativas Rejeitadas
- **Monorepo com workspaces:** simplificaria o compartilhamento de tipos, mas aumentaria o risco de acoplamento indevido entre camadas que devem permanecer desacopladas.

## Consequências
- Tipos e contratos precisam ser mantidos consistentes manualmente ou via geração a partir do OpenAPI (ver ADR-006).
- Cada repositório precisa de sua própria documentação, testes e pipeline de CI/CD.