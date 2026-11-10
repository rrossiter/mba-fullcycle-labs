# RFC (Request for Comments — Pedido de Comentários) — Webhooks de Notificação de Mudança de Status de Pedidos

| Campo | Valor |
|---|---|
| **Autor** | Larissa (Tech Lead) |
| **Status** | Em revisão |
| **Data** | 2026-11-09 |
| **Revisores** | Diego (Eng. Sênior, Plataforma), Bruno (Eng. Pleno, Pedidos), Sofia (Eng. de Segurança), Marcos (Product Manager) |
| **Origem** | Reunião técnica de webhooks (`TRANSCRICAO.md`, 09:00–09:53) |
| **Documentos relacionados** | `docs/PRD.md` (PRD — Product Requirements Document / Documento de Requisitos do Produto), `docs/FDD.md` (FDD — Feature Design Document / Documento de Design da Funcionalidade), `docs/adrs/` (ADRs — Architecture Decision Records / Registros de Decisão Arquitetural) |

---

## 1. Resumo executivo (TL;DR — Too Long; Didn't Read / Longo demais; não li)

Propomos notificar sistemas de clientes B2B (Business-to-Business / empresa para empresa), via **webhooks HTTP (Hypertext Transfer Protocol / Protocolo de Transferência de Hipertexto) de saída**, sempre que o status de um pedido mudar, com latência abaixo de 10 segundos. Os principais pontos da proposta:

- **Registro do evento:** é gravado numa **tabela outbox no MySQL**, dentro da mesma transação da mudança de status.
- **Envio:** fica a cargo de um **worker em processo separado** que faz **polling a cada 2 segundos**.
- **Falhas:** o worker faz **5 tentativas com backoff exponencial** e, depois disso, move o evento para uma **DLQ (Dead Letter Queue / fila de mensagens mortas)** com replay manual por um ADMIN (papel de administrador).
- **Segurança:** cada requisição é assinada com **HMAC-SHA256** (Hash-based Message Authentication Code com Secure Hash Algorithm de 256 bits / código de autenticação de mensagem baseado em hash, com algoritmo de hash seguro de 256 bits) usando uma **secret por endpoint**.
- **Garantia de entrega:** a entrega é **at-least-once** (pelo menos uma vez), com deduplicação pelo cliente via `X-Event-Id`.
- **Implementação:** tudo é construído como **mais um módulo do monólito**, reaproveitando os padrões existentes.
- **Infraestrutura:** nenhuma nova.
- **Estimativa:** três sprints, incluindo a revisão de segurança.

## 2. Contexto e problema

Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) pediram formalmente para ser notificados em tempo real quando o status dos seus pedidos mudar. Hoje eles fazem polling periódico em `GET /orders`, o que deixa a integração lenta e cara para eles. A Atlas sinalizou que pode migrar para um concorrente se a funcionalidade não for entregue até o fim do trimestre.

Restrições que moldam a solução:

- **Latência:** abaixo de 10 segundos já conta como "tempo real" para os clientes.
- **Direção:** só saída (outbound). Os clientes recebem, não enviam.
- **Consistência:** a mudança de status ocorre numa transação já pesada em `OrderService.changeStatus` (`src/modules/orders/order.service.ts`), que atualiza o pedido, grava o histórico e mexe no estoque. Não pode existir status alterado sem evento, nem evento de uma mudança que sofreu rollback.
- **Infraestrutura:** a única infraestrutura com estado é um MySQL 8. Não há broker, cache nem filas, e o time é pequeno.
- **Segurança:** os eventos carregam dados de pedidos para fora da nossa infraestrutura. O cliente precisa conseguir verificar a origem e a integridade de cada requisição.

## 3. Proposta técnica

### 3.1 Visão geral

```
 API (processo atual)                          Worker (novo processo)
 ┌───────────────────────────────┐            ┌──────────────────────────────┐
 │ OrderService.changeStatus     │            │ polling a cada 2s            │
 │  ┌─ transação MySQL ────────┐ │            │  lê eventos pendentes        │
 │  │ update order             │ │            │  assina (HMAC-SHA256)        │
 │  │ insert status_history    │ │  MySQL     │  POST https → cliente        │
 │  │ debita/repõe estoque     │ │ ─────────► │  sucesso → entregue          │
 │  │ insert webhook_outbox    │ │  outbox    │  falha → reagenda (backoff)  │
 │  └──────────────────────────┘ │            │  5 falhas → dead-letter      │
 └───────────────────────────────┘            └──────────────────────────────┘
```

### 3.2 Componentes da proposta

