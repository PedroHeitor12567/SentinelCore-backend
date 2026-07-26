# ADR-006: OpenAPI as API Contract

## Status
Aceito

## Contexto
O frontend precisa conhecer com precisão os formatos de request/response, códigos de erro e regras de autenticação de cada endpoint do backend, sem depender de suposições.

## Decisão
O FastAPI gerará automaticamente a especificação OpenAPI (`/openapi.json`) a partir dos schemas Pydantic e das rotas definidas no backend. Essa especificação é a fonte oficial do contrato entre backend e frontend. A geração automática de tipos TypeScript a partir do OpenAPI é registrada como uma evolução futura, a ser avaliada e documentada em uma ADR própria quando implementada.

## Justificativa
- O FastAPI já gera OpenAPI nativamente a partir do código, eliminando a necessidade de manter uma especificação manual separada que poderia divergir da implementação real.
- Serve como documentação viva e testável (Swagger UI / ReDoc) para qualquer consumidor da API, incluindo o time de frontend.

## Alternativas Rejeitadas
- **Contrato mantido manualmente em Markdown/Postman apenas:** rejeitado como única fonte, por risco de divergência entre documentação e implementação real. Documentação em Markdown (como a seção 11 do prompt mestre) continua existindo como referência legível por humanos, mas não substitui o OpenAPI como fonte de verdade.

## Consequências
- Toda mudança de schema Pydantic reflete automaticamente na documentação da API.
- A decisão sobre geração automática de tipos TypeScript a partir do OpenAPI fica em aberto e será revisitada quando o contrato entre repositórios crescer o suficiente para justificar a automação.