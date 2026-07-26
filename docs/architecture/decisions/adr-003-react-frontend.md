# ADR-003: React Frontend

## Status
Aceito

## Contexto
É necessário escolher a stack do frontend, responsável pelo dashboard, visualização de dados de segurança e interação com a API do backend.

## Decisão
O frontend será implementado em React com TypeScript.

## Justificativa
- React é amplamente adotado, com ecossistema maduro de bibliotecas para roteamento, formulários e visualização de dados (gráficos de risco, timelines de incidentes).
- TypeScript garante tipagem estática no consumo dos contratos da API, reduzindo divergências entre o que o backend envia e o que o frontend espera.
- Componentização facilita a separação entre componentes de UI puros e features que consomem a API.

## Alternativas Rejeitadas
- **Vue.js:** ecossistema também maduro, mas com menor prevalência em times de segurança/backend-heavy, o que reduziria o valor demonstrativo do projeto para avaliação técnica.
- **Server-side rendering completo (Next.js) full-stack:** misturaria responsabilidades de backend e frontend em um único runtime, contrariando a decisão de repositórios e responsabilidades separados (ADR-001).

## Consequências
- A ferramenta de build (Vite, CRA ou similar) será escolhida e documentada na Fase 3 (Bootstrap do Frontend).
- O frontend nunca deve reimplementar lógica de autorização — apenas refletir o que a API retorna.