# ADR-003: Política de retry com backoff exponencial e Dead Letter Queue

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Depends on:**
- [ADR-001: Padrão Outbox no MySQL para eventos de webhook](./ADR-001-outbox-no-mysql.md)
- [ADR-002: Worker em processo separado com polling de 2 segundos](./ADR-002-worker-separado-em-polling.md)

**Related to:**
- [ADR-005: Garantia de entrega at-least-once com X-Event-Id](./ADR-005-entrega-at-least-once-com-x-event-id.md)
- [ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks](./ADR-006-reuso-dos-padroes-existentes.md)

## Status

Aceito

## Contexto

O endpoint do cliente pode estar fora do ar, lento ou em manutenção. Já houve cliente com indisponibilidade de duas horas em manutenção planejada. O worker (ADR-002) precisa decidir o que fazer quando uma entrega falha, seja por erro HTTP ou pelo timeout de 10 segundos.

Sem um limite de tentativas, eventos de clientes que deixaram de existir ficariam pendentes para sempre. Um limite baixo demais, por outro lado, descartaria eventos de clientes em manutenção curta.

## Direcionadores da Decisão

- Cobrir janelas realistas de indisponibilidade dos clientes, de algumas horas.
- Não deixar eventos pendurados indefinidamente na outbox.
- Manter a outbox enxuta, só com eventos ativos.
- Preservar os eventos que falharam, para depuração e reprocessamento.
- Restringir e auditar o reprocessamento manual.

## Alternativas Consideradas

1. 5 tentativas com backoff exponencial e DLQ em tabela separada, com replay manual (opção escolhida)
2. Retry indefinido com backoff
3. 3 tentativas
4. Marcar o evento como falho na própria outbox, sem tabela separada

## Decisão

Opção escolhida: "5 tentativas com backoff exponencial e DLQ em tabela separada", porque cobre quase 15 horas de indisponibilidade sem intervenção humana e evita eventos pendurados para sempre.

Detalhes da decisão:

- Os intervalos entre tentativas são 1 minuto, 5 minutos, 30 minutos, 2 horas e 12 horas.
- Depois da última falha, o evento vai para a tabela `webhook_dead_letter`, com o payload, o motivo da falha e o timestamp.
- O reprocessamento é manual, pelo endpoint `POST /admin/webhooks/dead-letter/:id/replay`, que recoloca o evento na outbox como pendente.
- O endpoint de replay exige o papel ADMIN, reaproveitando o `requireRole` existente.
- Cada replay é registrado em log com quem o executou, para auditoria.

## Prós e Contras das Opções

### 5 tentativas com backoff e DLQ separada

- Bom, porque cobre indisponibilidades de até cerca de 15 horas.
- Bom, porque mantém a outbox só com eventos ativos.
- Bom, porque a DLQ preserva payload e motivo, o que facilita depurar e reprocessar.
- Ruim, porque um evento pode chegar com até cerca de 15 horas de atraso.
- Ruim, porque a DLQ só é esvaziada manualmente.

### Retry indefinido com backoff

- Bom, porque nenhum evento é descartado.
- Ruim, porque eventos de clientes que sumiram ficam pendentes para sempre.

### 3 tentativas

- Bom, porque é mais agressivo e libera a fila mais rápido.
- Ruim, porque esgotaria as tentativas em cerca de 30 minutos, descartando eventos de clientes em manutenção planejada.

### Falha marcada na própria outbox

- Bom, porque dispensa uma tabela adicional.
- Ruim, porque mistura eventos mortos com a fila ativa e deixa a leitura do worker mais cara e confusa.

## Consequências

A entrega passa a tolerar indisponibilidades reais dos clientes sem intervenção humana, a outbox fica enxuta e o replay é controlado, auditável e restrito a administradores.

Em contrapartida, um evento pode chegar com até cerca de 15 horas de atraso, e o cliente precisa tolerar isso. A DLQ exige alguém acompanhando, porque não há alerta automático: o aviso por e-mail ao cliente ficou para uma próxima fase. Um replay pode reenviar um evento que o cliente já tinha processado, o que depende da deduplicação por `X-Event-Id` (ADR-005). O worker também precisa guardar, por evento, o número da tentativa e a data da próxima.

O trade-off é trocar a garantia de entrega eventual sem limite (retry infinito) por uma janela finita e previsível de cerca de 15 horas, com recuperação manual depois disso.

## Referências

- TRANSCRICAO.md (trechos 09:14 a 09:19, 09:35 a 09:36 e 09:42)
- src/middlewares/auth.middleware.ts:49
- src/shared/logger/index.ts:14
