# ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Related to:**
- [ADR-001: Padrão Outbox no MySQL para eventos de webhook](./ADR-001-outbox-no-mysql.md)
- [ADR-002: Worker em processo separado com polling de 2 segundos](./ADR-002-worker-separado-em-polling.md)
- [ADR-003: Política de retry com backoff exponencial e Dead Letter Queue](./ADR-003-retry-com-backoff-e-dlq.md)

## Status

Aceito

## Contexto

O projeto é um monólito modular em TypeScript, Express 4 e Prisma, com convenções já consolidadas:

- Cada domínio é um módulo em `src/modules/<dominio>/`, com controller, service, repository, routes e schemas.
- Há uma hierarquia de erros em `src/shared/errors/`, com a classe base `AppError` e subclasses como `InsufficientStockError` e `InvalidStatusTransitionError`. Os códigos seguem o formato `INSUFFICIENT_STOCK` e `INVALID_STATUS_TRANSITION`.
- O tratamento de erros é centralizado em `src/middlewares/error.middleware.ts`, que já converte `AppError`, erros do Zod e erros do Prisma no envelope padrão.
- A validação de entrada usa Zod, por meio de `src/middlewares/validate.middleware.ts`.
- O logging usa Pino, configurado em `src/shared/logger/index.ts`.
- A autorização por papel usa `requireRole`, em `src/middlewares/auth.middleware.ts`.
- Todas as tabelas usam chave primária UUID.

A funcionalidade de webhooks traz controller, CRUD, worker, novas tabelas e novos erros. É preciso decidir se ela segue essas convenções ou se introduz uma estrutura própria.

## Direcionadores da Decisão

- Minimizar a curva de aprendizado para quem já conhece a base de código.
- Manter o mesmo envelope de erro e o mesmo logging em toda a API.
- Não alterar componentes compartilhados que já funcionam, como o middleware de erros.
- Caber no prazo de três sprints.
- Preservar a atomicidade com a transação de pedidos (ADR-001).

## Alternativas Consideradas

1. Reuso máximo dos padrões existentes, com webhooks como mais um módulo (opção escolhida)
2. Serviço separado (microsserviço de notificações) com stack própria
3. Módulo com estrutura e bibliotecas próprias (outro logger, outro formato de erro, container de DI)

## Decisão

Opção escolhida: "Reuso máximo dos padrões existentes", porque o webhook se encaixa na base atual sem nenhuma mudança em componentes compartilhados e sem trabalho de infraestrutura.

Detalhes da decisão:

- O módulo novo fica em `src/modules/webhooks/`, com a mesma estrutura dos outros. A lógica do worker fica em `src/modules/webhooks/webhook.processor.ts`, e `src/worker.ts` é só o ponto de entrada (ADR-002).
- Os erros estendem `AppError` e usam o prefixo `WEBHOOK_`, como `WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL` e `WEBHOOK_SECRET_REQUIRED`. São tratados pelo middleware de erros sem nenhuma alteração nele.
- Os schemas de entrada usam Zod com o middleware de validação existente.
- O logging usa o Pino já configurado, sem nenhuma biblioteca nova.
- O replay da DLQ usa `requireRole` com o papel ADMIN (ADR-003). O CRUD de configuração exige apenas autenticação.
- As novas tabelas usam UUID e o mapeamento de nomes em snake_case do Prisma.
- A integração com pedidos acontece no método `changeStatus` do serviço de pedidos, por meio da função `publishWebhookEvent(tx, ...)` (ADR-001).

## Prós e Contras das Opções

### Reuso máximo dos padrões existentes

- Bom, porque quem conhece um módulo entende o de webhooks.
- Bom, porque middleware de erros, validação e logging funcionam sem alteração.
- Bom, porque cabe no prazo de três sprints.
- Ruim, porque o módulo herda as limitações dos padrões atuais.

### Serviço separado

- Bom, porque teria deploy e escala independentes.
- Ruim, porque exigiria novo deploy, novo pipeline e comunicação entre serviços.
- Ruim, porque perderia a atomicidade com a transação de pedidos.

### Módulo com estrutura própria

- Bom, porque daria liberdade para escolher outras ferramentas.
- Ruim, porque fragmentaria a base de código e exigiria mudanças no middleware de erros.
- Ruim, porque aumentaria a curva de aprendizado sem ganho funcional.

## Consequências

A curva de aprendizado é mínima, as respostas de erro mantêm o mesmo envelope em toda a API e o prefixo `WEBHOOK_` facilita filtrar logs e diagnosticar problemas. A funcionalidade cabe no prazo sem trabalho de infraestrutura.

Em contrapartida, o módulo herda as limitações atuais, como a injeção manual de dependências em `src/app.ts` e o mapeamento de poucos códigos de erro do Prisma no middleware de erros. O monólito cresce e acopla mais um domínio ao mesmo deploy e ao mesmo banco. O worker é um segundo ponto de entrada que precisa compartilhar a composição de dependências sem duplicar código. Extrair webhooks para um serviço próprio no futuro dará mais trabalho do que se ele já nascesse isolado.

O trade-off é priorizar consistência e velocidade de entrega em vez de isolamento e independência de deploy. Para o escopo atual, com três clientes e prazo curto, a coesão com a base existente vale mais que a flexibilidade de um serviço separado.

## Referências

- TRANSCRICAO.md (trechos 09:27 a 09:30, 09:36 e 09:51)
- src/shared/errors/app-error.ts:3
- src/shared/errors/http-errors.ts:45
- src/middlewares/error.middleware.ts:14
- src/middlewares/auth.middleware.ts:49
- src/shared/logger/index.ts:14
- src/app.ts
