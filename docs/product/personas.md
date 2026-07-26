# Personas — SentinelCore

## Persona 1 — Analista de Segurança (SecOps)

**Nome fictício:** Camila
**Objetivo:** Monitorar eventos de autenticação e responder a incidentes rapidamente.
**Necessidades:**
- Ver em tempo real logins suspeitos e falhas consecutivas.
- Entender por que um Risk Score foi atribuído a um evento.
- Revisar a timeline de um incidente e as ações automatizadas já tomadas.
- Revogar sessões ou bloquear IPs manualmente quando necessário.

**Frustrações com sistemas atuais:**
- Logs dispersos sem correlação.
- Falta de explicação sobre por que um alerta foi gerado.
- Resposta manual lenta demais para conter um ataque em andamento.

## Persona 2 — Administrador de Sistema

**Nome fictício:** Rafael
**Objetivo:** Gerenciar usuários, papéis e permissões de forma segura.
**Necessidades:**
- Criar, ativar e desativar usuários.
- Atribuir papéis (roles) e visualizar permissões efetivas.
- Consultar auditoria de qualquer alteração de permissão.
- Gerenciar sessões ativas de qualquer usuário.

**Frustrações com sistemas atuais:**
- Falta de rastreabilidade de quem alterou o quê.
- Interfaces que escondem botões como única forma de controle de acesso, sem garantia real no backend.

## Persona 3 — Desenvolvedor/Avaliador Técnico

**Nome fictício:** Estudo de caso — recrutador técnico ou par de engenharia avaliando o projeto.
**Objetivo:** Entender as decisões arquiteturais e a qualidade de engenharia do sistema.
**Necessidades:**
- Documentação clara de arquitetura e decisões (ADRs).
- Código organizado, testado e com separação de responsabilidades evidente.
- Capacidade de rodar o projeto localmente via Docker Compose.

## Casos de Uso Principais

1. Como Camila, quero visualizar uma lista de eventos de segurança recentes, filtrando por severidade e tipo, para identificar padrões suspeitos.
2. Como Camila, quero abrir um incidente e ver sua timeline completa, incluindo eventos correlacionados e respostas automatizadas.
3. Como Rafael, quero criar um usuário e atribuir um papel, garantindo que a ação fique registrada em auditoria.
4. Como Rafael, quero revogar todas as sessões ativas de um usuário comprometido em um único clique.
5. Como qualquer usuário do sistema, quero fazer login com meu e-mail e senha e receber um token de acesso válido, com minha sessão registrada.
6. Como sistema, quero detectar automaticamente tentativas de força bruta e, ao ultrapassar um limiar de risco, abrir um incidente e executar uma resposta automatizada.