# ADR-001: Padrão Outbox no MySQL para eventos de webhook

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Used by:**
- [ADR-002: Worker em processo separado com polling de 2 segundos](./ADR-002-worker-separado-em-polling.md)
- [ADR-003: Política de retry com backoff exponencial e Dead Letter Queue](./ADR-003-retry-com-backoff-e-dlq.md)

**Related to:**
- [ADR-005: Garantia de entrega at-least-once com X-Event-Id](./ADR-005-entrega-at-least-once-com-x-event-id.md)
- [ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks](./ADR-006-reuso-dos-padroes-existentes.md)

## Status

Aceito

## Contexto

Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) pediram para ser notificados quando o status dos seus pedidos muda, com latência abaixo de 10 segundos. Hoje eles fazem polling em `GET /orders`, o que deixa a integração lenta e cara. A Atlas sinalizou que pode migrar para um concorrente se a funcionalidade não for entregue até o fim do trimestre.

A mudança de status acontece no método `changeStatus` do serviço de pedidos, dentro de uma única transação Prisma que atualiza o pedido, insere em `order_status_history` e debita ou repõe o estoque. O evento de webhook precisa ser consistente com essa transação: não pode ser enviado se a mudança sofrer rollback, e não pode ser perdido se ela for confirmada.

O MySQL 8.0 é a única infraestrutura com estado do projeto. Não há broker de mensagens nem cache distribuído, e o time é pequeno.

## Direcionadores da Decisão

- Garantir atomicidade entre a mudança de status do pedido e o registro do evento.
- Não bloquear nem atrasar a transação de pedidos por causa da latência ou da indisponibilidade de clientes externos.
- Evitar novos componentes de infraestrutura para uma equipe pequena.
- Atender a latência de entrega abaixo de 10 segundos pedida pelos clientes.
- Não gerar eventos para clientes que não assinaram o status em questão.

## Alternativas Consideradas

1. Outbox transacional no próprio MySQL, com envio feito por um worker separado (opção escolhida)
2. Chamada HTTP síncrona dentro do serviço de pedidos
3. Fila externa baseada em Redis Streams (ou broker equivalente)
4. Trigger no MySQL notificando o processo de envio

## Decisão

Opção escolhida: "Outbox transacional no próprio MySQL", porque garante, na mesma transação SQL da mudança de status, que o evento exista se e somente se a mudança for confirmada. Se a transação sofrer rollback, o evento some junto; se a gravação do evento falhar, a mudança de status é revertida. A opção reaproveita a única infraestrutura existente e deixa o envio HTTP a cargo de um worker independente.

Decisões complementares tomadas na mesma discussão:

- A gravação usa uma função `publishWebhookEvent(tx, order, fromStatus, toStatus)`, que recebe o cliente transacional corrente, em vez de injetar um repositório inteiro no serviço de pedidos.
- O payload é gravado como snapshot renderizado no momento da inserção.
- O filtro de eventos é aplicado na inserção: se nenhum webhook do cliente assina o status de destino, nenhuma linha é criada.
- Os identificadores são UUID, seguindo o padrão do projeto.
- A tabela é indexada por estado de entrega (pendente, processando, falhou, entregue) e por data de criação.

O arquivamento das linhas entregues (cerca de 30 dias) fica fora do escopo desta decisão.

## Prós e Contras das Opções

### Outbox transacional no MySQL

- Bom, porque garante atomicidade entre mudança de status e evento.
- Bom, porque não exige infraestrutura além do MySQL já existente.
- Bom, porque isola falhas e lentidão de clientes externos da transação de pedidos.
- Ruim, porque usa o banco principal como fila, com carga de polling e crescimento contínuo da tabela.

### Chamada HTTP síncrona no serviço

- Bom, porque é a implementação mais simples, sem componentes adicionais.
- Ruim, porque um cliente lento trava mudanças de status de outros pedidos.
- Ruim, porque não faz sentido reverter a mudança de status quando o cliente está fora do ar.

### Redis Streams / broker externo

- Bom, porque separa a fila do banco principal e escala melhor para alto volume.
- Ruim, porque exige subir e operar nova infraestrutura (por exemplo Redis Cluster), o que é overengineering para um time pequeno.
- Ruim, porque não oferece atomicidade nativa com a transação SQL.

### Trigger no MySQL

- Bom, porque reagiria imediatamente à mudança de status.
- Ruim, porque triggers só executam SQL e não conseguem notificar um processo externo.

## Consequências

O principal benefício é a consistência: a divergência entre o status do pedido e a notificação deixa de ser possível, sem nenhum componente operacional novo. O snapshot garante que o cliente recebe o estado do momento da mudança, mesmo que o pedido mude de novo antes do envio.

Em contrapartida, o banco principal passa a funcionar também como fila: cresce continuamente e recebe a carga do polling do worker. A transação de `changeStatus` fica um pouco mais longa. Qualquer código que altere o status de pedidos passa a ter a obrigação de gravar o evento dentro da transação, e omitir essa etapa quebra a garantia sem nenhum erro visível. O snapshot também dificulta mudar o formato de eventos já enfileirados.

O trade-off é trocar a escalabilidade e o isolamento de um broker dedicado por consistência transacional forte e zero infraestrutura nova. Para o volume atual (três clientes B2B), a carga extra no MySQL é aceitável. Se a outbox passar a pressionar o banco principal, a decisão deve ser revista em favor de um broker.

## Referências

- TRANSCRICAO.md (trechos 09:03 a 09:08, 09:40 a 09:41 e 09:51 a 09:52)
- src/modules/orders/order.service.ts:126
- prisma/schema.prisma
- docker-compose.yml
