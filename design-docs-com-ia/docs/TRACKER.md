# Tracker de Rastreabilidade

Mapeia cada item dos documentos do pacote à sua origem na transcrição da reunião (`TRANSCRICAO.md`) ou no código base. Itens sem origem identificável foram marcados como **(hipótese)** nos documentos e estão listados à parte, no fim deste arquivo.

## Tabela

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |
| PRD-PROB-01 | docs/PRD.md | Problema | Clientes B2B fazem polling em GET /orders, integração lenta e cara | TRANSCRICAO | [09:00] Marcos |
| PRD-PROB-02 | docs/PRD.md | Problema | Atlas pode migrar para concorrente se não houver entrega no trimestre | TRANSCRICAO | [09:00] Marcos |
| PRD-PROB-03 | docs/PRD.md | Problema | Envio síncrono travaria a mudança de status e não permite rollback coerente | TRANSCRICAO | [09:04] Bruno |
| PRD-PUB-01 | docs/PRD.md | Público-alvo | Clientes B2B Atlas Comercial, MaxDistribuição e Nova Cargo | TRANSCRICAO | [09:00] Marcos |
| PRD-PUB-02 | docs/PRD.md | Público-alvo | Usuários internos que representam o cliente configuram webhooks via API | TRANSCRICAO | [09:32] Marcos |
| PRD-CEN-01 | docs/PRD.md | Cenário de uso | Cliente escolhe receber só alguns status (ex.: SHIPPED, DELIVERED) | TRANSCRICAO | [09:33] Marcos |
| PRD-CEN-02 | docs/PRD.md | Cenário de uso | Cliente em manutenção de 2 horas recebe eventos depois, sem perda | TRANSCRICAO | [09:16] Diego |
| PRD-CEN-03 | docs/PRD.md | Cenário de uso | Cliente valida que a requisição veio da plataforma e não foi adulterada | TRANSCRICAO | [09:19] Sofia |
| PRD-IMPL-01 | docs/PRD.md | Restrição | Feature implantada no sistema existente, com worker separado no mesmo banco | TRANSCRICAO | [09:11] Larissa |
| PRD-OBJ-01 | docs/PRD.md | Objetivo | Latência abaixo de 10 s é considerada "tempo real" pelos clientes | TRANSCRICAO | [09:02] Marcos |
| PRD-OBJ-02 | docs/PRD.md | Objetivo | Nenhuma mudança de status pode ficar sem evento | TRANSCRICAO | [09:40] Bruno |
| PRD-OBJ-05 | docs/PRD.md | Objetivo | Atender os três clientes que fizeram o pedido formal | TRANSCRICAO | [09:00] Marcos |
| PRD-ESC-01 | docs/PRD.md | Escopo | Webhooks são somente de saída (outbound) | TRANSCRICAO | [09:02] Marcos |
| PRD-FORA-01 | docs/PRD.md | Fora de escopo | Aviso por e-mail ao cliente em falhas adiado para próxima fase | TRANSCRICAO | [09:37] Larissa |
| PRD-FORA-02 | docs/PRD.md | Fora de escopo | Dashboard visual fora de escopo, projeto do time de frontend | TRANSCRICAO | [09:40] Larissa |
| PRD-FORA-03 | docs/PRD.md | Fora de escopo | Rate limiting de envio: observar e decidir depois | TRANSCRICAO | [09:39] Larissa |
| PRD-FORA-04 | docs/PRD.md | Fora de escopo | Múltiplos workers e ordenação global ficam para o futuro | TRANSCRICAO | [09:13] Larissa |
| PRD-FORA-05 | docs/PRD.md | Fora de escopo | Arquivamento de eventos entregues (cerca de 30 dias) fora do escopo | TRANSCRICAO | [09:08] Diego |
| PRD-FORA-06 | docs/PRD.md | Fora de escopo | Webhooks de entrada (inbound) descartados | TRANSCRICAO | [09:02] Marcos |
| PRD-FORA-07 | docs/PRD.md | Fora de escopo | Endurecer permissões do CRUD de webhooks adiado | TRANSCRICAO | [09:37] Sofia |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | Cadastrar webhook com URL e status de interesse; secret gerada e devolvida na criação | TRANSCRICAO | [09:31] Marcos |
| PRD-FR-02 | docs/PRD.md | Requisito Funcional | Listar webhooks de um cliente | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-03 | docs/PRD.md | Requisito Funcional | Editar webhook (PATCH) | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-04 | docs/PRD.md | Requisito Funcional | Remover webhook (DELETE) | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-05 | docs/PRD.md | Requisito Funcional | Registrar evento na mesma transação da mudança de status | TRANSCRICAO | [09:06] Diego |
| PRD-FR-05a | docs/PRD.md | Regra de negócio | Filtrar eventos na inserção: sem assinante, nenhuma linha | TRANSCRICAO | [09:34] Bruno |
| PRD-FR-05b | docs/PRD.md | Regra de negócio | Payload gravado como snapshot no momento da mudança | TRANSCRICAO | [09:52] Larissa |
| PRD-FR-06 | docs/PRD.md | Requisito Funcional | Enviar notificação assinada com X-Event-Id, X-Signature, X-Timestamp | TRANSCRICAO | [09:44] Diego |
| PRD-FR-06a | docs/PRD.md | Requisito Funcional | Header X-Webhook-Id identifica o cadastro de origem | TRANSCRICAO | [09:44] Sofia |
| PRD-FR-07 | docs/PRD.md | Requisito Funcional | Retentar com backoff 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Larissa |
| PRD-FR-08 | docs/PRD.md | Requisito Funcional | Mover para DLQ em tabela separada com payload, motivo e timestamp | TRANSCRICAO | [09:18] Diego |
| PRD-FR-08a | docs/PRD.md | Requisito Funcional | Replay manual da DLQ via endpoint admin | TRANSCRICAO | [09:18] Diego |
| PRD-FR-09 | docs/PRD.md | Requisito Funcional | Rotacionar secret; antiga válida por 24 h | TRANSCRICAO | [09:21] Sofia |
| PRD-FR-10 | docs/PRD.md | Requisito Funcional | Histórico de entregas: sucesso/falha, payload, resposta, tempo, últimas 100 | TRANSCRICAO | [09:34] Marcos |
| PRD-RNF-01 | docs/PRD.md | Requisito Não Funcional | Polling de 2 s atende o limite de 10 s | TRANSCRICAO | [09:10] Larissa |
| PRD-RNF-02 | docs/PRD.md | Requisito Não Funcional | Timeout de 10 s por chamada ao cliente | TRANSCRICAO | [09:42] Diego |
| PRD-RNF-03 | docs/PRD.md | Requisito Não Funcional | URL obrigatoriamente HTTPS, validada no schema Zod | TRANSCRICAO | [09:23] Sofia |
| PRD-RNF-04 | docs/PRD.md | Requisito Não Funcional | Limite de 64 KB por payload, com erro se ultrapassar | TRANSCRICAO | [09:24] Larissa |
| PRD-RNF-05 | docs/PRD.md | Requisito Não Funcional | Replay exige papel ADMIN e registra quem executou | TRANSCRICAO | [09:36] Sofia |
| PRD-RNF-06 | docs/PRD.md | Requisito Não Funcional | Logs com o Pino já existente, sem nova biblioteca | TRANSCRICAO | [09:29] Bruno |
| PRD-RNF-07 | docs/PRD.md | Requisito Não Funcional | Endpoints sob /api/v1 no padrão REST JSON existente | CODIGO | src/app.ts |
| PRD-DEP-01 | docs/PRD.md | Dependência | Revisão de segurança com dois dias úteis antes do deploy | TRANSCRICAO | [09:46] Sofia |
| PRD-DEP-02 | docs/PRD.md | Dependência | Documentação de deduplicação no portal do desenvolvedor | TRANSCRICAO | [09:26] Marcos |
| PRD-DEP-03 | docs/PRD.md | Dependência | Clientes precisam deduplicar pelo event_id | TRANSCRICAO | [09:25] Diego |
| PRD-RISCO-01 | docs/PRD.md | Risco | Prazo: Atlas quer para fim de novembro, estimativa de três sprints | TRANSCRICAO | [09:46] Larissa |
| PRD-RISCO-04 | docs/PRD.md | Risco | Vazamento de secret: cliente já vazou secret em log | TRANSCRICAO | [09:22] Diego |
| PRD-VAL-01 | docs/PRD.md | Validação | Sessão de revisão do design com Bruno e Diego antes de codar | TRANSCRICAO | [09:50] Larissa |
| PRD-TEST-01 | docs/PRD.md | Teste | Testes de integração contra MySQL real, padrão já usado | CODIGO | tests/setup.ts |
| RFC-PROP-01 | docs/RFC.md | Decisão | Outbox no MySQL na mesma transação da mudança de status | TRANSCRICAO | [09:08] Larissa |
| RFC-PROP-02 | docs/RFC.md | Decisão | Worker em processo separado com polling de 2 s | TRANSCRICAO | [09:10] Larissa |
| RFC-PROP-03 | docs/RFC.md | Decisão | 5 tentativas com backoff e DLQ com replay ADMIN | TRANSCRICAO | [09:17] Larissa |
| RFC-PROP-04 | docs/RFC.md | Decisão | HMAC-SHA256, secret por endpoint, rotação com 24 h | TRANSCRICAO | [09:22] Sofia |
| RFC-PROP-05 | docs/RFC.md | Decisão | At-least-once com X-Event-Id | TRANSCRICAO | [09:26] Larissa |
| RFC-PROP-06 | docs/RFC.md | Decisão | Reuso máximo dos padrões do projeto em módulo webhooks | TRANSCRICAO | [09:30] Larissa |
| RFC-ESTIM-01 | docs/RFC.md | Restrição | Estimativa de três sprints incluindo revisão de segurança | TRANSCRICAO | [09:47] Larissa |
| RFC-ALT-01 | docs/RFC.md | Alternativa descartada | HTTP síncrono no changeStatus: cliente lento trava outros pedidos | TRANSCRICAO | [09:04] Bruno |
| RFC-ALT-02 | docs/RFC.md | Alternativa descartada | Redis Streams ou broker: exige infra nova, overengineering | TRANSCRICAO | [09:07] Diego |
| RFC-ALT-03 | docs/RFC.md | Alternativa descartada | Trigger do MySQL não notifica processo externo | TRANSCRICAO | [09:09] Diego |
| RFC-ALT-04 | docs/RFC.md | Alternativa descartada | 3 tentativas é pouco; retry indefinido deixa eventos pendurados | TRANSCRICAO | [09:16] Diego |
| RFC-ALT-05 | docs/RFC.md | Alternativa descartada | Exactly-once exige coordenação dos dois lados | TRANSCRICAO | [09:25] Diego |
| RFC-ALT-06 | docs/RFC.md | Alternativa descartada | Secret global: se vaza uma, vaza tudo | TRANSCRICAO | [09:21] Sofia |
| RFC-ALT-07 | docs/RFC.md | Alternativa descartada | Worker no processo da API: reinício da API derruba o worker | TRANSCRICAO | [09:11] Diego |
| RFC-QA-01 | docs/RFC.md | Questão em aberto | Rate limiting de envio por cliente | TRANSCRICAO | [09:38] Diego |
| RFC-QA-02 | docs/RFC.md | Questão em aberto | Escalar para múltiplos workers (particionar por order_id ou lock) | TRANSCRICAO | [09:13] Diego |
| RFC-QA-03 | docs/RFC.md | Questão em aberto | Aviso proativo por e-mail ao cliente com falha | TRANSCRICAO | [09:37] Marcos |
| RFC-QA-04 | docs/RFC.md | Questão em aberto | Política de arquivamento de eventos entregues | TRANSCRICAO | [09:08] Diego |
| RFC-QA-05 | docs/RFC.md | Questão em aberto | Endurecer autorização do CRUD de webhooks | TRANSCRICAO | [09:37] Sofia |
| RFC-QA-06 | docs/RFC.md | Questão em aberto | customer_id no body ou no path (não vem do JWT) | TRANSCRICAO | [09:32] Larissa |
| RFC-QA-07 | docs/RFC.md | Questão em aberto | Painel visual para o cliente | TRANSCRICAO | [09:39] Marcos |
| RFC-IMP-01 | docs/RFC.md | Impacto | changeStatus é o único fluxo existente alterado | CODIGO | src/modules/orders/order.service.ts |
| ADR-001 | docs/adrs/ADR-001-outbox-no-mysql.md | Decisão | Padrão Outbox no MySQL para eventos de webhook | TRANSCRICAO | [09:06] Diego |
| ADR-001-TO | docs/adrs/ADR-001-outbox-no-mysql.md | Trade-off | Banco principal vira fila; índices em status e created_at | TRANSCRICAO | [09:08] Diego |
| ADR-001-COD | docs/adrs/ADR-001-outbox-no-mysql.md | Contexto | Transação de changeStatus atualiza pedido, histórico e estoque | CODIGO | src/modules/orders/order.service.ts |
| ADR-001-UUID | docs/adrs/ADR-001-outbox-no-mysql.md | Decisão | Ids da outbox em UUID, padrão do projeto | TRANSCRICAO | [09:51] Larissa |
| ADR-002 | docs/adrs/ADR-002-worker-separado-em-polling.md | Decisão | Worker separado com polling de 2 s | TRANSCRICAO | [09:09] Diego |
| ADR-002-ENT | docs/adrs/ADR-002-worker-separado-em-polling.md | Decisão | Novo entry point src/worker.ts e script npm run worker | TRANSCRICAO | [09:11] Larissa |
| ADR-002-ORD | docs/adrs/ADR-002-worker-separado-em-polling.md | Trade-off | Single-worker: ordem só por order_id | TRANSCRICAO | [09:12] Diego |
| ADR-002-COD | docs/adrs/ADR-002-worker-separado-em-polling.md | Contexto | Entry point atual da API usado como referência | CODIGO | src/server.ts |
| ADR-003 | docs/adrs/ADR-003-retry-com-backoff-e-dlq.md | Decisão | 5 tentativas com backoff exponencial e DLQ | TRANSCRICAO | [09:17] Diego |
| ADR-003-DLQ | docs/adrs/ADR-003-retry-com-backoff-e-dlq.md | Decisão | DLQ em tabela separada webhook_dead_letter | TRANSCRICAO | [09:18] Diego |
| ADR-003-TO | docs/adrs/ADR-003-retry-com-backoff-e-dlq.md | Trade-off | Cliente fora por 15 h já tem problema sério; janela aceitável | TRANSCRICAO | [09:17] Marcos |
| ADR-003-COD | docs/adrs/ADR-003-retry-com-backoff-e-dlq.md | Reuso | Replay protegido por requireRole existente | CODIGO | src/middlewares/auth.middleware.ts |
| ADR-004 | docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md | Decisão | HMAC-SHA256 sobre o corpo, header X-Signature | TRANSCRICAO | [09:20] Sofia |
| ADR-004-CFG | docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md | Decisão | Tabela de configuração com url, secret, customer_id e ativo | TRANSCRICAO | [09:21] Bruno |
| ADR-004-COD | docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md | Reuso | Validação HTTPS via middleware Zod existente | CODIGO | src/middlewares/validate.middleware.ts |
| ADR-005 | docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md | Decisão | Garantia at-least-once com deduplicação por X-Event-Id | TRANSCRICAO | [09:24] Diego |
| ADR-005-TO | docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md | Trade-off | Responsabilidade de deduplicar passa para o cliente | TRANSCRICAO | [09:25] Sofia |
| ADR-005-PAY | docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md | Decisão | Payload enxuto, sem items; detalhes via GET /orders/:id | TRANSCRICAO | [09:43] Diego |
| ADR-006 | docs/adrs/ADR-006-reuso-dos-padroes-existentes.md | Decisão | Módulo src/modules/webhooks no padrão controller/service/repository | TRANSCRICAO | [09:27] Bruno |
| ADR-006-ERR | docs/adrs/ADR-006-reuso-dos-padroes-existentes.md | Decisão | Erros estendem AppError com prefixo WEBHOOK_ | TRANSCRICAO | [09:29] Larissa |
| ADR-006-COD1 | docs/adrs/ADR-006-reuso-dos-padroes-existentes.md | Reuso | Classe base AppError | CODIGO | src/shared/errors/app-error.ts |
| ADR-006-COD2 | docs/adrs/ADR-006-reuso-dos-padroes-existentes.md | Reuso | Middleware de erro centralizado sem alteração | CODIGO | src/middlewares/error.middleware.ts |
| ADR-006-COD3 | docs/adrs/ADR-006-reuso-dos-padroes-existentes.md | Reuso | Logger Pino compartilhado | CODIGO | src/shared/logger/index.ts |
| FDD-FLUXO-01 | docs/FDD.md | Fluxo | Criação do evento na outbox dentro de changeStatus | TRANSCRICAO | [09:40] Bruno |
| FDD-FLUXO-02 | docs/FDD.md | Fluxo | Worker lê pendentes em lote pequeno e marca entregues | TRANSCRICAO | [09:08] Diego |
| FDD-FLUXO-03 | docs/FDD.md | Fluxo | Retry: tenta de novo com intervalo crescente até um teto | TRANSCRICAO | [09:15] Diego |
| FDD-FLUXO-04 | docs/FDD.md | Fluxo | DLQ com payload, motivo da falha e timestamp | TRANSCRICAO | [09:18] Diego |
| FDD-FLUXO-05 | docs/FDD.md | Fluxo | Replay recoloca o evento na outbox como pendente | TRANSCRICAO | [09:18] Diego |
| FDD-FUNC-01 | docs/FDD.md | Contrato | Função publishWebhookEvent(tx, order, fromStatus, toStatus) | TRANSCRICAO | [09:41] Bruno |
| FDD-CONTRATO-01 | docs/FDD.md | Contrato | POST /webhooks cria webhook e devolve a secret | TRANSCRICAO | [09:31] Marcos |
| FDD-CONTRATO-02 | docs/FDD.md | Contrato | GET /webhooks lista por cliente | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-03 | docs/FDD.md | Contrato | PATCH /webhooks/:id edita | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-04 | docs/FDD.md | Contrato | DELETE /webhooks/:id remove | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-05 | docs/FDD.md | Contrato | Endpoint de rotação de secret pela API | TRANSCRICAO | [09:21] Sofia |
| FDD-CONTRATO-06 | docs/FDD.md | Contrato | GET /webhooks/:id/deliveries | TRANSCRICAO | [09:34] Marcos |
| FDD-CONTRATO-07 | docs/FDD.md | Contrato | POST /admin/webhooks/dead-letter/:id/replay | TRANSCRICAO | [09:35] Diego |
| FDD-CONTRATO-08 | docs/FDD.md | Contrato | Payload: event_id, event_type, timestamp, order_id, order_number, status, customer_id, total_cents | TRANSCRICAO | [09:43] Diego |
| FDD-CONTRATO-08a | docs/FDD.md | Contrato | Headers X-Event-Id, X-Signature, X-Timestamp, Content-Type | TRANSCRICAO | [09:44] Diego |
| FDD-PAG-01 | docs/FDD.md | Contrato | Listagem no formato { data, pagination } já usado | CODIGO | src/shared/http/response.ts |
| FDD-ERRO-01 | docs/FDD.md | Erro | WEBHOOK_NOT_FOUND | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-02 | docs/FDD.md | Erro | WEBHOOK_INVALID_URL | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-03 | docs/FDD.md | Erro | WEBHOOK_SECRET_REQUIRED | TRANSCRICAO | [09:28] Bruno |
| FDD-ERRO-06 | docs/FDD.md | Erro | WEBHOOK_PAYLOAD_TOO_LARGE (limite 64 KB, erra em vez de truncar) | TRANSCRICAO | [09:23] Sofia |
| FDD-ERRO-10 | docs/FDD.md | Erro | WEBHOOK_DELIVERY_TIMEOUT após 10 s | TRANSCRICAO | [09:42] Diego |
| FDD-ERRO-13 | docs/FDD.md | Erro | WEBHOOK_OUTBOX_WRITE_FAILED causa rollback | TRANSCRICAO | [09:40] Bruno |
| FDD-ERRO-BASE | docs/FDD.md | Reuso | Hierarquia de erros HTTP (NotFound, BadRequest, Conflict) estendida | CODIGO | src/shared/errors/http-errors.ts |
| FDD-RES-01 | docs/FDD.md | Resiliência | Timeout de 10 s | TRANSCRICAO | [09:42] Diego |
| FDD-RES-02 | docs/FDD.md | Resiliência | Backoff 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Diego |
| FDD-RES-03 | docs/FDD.md | Resiliência | Fallback: DLQ e replay manual | TRANSCRICAO | [09:18] Diego |
| FDD-OBS-01 | docs/FDD.md | Observabilidade | Log de auditoria do replay com quem executou | TRANSCRICAO | [09:36] Sofia |
| FDD-OBS-02 | docs/FDD.md | Observabilidade | Logs estruturados com Pino | CODIGO | src/shared/logger/index.ts |
| FDD-DEP-01 | docs/FDD.md | Dependência | Node >= 20, Prisma 5.22, Express 4.21, Zod 3.23, Pino 9.5 | CODIGO | package.json |
| FDD-DEP-02 | docs/FDD.md | Dependência | MySQL 8 como único datastore | CODIGO | docker-compose.yml |
| FDD-INT-01 | docs/FDD.md | Integração | changeStatus estendido com publishWebhookEvent | CODIGO | src/modules/orders/order.service.ts |
| FDD-INT-02 | docs/FDD.md | Integração | Novos erros como subclasses de AppError | CODIGO | src/shared/errors/app-error.ts |
| FDD-INT-03 | docs/FDD.md | Integração | errorMiddleware converte erros WEBHOOK_ sem alteração | CODIGO | src/middlewares/error.middleware.ts |
| FDD-INT-04 | docs/FDD.md | Integração | authenticate e requireRole('ADMIN') nas rotas | CODIGO | src/middlewares/auth.middleware.ts |
| FDD-INT-05 | docs/FDD.md | Integração | Router registra /webhooks e /admin/webhooks | CODIGO | src/routes/index.ts |
| FDD-INT-06 | docs/FDD.md | Integração | buildControllers instancia o módulo webhooks | CODIGO | src/app.ts |
| FDD-INT-07 | docs/FDD.md | Integração | Worker cria seu próprio PrismaClient | TRANSCRICAO | [09:30] Bruno |
| FDD-INT-08 | docs/FDD.md | Integração | Criação do PrismaClient reutilizada pelo worker | CODIGO | src/config/database.ts |
| FDD-INT-09 | docs/FDD.md | Integração | Variáveis WEBHOOK_* no schema de ambiente | CODIGO | src/config/env.ts |
| FDD-INT-10 | docs/FDD.md | Integração | Novos modelos Prisma com UUID e @@map snake_case | CODIGO | prisma/schema.prisma |
| FDD-INT-11 | docs/FDD.md | Integração | Limpeza das novas tabelas no beforeEach dos testes | CODIGO | tests/setup.ts |
| FDD-INT-12 | docs/FDD.md | Integração | Lógica do worker em arquivo do módulo (webhook.processor.ts) | TRANSCRICAO | [09:28] Bruno |

