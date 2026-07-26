# ADR-005: API Versioning

## Status
Aceito

## Contexto
O frontend depende do contrato exposto pelo backend. É necessário definir como mudanças incompatíveis na API serão comunicadas e geridas ao longo do tempo.

## Decisão
A API será versionada por caminho de URL, com o prefixo `/api/v1`. Toda alteração que quebre compatibilidade com clientes existentes (mudança de formato de request/response, remoção de campo, alteração de semântica de um endpoint) resulta em uma nova versão (`/api/v2`), mantendo a versão anterior ativa durante um período de transição documentado.

## Justificativa
- Versionamento por URL é simples de implementar, simples de testar e explícito para quem consome a API (incluindo o frontend e ferramentas de documentação como o Swagger/OpenAPI gerado pelo FastAPI).
- Evita que mudanças no backend quebrem o frontend silenciosamente.

## Alternativas Rejeitadas
- **Versionamento por header (`Accept-Version`):** mais "elegante" do ponto de vista REST, porém menos visível e mais difícil de depurar manualmente ou testar via ferramentas simples (curl, navegador).
- **Sem versionamento:** rejeitado por criar acoplamento frágil entre backend e frontend, contrariando a separação de repositórios definida na ADR-001.

## Consequências
- Toda alteração de contrato precisa ser avaliada quanto à compatibilidade antes de ser mesclada.
- Endpoints legados devem ser documentados com prazo de descontinuação quando uma nova versão for introduzida.