# Architectural Decision Records

Este diretório armazena os ADRs (Architectural Decision Records) do projeto.
Cada decisão arquitetural relevante deve ser registrada aqui em arquivos individuais,
nomeados no formato `ADR-NNN-titulo-em-kebab-case.md` (por exemplo `ADR-001-outbox-no-mysql.md`).

## Índice — Sistema de Webhooks de Notificação de Pedidos

| ADR | Decisão | Status |
|---|---|---|
| [ADR-001](./ADR-001-outbox-no-mysql.md) | Padrão Outbox no MySQL | Aceito |
| [ADR-002](./ADR-002-worker-separado-em-polling.md) | Worker em processo separado com polling de 2s | Aceito |
| [ADR-003](./ADR-003-retry-com-backoff-e-dlq.md) | Retry com backoff exponencial e DLQ | Aceito |
| [ADR-004](./ADR-004-hmac-sha256-com-secret-por-endpoint.md) | Autenticação HMAC-SHA256 com secret por endpoint | Aceito |
| [ADR-005](./ADR-005-entrega-at-least-once-com-x-event-id.md) | Entrega at-least-once com X-Event-Id | Aceito |
| [ADR-006](./ADR-006-reuso-dos-padroes-existentes.md) | Reuso dos padrões existentes do projeto | Aceito |

Fonte das decisões: `TRANSCRICAO.md` (reunião técnica de webhooks).
