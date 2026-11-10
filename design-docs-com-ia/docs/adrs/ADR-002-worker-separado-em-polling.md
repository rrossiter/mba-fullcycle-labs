# ADR-002: Worker em processo separado com polling de 2 segundos

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Depends on:**
- [ADR-001: Padrão Outbox no MySQL para eventos de webhook](./ADR-001-outbox-no-mysql.md)

**Used by:**
- [ADR-003: Política de retry com backoff exponencial e Dead Letter Queue](./ADR-003-retry-com-backoff-e-dlq.md)

**Related to:**
- [ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks](./ADR-006-reuso-dos-padroes-existentes.md)

## Status

Aceito

## Contexto

Com o outbox (ADR-001), algum componente precisa ler os eventos pendentes e enviá-los por HTTP aos clientes. O requisito de produto é latência abaixo de 10 segundos, o que para os clientes já conta como "tempo real". Os clientes não pedem ordenação global de eventos, só querem saber quando cada pedido muda.

Hoje a aplicação tem um único ponto de entrada, `src/server.ts`, que sobe a API Express. O MySQL não tem um mecanismo nativo de notificação como o `LISTEN/NOTIFY` do PostgreSQL. Se o envio rodasse dentro da API, um reinício ou deploy derrubaria o worker junto.

## Direcionadores da Decisão

- Atender a latência de entrega abaixo de 10 segundos.
- Tornar o ciclo de vida da entrega independente do ciclo de vida da API.
- Manter a ordem de entrega por pedido.
- Reaproveitar o mesmo banco e a mesma stack, sem infraestrutura nova.
- Manter a solução simples para um time pequeno.

## Alternativas Consideradas

1. Processo separado com polling a cada 2 segundos e um único worker (opção escolhida)
2. Worker rodando dentro do processo da API
3. Trigger do MySQL notificando o worker
4. Múltiplos workers em paralelo

## Decisão

Opção escolhida: "Processo separado com polling a cada 2 segundos e um único worker", porque atende com folga o requisito de menos de 10 segundos, isola a entrega dos reinícios da API e preserva a ordem por pedido sem nenhum mecanismo extra.

Detalhes da decisão:

- O novo ponto de entrada é `src/worker.ts`, com o script `npm run worker`.
- A lógica de processamento fica dentro do módulo de webhooks (por exemplo `src/modules/webhooks/webhook.processor.ts`).
- O worker usa o mesmo banco e a mesma `DATABASE_URL`, mas abre sua própria instância de `PrismaClient`, porque o cliente é por processo.
- A cada 2 segundos, o worker lê em lotes pequenos os eventos pendentes mais antigos, ordenados por data de criação, envia e marca o resultado.
- O timeout de cada chamada HTTP é de 10 segundos. Acima disso, conta como falha e entra na política de retry (ADR-003).
- Roda um único worker. A ordem é garantida só por `order_id` e enquanto houver um único worker, o que fica registrado como limitação conhecida.

## Prós e Contras das Opções

### Processo separado com polling de 2s e worker único

- Bom, porque reinícios e deploys da API não interrompem a entrega.
- Bom, porque o polling de 2 segundos atende o requisito de latência com folga.
- Bom, porque a ordem por pedido vem naturalmente da ordenação por data de criação.
- Ruim, porque há uma latência mínima de até 2 segundos, mesmo com o sistema ocioso.
- Ruim, porque o polling consulta o banco continuamente, mesmo sem eventos.

### Worker dentro do processo da API

- Bom, porque não exige um processo adicional para implantar.
- Ruim, porque um reinício da API derruba o worker.
- Ruim, porque o envio competiria por recursos com as requisições HTTP.

### Trigger do MySQL notificando o worker

- Bom, porque seria mais reativo que o polling.
- Ruim, porque o MySQL não tem listener nativo e o trigger não notifica processos externos, o que exigiria improvisos como escrever em arquivo ou chamar um endpoint.

### Múltiplos workers em paralelo

- Bom, porque aumentaria o throughput de entrega.
- Ruim, porque perde a garantia de ordem por pedido, a menos que se particione por `order_id` ou se use lock pessimista.

## Consequências

A entrega passa a ter ciclo de vida próprio e a solução continua simples, sem componentes novos, atendendo o requisito de latência com margem.

Em contrapartida, há mais um processo para implantar, monitorar e manter no ar. O worker único é um ponto único de falha e limita o throughput: se ele parar, as entregas param. O ponto de entrada `src/worker.ts` precisa reaproveitar parte da composição feita em `src/app.ts` (configuração, Prisma, logger) sem duplicá-la.

O trade-off é aceitar uma latência fixa de até 2 segundos e um teto de throughput em troca de simplicidade operacional e ordenação por pedido. A ordem global não é garantida. Quando for preciso escalar, a saída prevista é particionar por `order_id` ou usar lock pessimista, o que exigirá nova decisão.

## Referências

- TRANSCRICAO.md (trechos 09:08 a 09:14, 09:28 a 09:30 e 09:42)
- src/server.ts
- src/app.ts
- src/config/database.ts
- package.json:10
