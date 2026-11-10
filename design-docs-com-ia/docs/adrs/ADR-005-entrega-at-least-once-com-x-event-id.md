# ADR-005: Garantia de entrega at-least-once com X-Event-Id

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Related to:**
- [ADR-001: Padrão Outbox no MySQL para eventos de webhook](./ADR-001-outbox-no-mysql.md)
- [ADR-003: Política de retry com backoff exponencial e Dead Letter Queue](./ADR-003-retry-com-backoff-e-dlq.md)
- [ADR-004: Autenticação HMAC-SHA256 com secret por endpoint](./ADR-004-hmac-sha256-com-secret-por-endpoint.md)

## Status

Aceito

## Contexto

Com outbox e retry (ADR-001 e ADR-003), há situações em que o mesmo evento é enviado mais de uma vez. Por exemplo: o cliente processou a requisição, mas a resposta não chegou antes do timeout de 10 segundos, ou um administrador fez replay a partir da DLQ.

É preciso definir qual garantia de entrega a plataforma oferece, como o cliente lida com duplicatas e qual é o contrato de headers e payload de cada envio.

## Direcionadores da Decisão

- Não perder eventos confirmados.
- Manter a implementação simples e compatível com outbox e retry.
- Seguir o padrão de mercado já conhecido pelos integradores.
- Manter o payload enxuto.
- Dar ao cliente meios de deduplicar e de identificar a origem de cada envio.

## Alternativas Consideradas

1. At-least-once com UUID do evento no header `X-Event-Id` (opção escolhida)
2. Exactly-once
3. At-most-once (envio único, sem retry)

## Decisão

Opção escolhida: "At-least-once com UUID do evento no header `X-Event-Id`", porque garante que nenhum evento confirmado se perca e deixa a deduplicação para o cliente com um identificador estável. É o mesmo modelo adotado por Stripe e GitHub.

Detalhes da decisão:

- Cada evento recebe um UUID gerado na inserção na outbox, enviado em `X-Event-Id`.
- O contrato de headers é:
  - `X-Event-Id`;
  - `X-Signature` (ADR-004);
  - `X-Timestamp`, com o momento do envio;
  - `X-Webhook-Id`, que identifica o cadastro do endpoint;
  - `Content-Type: application/json`.
- O payload é enxuto: `event_id`, `event_type` (`order.status_changed`), timestamp ISO 8601, `order_id`, `order_number`, `from_status`, `to_status`, `customer_id` e campos básicos como `total_cents`. Os itens do pedido não são enviados; quem precisar deles consulta `GET /orders/:id`.
- O payload tem limite de 64KB. Acima disso, o envio gera erro, sem truncar.
- O cliente consulta o histórico de entregas em `GET /webhooks/:id/deliveries`.
- A semântica de duplicatas será documentada em destaque no portal do desenvolvedor.

## Prós e Contras das Opções

### At-least-once com X-Event-Id

- Bom, porque nenhum evento confirmado se perde dentro da janela de retry.
- Bom, porque é simples de implementar e compatível com outbox e retry.
- Bom, porque é o padrão de mercado, familiar para os integradores.
- Ruim, porque a responsabilidade de deduplicar fica com o cliente.

### Exactly-once

- Bom, porque o cliente nunca receberia duplicatas.
- Ruim, porque exigiria coordenação dos dois lados, com complexidade muito maior.

### At-most-once

- Bom, porque não há duplicatas nem fila de retry.
- Ruim, porque eventos se perdem sempre que o cliente está indisponível, o que contradiz o objetivo de substituir o polling.

## Consequências

Nenhum evento confirmado se perde dentro da janela de retry, o contrato é familiar para quem já integra com Stripe ou GitHub e o payload enxuto reduz banda e exposição de dados.

Em contrapartida, um cliente que não implementar a deduplicação pode processar o mesmo evento duas vezes. O payload enxuto obriga o cliente a uma chamada extra quando precisa dos itens. Os headers e o formato do payload passam a ser uma API pública, e qualquer mudança exigirá uma estratégia de versionamento que ainda não foi definida.

O trade-off é aceitar duplicidade possível, com o custo da deduplicação ficando com o cliente, em troca de simplicidade e de não perder eventos. O risco é mitigado pelo `X-Event-Id` estável e pela documentação no portal.

## Referências

- TRANSCRICAO.md (trechos 09:23 a 09:26, 09:34 a 09:35 e 09:43 a 09:45)
