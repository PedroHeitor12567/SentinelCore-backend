# Problem Statement — SentinelCore

## Contexto

Organizações que operam sistemas com autenticação e controle de acesso enfrentam um problema recorrente: a maior parte dos incidentes de segurança não é causada por falhas de infraestrutura, mas por abuso de identidade — credenciais comprometidas, sessões sequestradas, escalonamento indevido de privilégios e comportamento anômalo de login que passa despercebido até que o dano já esteja feito.

A maioria dos sistemas trata autenticação, autorização e auditoria como funcionalidades isoladas, implementadas de forma reativa, sem correlação entre eventos. Isso resulta em três lacunas:

1. **Detecção tardia**: eventos suspeitos (força bruta, credential stuffing, login de dispositivo não reconhecido) são registrados em log, mas raramente analisados em tempo real.
2. **Resposta manual**: quando um incidente é identificado, a contenção (revogar sessão, bloquear IP, exigir MFA) depende de intervenção humana, aumentando o tempo de exposição.
3. **Falta de rastreabilidade**: decisões de segurança (por que uma sessão foi revogada, por que uma permissão foi alterada) não são auditáveis de forma clara e explicável.

## Problema

> Como fornecer uma plataforma de identidade que não apenas autentique e autorize usuários, mas que também detecte comportamento anômalo, calcule risco de forma explicável, registre auditoria completa e responda a ameaças de forma automatizada e rastreável?

## Público-Alvo

- Times de engenharia que precisam de um módulo de identidade e segurança robusto como referência de arquitetura.
- Times de segurança (SecOps) que precisam de visibilidade sobre eventos de autenticação e incidentes.
- Administradores de sistema responsáveis por gerenciar usuários, sessões e permissões.

## Objetivos do Produto

1. Fornecer autenticação segura com tokens de curta duração e rotação de refresh tokens.
2. Fornecer autorização baseada em papéis (RBAC), com trilha de auditoria de qualquer alteração de permissão.
3. Detectar comportamento suspeito (força bruta, credential stuffing, login anômalo) com pontuação de risco explicável.
4. Criar incidentes de segurança automaticamente a partir de eventos correlacionados, com timeline e severidade.
5. Executar respostas automatizadas (revogação de sessão, bloqueio de IP, exigência de MFA) de forma auditável.
6. Expor toda a operação através de um dashboard que permita a um analista entender o que aconteceu, por quê, e o que foi feito a respeito.

## Não-Objetivos (Fora de Escopo Inicial)

- Não é um SIEM completo nem substitui ferramentas de correlação de logs corporativos.
- Não implementa detecção baseada em machine learning na primeira versão — o Risk Score inicial é baseado em regras explicáveis.
- Não gerencia identidade federada (SSO/SAML/OIDC com provedores externos) na primeira fase.

## Métrica de Sucesso

O projeto é bem-sucedido quando é possível demonstrar, de ponta a ponta, o fluxo:

```
Tentativa de login suspeita
        →
Evento de segurança registrado
        →
Risk Score calculado
        →
Incidente criado
        →
Resposta automatizada executada
        →
Visualização completa no frontend
```