1. **Registro transacional do evento (outbox).** Quando o status muda, o evento é gravado na tabela de outbox na mesma transação. O payload é gravado como snapshot do momento da mudança. Só são criados eventos para os status que algum webhook do cliente assinou: o filtro é aplicado na inserção. Ver [ADR-001](./adrs/ADR-001-outbox-no-mysql.md).
2. **Envio desacoplado (worker).** Um processo separado da API (Application Programming Interface / Interface de Programação de Aplicações), com ponto de entrada próprio, lê a outbox a cada 2 segundos e faz as chamadas HTTP com timeout de 10 segundos. Roda **um único worker**, o que garante a ordem de entrega por pedido. Ver [ADR-002](./adrs/ADR-002-worker-separado-em-polling.md).
3. **Resiliência (retry e DLQ).** São 5 tentativas, com intervalos de 1 min, 5 min, 30 min, 2 h e 12 h, cobrindo cerca de 15 horas de indisponibilidade do cliente. Depois disso, o evento vai para uma tabela de dead-letter separada, com reprocessamento manual por endpoint restrito a ADMIN e auditado. Ver [ADR-003](./adrs/ADR-003-retry-com-backoff-e-dlq.md).
4. **Autenticidade e integridade (HMAC).** O corpo da requisição é assinado com HMAC-SHA256, com uma secret única por endpoint de webhook. A secret pode ser rotacionada, e a antiga continua válida por 24 horas. Só são aceitas URLs (Uniform Resource Locator / Localizador Uniforme de Recursos) HTTPS (HTTP Secure / HTTP seguro, sobre TLS — Transport Layer Security / Segurança da Camada de Transporte). Ver [ADR-004](./adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md).
5. **Contrato de entrega (at-least-once).** Cada evento tem um id único (`X-Event-Id`) para o cliente deduplicar. O payload é enxuto, sem os itens do pedido. O cliente pode consultar o histórico das entregas. Ver [ADR-005](./adrs/ADR-005-entrega-at-least-once-com-x-event-id.md).
6. **Encaixe no código existente.** A funcionalidade vira um novo módulo `webhooks`, seguindo a mesma estrutura dos módulos atuais. Ele reaproveita a hierarquia `AppError` (códigos `WEBHOOK_*`), o middleware de erros, a validação com Zod, o logger Pino e o `requireRole`. Ver [ADR-006](./adrs/ADR-006-reuso-dos-padroes-existentes.md).

### 3.3 Superfície exposta (visão de alto nível)

- **CRUD (Create, Read, Update, Delete / criar, ler, atualizar, excluir) de configuração de webhooks** por cliente (URL, status assinados, rotação de secret). Exige um usuário autenticado.
- **Histórico de entregas** por webhook.
- **Replay da dead-letter.** Restrito ao papel ADMIN.

Os contratos detalhados (rotas, payloads, códigos de erro, modelo de dados) ficam no FDD.

## 4. Alternativas consideradas

| ID | Alternativa | Por que foi descartada (trade-off) |
|---|---|---|
| RFC-ALT-01 | **Chamada HTTP síncrona dentro de `changeStatus`** | É a solução mais simples, mas acopla a transação de pedidos à latência e à disponibilidade do cliente. Um cliente lento travaria mudanças de status de outros pedidos, e não faz sentido dar rollback na mudança de status porque o cliente está fora do ar. ([09:04] Bruno) |
| RFC-ALT-02 | **Redis Streams ou outro broker dedicado** | Escalaria melhor e tiraria a carga do banco, mas exige subir e operar infraestrutura nova. Isso foi considerado overengineering para um time pequeno, além de não ser atômico com a transação SQL. ([09:07] Larissa, [09:07] Diego) |
| RFC-ALT-03 | **Trigger do MySQL para acionar o envio** | Seria mais reativo que o polling, mas o MySQL não tem listener nativo como o `LISTEN/NOTIFY` do PostgreSQL. A trigger só executa SQL, então avisar o worker exigiria improvisos. O polling de 2s já atende o requisito de menos de 10s. ([09:09] Bruno, [09:09] Diego) |
| RFC-ALT-04 | **Retry indefinido** e **apenas 3 tentativas** | O retry indefinido deixaria eventos pendurados para sempre se o cliente sumisse. Com 3 tentativas, as chances se esgotariam em cerca de 30 minutos e se perderiam eventos de clientes em manutenção planejada, que já durou 2 horas. ([09:15] Diego, [09:16] Diego) |
| RFC-ALT-05 | **Garantia exactly-once** | Eliminaria as duplicatas no cliente, mas exige coordenação dos dois lados, com complexidade muito maior. At-least-once com id de evento é o padrão de mercado (Stripe, GitHub). ([09:25] Diego) |
| RFC-ALT-06 | **Secret global da plataforma** | Seria mais simples de gerenciar, mas o vazamento de uma única secret comprometeria todos os clientes. ([09:21] Sofia) |
| RFC-ALT-07 | **Worker no mesmo processo da API** | Dispensaria um novo processo, mas um reinício ou deploy da API derrubaria o envio. ([09:11] Diego) |

## 5. Questões em aberto

