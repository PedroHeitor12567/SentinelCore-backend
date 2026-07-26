# ADR-004: Modular Monolith

## Status
Aceito

## Contexto
O backend precisa organizar múltiplos domínios (identidade, autenticação, autorização, sessões, auditoria, eventos de segurança, detecção de ameaças, incidentes). É necessário decidir entre microsserviços desde o início ou um monolito modular.

## Decisão
O backend será estruturado como um **Modular Monolith**: um único processo/deploy, organizado em módulos de domínio com fronteiras internas claras (`modules/identity`, `modules/authentication`, `modules/authorization`, `modules/sessions`, `modules/audit`, `modules/security_events`, `modules/threat_detection`, `modules/risk_analysis`, `modules/incidents`), comunicando-se entre si através de contratos internos explícitos (não acesso direto a modelos de outros módulos).

## Justificativa
- Os domínios do SentinelCore são fortemente coesos (autenticação, autorização e auditoria compartilham o mesmo ciclo de vida de sessão/usuário). Dividir prematuramente em microsserviços introduziria complexidade de rede sem benefício real neste estágio.
- Um monolito modular permite demonstrar separação de responsabilidades e Clean/Hexagonal Architecture sem o custo operacional de orquestrar múltiplos serviços.
- RabbitMQ já é adotado internamente para desacoplar processamento assíncrono de eventos, o que prepara o terreno para uma eventual extração de módulos em serviços separados no futuro, caso necessário.

## Alternativas Rejeitadas
- **Microsserviços desde o início:** aumentaria complexidade de infraestrutura (service discovery, comunicação entre serviços, consistência distribuída) sem justificativa de escala real para o escopo do projeto.
- **Monolito não-modular ("big ball of mud"):** rejeitado por violar diretamente o objetivo de demonstrar separação de responsabilidades.

## Consequências
- Módulos não devem importar modelos internos de outros módulos diretamente; a comunicação ocorre via serviços de aplicação ou eventos publicados no RabbitMQ.
- Caso um módulo precise escalar independentemente no futuro, a fronteira já modular facilita a extração para um serviço próprio.