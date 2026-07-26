# ADR-002: Python Backend

## Status
Aceito

## Contexto
É necessário escolher a linguagem principal do backend, responsável por regras de negócio, segurança, autenticação, autorização e detecção de ameaças.

## Decisão
O backend será implementado em Python, utilizando FastAPI como framework web e `uv` como gerenciador de ambiente e dependências.

## Justificativa
- Ecossistema maduro para APIs assíncronas (FastAPI + Starlette + Pydantic).
- Tipagem estática opcional via type hints, validada em tempo de execução pelo Pydantic, o que reduz erros de contrato entre camadas.
- Bibliotecas maduras para os requisitos do domínio: SQLAlchemy Async para persistência, `aio-pika`/`aiormq` para RabbitMQ, `redis-py` assíncrono para cache.
- `uv` oferece resolução de dependências determinística e rápida, substituindo a necessidade de Poetry/Pipenv.

## Alternativas Rejeitadas
- **Node.js/TypeScript no backend:** unificaria a linguagem com o frontend, mas o ecossistema Python tem maior maturidade para os requisitos de segurança, análise de risco e integração com ferramentas de observabilidade que o projeto pretende demonstrar.
- **Go:** ofereceria melhor performance bruta, mas aumentaria a curva de desenvolvimento para o escopo de regras de negócio complexas do domínio de identidade e segurança.

## Consequências
- A versão exata do Python deve ser fixada em `pyproject.toml` e documentada no README do backend.
- Todo o fluxo de desenvolvimento (execução, testes, lint) passa a depender do `uv`.