| ID | Questão | Situação na reunião | Proposta de encaminhamento |
|---|---|---|---|
| RFC-QA-01 | **Rate limiting de envio por cliente.** Devemos limitar a vazão quando muitos pedidos de um mesmo cliente mudam de status ao mesmo tempo (por exemplo, 50 por minuto)? | Adiado: "observar e decidir depois". ([09:38] Diego, [09:39] Larissa) | Medir a vazão por cliente em produção e definir um gatilho para reabrir o tema. |
| RFC-QA-02 | **Escalar para múltiplos workers.** Rodar mais de um worker em paralelo quebra a ordem de entrega por pedido. | Registrado como limitação conhecida. Particionar por `order_id` ou usar lock pessimista ficou "para o futuro". ([09:13] Diego, [09:13] Larissa) | Monitorar o backlog da outbox. Abrir um novo ADR quando um único worker não bastar. |
| RFC-QA-03 | **Aviso proativo ao cliente com falha.** Avisar por e-mail após falhas seguidas? | Fora de escopo nesta fase. Talvez numa próxima fase, depois de medir o impacto. ([09:37] Marcos, [09:37] Larissa) | Reavaliar com base no volume da DLQ. |
| RFC-QA-04 | **Arquivamento de eventos entregues.** A ideia é arquivar depois de cerca de 30 dias. | Fora do escopo desta funcionalidade. ([09:08] Diego) | Definir a política de retenção e o job de limpeza antes de a tabela crescer. |
| RFC-QA-05 | **Endurecer a autorização do CRUD de webhooks.** Hoje basta um usuário autenticado, de qualquer papel. | "Por enquanto sim. Mais pra frente a gente pode endurecer." ([09:37] Sofia) | Revisar junto com a revisão de segurança. |
| RFC-QA-06 | **Como o `customer_id` é informado no cadastro**: no corpo ou no path. | Foi decidido que não vem do JWT (JSON Web Token / token web JSON), mas a forma ficou em aberto: "no body ou no path". ([09:32] Larissa) | Fechar no FDD. |
| RFC-QA-07 | **Painel visual para o cliente.** | Fora de escopo: é um projeto separado do time de frontend. ([09:40] Larissa) | Nenhuma ação nesta entrega. |

## 6. Impacto e riscos

**Impacto no sistema existente**

- **Pedidos:** `OrderService.changeStatus` passa a gravar também na outbox. É a única mudança num fluxo existente, e é crítica: um erro ali compromete toda a garantia de entrega.
- **Banco:** o MySQL ganha novas tabelas (configuração de webhooks, outbox, dead-letter, histórico de entregas) e uma carga contínua de polling.
- **Operação:** surge um segundo processo (`worker`) para implantar e monitorar.
- **Clientes:** precisam validar a assinatura HMAC e deduplicar por `X-Event-Id`. Marcos vai documentar isso no portal do desenvolvedor.

**Riscos**

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Algum fluxo futuro mudar o status sem gravar na outbox, quebrando a garantia sem nenhum erro visível | Média | Alto | Concentrar a publicação numa única função chamada dentro da transação, com teste de integração cobrindo o commit e o rollback |
| Worker único parado, interrompendo todas as entregas | Média | Alto | Monitorar o processo e a idade do evento pendente mais antigo, e configurar reinício automático |
| Crescimento da outbox e carga de polling no MySQL principal | Média | Médio | Índices por estado e data, leitura em lotes pequenos e política de arquivamento (RFC-QA-04) |
| Cliente não deduplicar e processar o mesmo evento duas vezes | Média | Médio | `X-Event-Id` estável e documentação em destaque no portal |
| Vazamento ou falha na geração e armazenamento das secrets | Baixa | Alto | Uma secret por endpoint, rotação com prazo de transição e revisão de segurança de 2 dias úteis antes do deploy |
| Prazo: a Atlas quer a entrega até o fim de novembro, e a estimativa é de 3 sprints | Média | Alto | Fatiar a entrega (outbox e worker primeiro) e reservar a revisão de segurança no plano |

## 7. Decisões relacionadas

| ADR | Decisão |
|---|---|
| [ADR-001](./adrs/ADR-001-outbox-no-mysql.md) | Padrão Outbox no MySQL para eventos de webhook |
| [ADR-002](./adrs/ADR-002-worker-separado-em-polling.md) | Worker em processo separado com polling de 2 segundos |
| [ADR-003](./adrs/ADR-003-retry-com-backoff-e-dlq.md) | Política de retry com backoff exponencial e Dead Letter Queue |
| [ADR-004](./adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md) | Autenticação HMAC-SHA256 com secret por endpoint |
| [ADR-005](./adrs/ADR-005-entrega-at-least-once-com-x-event-id.md) | Garantia de entrega at-least-once com X-Event-Id |
| [ADR-006](./adrs/ADR-006-reuso-dos-padroes-existentes.md) | Reuso dos padrões existentes do projeto no módulo de webhooks |

## 8. Pedido de revisão

Pedimos a cada revisor que confirme ou conteste a proposta até o início da primeira sprint:

- **Diego**: outbox, worker e retry.
- **Bruno**: integração com `changeStatus` e estrutura do módulo.
- **Sofia**: HMAC, gestão de secrets e autorização.
- **Marcos**: contrato com os clientes e prazo.

Comentários sobre as questões em aberto (seção 5) são especialmente bem-vindos.