## Resumo de cobertura

| Medida | Valor |
| --- | --- |
| Linhas na tabela | 135 |
| Linhas com Fonte = TRANSCRICAO | 110 (81%) |
| Linhas com Fonte = CODIGO | 25 |
| Caminhos de código distintos citados | 17 |

## Itens sem origem identificável (hipóteses)

Estes itens aparecem nos documentos marcados como **(hipótese)**. Não têm linha na tabela porque não foram ditos na reunião nem existem no código; precisam ser validados pela equipe antes de virar decisão.

- docs/PRD.md: meta de 99% de entregas na janela de retry (PRD-OBJ-03); redução de 80% do polling (PRD-OBJ-04); disponibilidade de 99.9%; ferramenta de tracing; alerta de 60 s; forma de implantação do worker; validação em homologação com a Atlas; recusa de nova rotação durante o grace period.
- docs/FDD.md: lote de 20 eventos por ciclo; recuperação de linhas presas em PROCESSING após 60 s; estado CANCELLED para endpoints inativos ou removidos; formato `sha256=<hex>` e duas assinaturas durante a rotação; rota `rotate-secret`; `customer_id` no body e na query; códigos WEBHOOK_INVALID_EVENTS, WEBHOOK_CUSTOMER_NOT_FOUND, WEBHOOK_ROTATION_IN_PROGRESS, WEBHOOK_DEAD_LETTER_NOT_FOUND, WEBHOOK_ALREADY_REPLAYED; nomes das variáveis WEBHOOK_*; prom-client e OpenTelemetry; amostragem de tracing.
