### PRD: Order Management System (OMS) Webhooks de Notificação de Pedidos

Versão: 1.0
Data: 2026-11-09
Responsável: Marcos (Product Manager)

> PRD (Product Requirements Document / Documento de Requisitos do Produto). Este documento responde **por que** a feature existe, **o que** ela precisa fazer e **como saber que está pronta**. A proposta técnica está no [RFC](./RFC.md), as decisões nos [ADRs](./adrs/README.md) e o detalhe de implementação no [FDD](./FDD.md). Itens marcados com **(hipótese)** não foram definidos na reunião e precisam de validação.

---

### Resumo e contexto da feature

Clientes B2B (Business-to-Business / empresa para empresa) do OMS precisam saber, em quase tempo real, quando o status dos seus pedidos muda. Hoje eles descobrem isso consultando a API periodicamente. A feature cria **webhooks de saída**: a cada mudança de status de um pedido, a plataforma envia uma notificação HTTPS assinada para a URL cadastrada pelo cliente, em menos de 10 segundos, com retentativas automáticas quando o cliente está indisponível. A feature roda dentro do sistema existente (`order-management-api`), sem nova infraestrutura.

---

### Público-alvo e cenários de uso

Público-alvo
- Clientes B2B integrados via API: Atlas Comercial, MaxDistribuição e Nova Cargo ([09:00] Marcos).
- Usuários internos que configuram webhooks em nome dos clientes (papéis ADMIN e OPERATOR) ([09:32] Marcos).
- Administradores da plataforma que acompanham e reprocessam falhas de entrega ([09:36] Sofia).

Cenários de uso chave
- Um pedido muda para SHIPPED e o sistema do cliente é avisado em segundos, sem precisar consultar a API.
- O cliente escolhe receber só alguns status (por exemplo SHIPPED e DELIVERED) ([09:33] Marcos).
- O sistema do cliente fica fora do ar por duas horas em manutenção e recebe os eventos depois, sem perda ([09:16] Diego).
- O cliente verifica que a notificação veio da plataforma e não foi alterada no caminho ([09:19] Sofia).
- O cliente consulta o histórico das últimas entregas para investigar um problema ([09:34] Marcos).

---

### Problema e motivação

Onde essa feature será implantada
- Sistema existente: o monólito `order-management-api` (Node.js, Express, Prisma, MySQL 8), como um novo módulo `webhooks` e um processo worker separado que usa o mesmo banco ([09:11] Larissa, [09:27] Bruno).

Problemas priorizados
- **Integração lenta e cara por polling:** os clientes consultam `GET /orders` de tempos em tempos para detectar mudanças, o que atrasa a reação deles e gera custo para os dois lados. Prioridade alta ([09:00] Marcos).
- **Risco comercial:** a Atlas sinalizou que pode migrar para um concorrente se a funcionalidade não for entregue até o fim do trimestre. Prioridade alta ([09:00] Marcos).
- **Ausência de garantia de entrega:** sem um mecanismo próprio, uma notificação perdida ou enviada para uma mudança desfeita levaria a dados inconsistentes no cliente. Prioridade alta ([09:04] Bruno, [09:06] Diego).

---

### Objetivos e métricas de sucesso

| Objetivo | Métrica | Meta |
| --- | --- | --- |
| Notificar o cliente em "tempo real" | Latência p95 entre a mudança de status e a primeira tentativa de envio | Menor que 10 s ([09:02] Marcos) |
| Garantir que nenhuma mudança de status se perca | Percentual de eventos entregues ou enviados à DLQ (Dead Letter Queue / fila de mensagens mortas), sem perda silenciosa | 100% |
| Entregar com confiabilidade para clientes disponíveis | Taxa de eventos entregues dentro da janela de retentativas (cerca de 15 h) | Maior ou igual a 99% **(hipótese)** |
| Substituir o polling dos clientes integrados | Número de chamadas `GET /orders` feitas pelos três clientes, 30 dias após a adoção | Redução de pelo menos 80% **(hipótese)** |
| Reter os clientes que pediram a feature | Clientes com webhook ativo em produção | 3 de 3 (Atlas, MaxDistribuição, Nova Cargo) |

---

### Escopo

Incluso
- Cadastro, listagem, edição e remoção de webhooks por cliente, com escolha dos status de interesse.
- Geração de uma secret por webhook e rotação com período de transição de 24 h.
- Notificação a cada mudança de status de pedido, registrada de forma atômica com a mudança.
- Envio HTTPS assinado com HMAC-SHA256, com `X-Event-Id` para deduplicação.
- Retentativas com backoff de 1 min, 5 min, 30 min, 2 h e 12 h, e envio à DLQ depois disso.
- Reprocessamento manual da DLQ por ADMIN, com auditoria.
- Histórico de entregas por webhook.
- Validações de URL `https` e limite de 64 KB por evento.

Fora de escopo
- **Aviso por e-mail ao cliente quando o webhook falha:** adiado para uma próxima fase, depois de medir o impacto ([09:37] Larissa).
- **Dashboard visual para o cliente:** descartado nesta entrega; é um projeto separado do time de frontend ([09:40] Larissa).
- **Rate limiting de envio por cliente:** adiado; a equipe vai observar o comportamento e decidir depois ([09:39] Larissa).
- **Múltiplos workers e ordenação global de eventos:** adiado; nesta versão há um único worker e a ordem só é garantida por pedido ([09:13] Larissa).
- **Arquivamento de eventos entregues (cerca de 30 dias):** fora do escopo desta feature ([09:08] Diego).
- **Webhooks de entrada (o cliente enviar para a plataforma):** descartado; a feature é só de saída ([09:02] Marcos).
- **Endurecer as permissões do cadastro de webhooks:** adiado; por enquanto qualquer usuário autenticado pode configurar ([09:37] Sofia).

---

### Requisitos funcionais

#### FR-001 Cadastrar webhook
O sistema permite que um usuário autenticado cadastre uma URL de webhook para um cliente, escolhendo os status de pedido que quer receber.

**Fluxo principal**
- O usuário informa o cliente, a URL e a lista de status de interesse.
- O sistema valida os dados e gera uma secret única para o webhook.
- O sistema salva o webhook como ativo e devolve os dados, incluindo a secret, uma única vez ([09:31] Marcos).

**Fluxos alternativos e exceções**
- O mesmo cliente pode ter vários webhooks, cada um com sua secret e seus status ([09:44] Sofia).

**Erros previstos**
- URL que não usa `https` é recusada ([09:23] Sofia).
- Lista de status vazia ou com status inexistente é recusada.
- Cliente inexistente é recusado.

**Prioridade:** alta

---

#### FR-002 Listar webhooks de um cliente
O sistema lista os webhooks cadastrados para um cliente.

**Fluxo principal**
- O usuário pede a lista informando o cliente.
- O sistema devolve os webhooks com URL, status assinados e situação (ativo ou inativo), sem a secret.

**Fluxos alternativos e exceções**
- Cliente sem webhooks recebe lista vazia.

**Erros previstos**
- Requisição sem autenticação é recusada.

**Prioridade:** média

---

#### FR-003 Editar webhook
O sistema permite alterar a URL, os status assinados e a situação ativa de um webhook ([09:33] Bruno).

**Fluxo principal**
- O usuário envia as alterações desejadas.
- O sistema valida e salva; as novas regras valem para as próximas mudanças de status.

**Fluxos alternativos e exceções**
- Desativar o webhook interrompe novos envios sem apagar o histórico.

**Erros previstos**
- Webhook inexistente.
- URL `http` ou lista de status inválida.

**Prioridade:** média

---

#### FR-004 Remover webhook
O sistema permite remover um webhook ([09:33] Bruno).

**Fluxo principal**
- O usuário pede a remoção.
- O sistema remove o webhook e deixa de gerar eventos para ele.

**Fluxos alternativos e exceções**
- Eventos pendentes desse webhook deixam de ser enviados **(hipótese)**.

**Erros previstos**
- Webhook inexistente.

**Prioridade:** média

---

#### FR-005 Registrar evento a cada mudança de status
Toda mudança de status de pedido gera um evento de notificação para os webhooks do cliente que assinam aquele status, registrado junto com a própria mudança.

**Fluxo principal**
- Um usuário muda o status de um pedido.
- Na mesma operação que atualiza o pedido, o histórico e o estoque, o sistema registra um evento para cada webhook ativo do cliente que assina o novo status ([09:06] Diego, [09:40] Bruno).
- O evento guarda uma cópia dos dados do pedido naquele momento ([09:52] Larissa).

**Fluxos alternativos e exceções**
- Se nenhum webhook do cliente assina o status, nenhum evento é criado ([09:34] Bruno).
- Se a mudança de status for desfeita, o evento também some.

**Erros previstos**
- Se o registro do evento falhar, a mudança de status inteira é desfeita; não pode haver status alterado sem evento ([09:40] Bruno).
- Evento maior que 64 KB não é enviado e fica registrado como falha ([09:24] Larissa).

**Prioridade:** alta

---

#### FR-006 Enviar notificação assinada ao cliente
O sistema envia cada evento para a URL do webhook, por HTTPS, com assinatura e identificador único.

**Fluxo principal**
- Um processo separado da API verifica eventos pendentes a cada 2 segundos ([09:09] Diego).
- Para cada evento, monta a notificação com os dados do pedido (número, status anterior, status novo, cliente, valor total), sem os itens ([09:43] Diego).
- Assina o conteúdo com HMAC-SHA256 usando a secret do webhook e envia os cabeçalhos `X-Event-Id`, `X-Signature`, `X-Timestamp` e `X-Webhook-Id` ([09:44] Diego, [09:44] Sofia).
- Considera entregue quando o cliente responde com sucesso em até 10 segundos ([09:42] Diego).

**Fluxos alternativos e exceções**
- Eventos de um mesmo pedido são enviados na ordem em que aconteceram, enquanto houver um único processo de envio ([09:12] Diego).
- O cliente pode receber o mesmo evento mais de uma vez e deve descartar repetições pelo `X-Event-Id` ([09:24] Diego).

**Erros previstos**
- Cliente não responde em 10 segundos: tratado como falha.
- Cliente responde com erro: tratado como falha.

**Prioridade:** alta

---

#### FR-007 Retentar envios com falha
O sistema tenta de novo os envios que falharam, com intervalos crescentes.

**Fluxo principal**
- Após uma falha, o sistema agenda nova tentativa em 1 min, depois 5 min, 30 min, 2 h e 12 h ([09:17] Larissa).
- Se alguma tentativa tiver sucesso, o evento é marcado como entregue.

**Fluxos alternativos e exceções**
- A janela total entre a primeira falha e a última tentativa é de quase 15 horas ([09:17] Diego).

**Erros previstos**
- Esgotadas as tentativas, o evento segue para a DLQ (FR-008).

**Prioridade:** alta

---

#### FR-008 Enviar para a DLQ e reprocessar manualmente
Eventos que esgotaram as tentativas vão para uma área separada, de onde um administrador pode reenviá-los.

**Fluxo principal**
- O sistema guarda o evento, o motivo da falha e o horário numa tabela separada ([09:18] Diego).
- Um usuário ADMIN pede o reenvio de um item da DLQ ([09:18] Diego).
- O sistema recoloca o evento na fila como pendente, com o mesmo identificador, e registra quem fez o reenvio ([09:36] Sofia).

**Fluxos alternativos e exceções**
- O reenvio passa de novo pelo ciclo de tentativas.

**Erros previstos**
- Usuário sem papel ADMIN é recusado ([09:36] Sofia).
- Item da DLQ inexistente.

**Prioridade:** alta

---

#### FR-009 Rotacionar a secret do webhook
O cliente pode pedir uma nova secret; a antiga continua valendo por 24 horas para dar tempo de migrar ([09:21] Sofia).

**Fluxo principal**
- O usuário pede a rotação.
- O sistema gera e devolve a nova secret.
- Durante 24 h as duas secrets são aceitas; depois disso só a nova.

**Fluxos alternativos e exceções**
- Nova rotação durante o período de transição é recusada **(hipótese)**.

**Erros previstos**
- Webhook inexistente.

**Prioridade:** média

---

#### FR-010 Consultar histórico de entregas
O cliente vê as últimas entregas de um webhook, com sucesso ou falha, conteúdo enviado, resposta recebida e tempo de resposta ([09:34] Marcos).

**Fluxo principal**
- O usuário pede o histórico de um webhook.
- O sistema devolve as últimas 100 entregas, da mais recente para a mais antiga.

**Fluxos alternativos e exceções**
- Webhook sem envios recebe lista vazia.

**Erros previstos**
- Webhook inexistente.

**Prioridade:** média

---

### Requisitos não funcionais

Performance
- Latência p95 entre a mudança de status e a primeira tentativa de envio menor que 10 s; esperado cerca de 2 s pelo intervalo de verificação ([09:10] Larissa).
- Timeout de 10 s por envio ao cliente ([09:42] Diego).
- A mudança de status de pedido não pode esperar pela resposta do cliente ([09:04] Bruno).

Disponibilidade
- 99.9% de disponibilidade mensal da API de configuração de webhooks **(hipótese: default para sistemas voltados ao cliente externo)**.
- Se o processo de envio parar, nenhum evento se perde; os pendentes são enviados quando ele voltar.

Segurança e autorização
- Toda notificação assinada com HMAC-SHA256 e secret única por webhook ([09:22] Sofia).
- Somente URLs `https` ([09:23] Sofia).
- Endpoints de configuração exigem usuário autenticado; reprocessamento da DLQ exige papel ADMIN ([09:36] Sofia).
- A secret é mostrada apenas na criação e na rotação e nunca aparece em logs.
- Revisão de segurança do código de assinatura e geração de secret antes do deploy ([09:46] Sofia).

Observabilidade
- Logs estruturados com o logger já usado no projeto, com identificador do evento em cada tentativa ([09:29] Bruno).
- Métricas de eventos pendentes, idade do evento mais antigo, taxa de sucesso, latência e entradas na DLQ.
- Tracing da mudança de status até o envio **(hipótese: o projeto ainda não tem ferramenta de tracing)**.

Confiabilidade e integridade de dados
- O registro do evento é atômico com a mudança de status ([09:41] Diego).
- Entrega pelo menos uma vez (at-least-once), com identificador estável para deduplicação ([09:26] Larissa).
- O evento reflete o estado do pedido no momento da mudança ([09:52] Diego).

Compatibilidade e portabilidade
- Endpoints sob `/api/v1`, no padrão REST JSON já usado pelo sistema.
- Nenhuma mudança no contrato atual de mudança de status de pedido.
- Notificações em JSON, até 64 KB ([09:24] Diego).

Compliance
- Todo reprocessamento da DLQ registra quem o executou, para auditoria ([09:36] Sofia).
- O histórico de entregas fica disponível para o cliente conferir o que foi enviado.

Acessibilidade no frontend consumidor
- Não se aplica nesta entrega: a feature expõe apenas API e não tem interface visual ([09:40] Larissa).

---

### Arquitetura e abordagem

Abordagem
- Novo módulo dentro do monólito existente, seguindo o mesmo padrão dos demais, com os eventos registrados numa tabela do próprio MySQL (padrão outbox) e enviados por um processo worker separado ([ADR-001](./adrs/ADR-001-outbox-no-mysql.md), [ADR-002](./adrs/ADR-002-worker-separado-em-polling.md), [ADR-006](./adrs/ADR-006-reuso-dos-padroes-existentes.md)).

Componentes
- API existente (Express), com o novo módulo de configuração de webhooks.
- Serviço de pedidos, que passa a registrar o evento ao mudar o status.
- Banco MySQL 8, com tabelas de webhooks, eventos pendentes, histórico de entregas e DLQ.
- Processo worker, que verifica eventos a cada 2 s, assina e envia.

Integrações
- Sistemas dos clientes B2B, que recebem `POST` HTTPS assinados (comunicação assíncrona do ponto de vista do pedido).
- Portal do desenvolvedor, onde a equipe de produto documenta assinatura e deduplicação para os clientes ([09:26] Marcos).

### Decisões e trade-offs principais

#### Decisão: registrar eventos numa tabela do MySQL (outbox) em vez de chamar o cliente na hora ou usar Redis
- **Justificativa:** garante que evento e mudança de status aconteçam juntos e não exige nova infraestrutura para um time pequeno ([09:06] Diego, [09:07] Diego). Ver [ADR-001](./adrs/ADR-001-outbox-no-mysql.md).
- **Trade-off:** o banco principal passa a funcionar também como fila, com mais carga e crescimento da tabela.

#### Decisão: processo worker separado verificando a cada 2 segundos
- **Justificativa:** reinícios da API não interrompem os envios e 2 s atende com folga a meta de 10 s ([09:09] Diego, [09:11] Diego). Ver [ADR-002](./adrs/ADR-002-worker-separado-em-polling.md).
- **Trade-off:** mais um processo para operar, latência mínima de até 2 s e um único worker como ponto de falha.

#### Decisão: 5 retentativas com backoff e DLQ com reenvio manual
- **Justificativa:** cobre indisponibilidades de algumas horas sem deixar eventos pendentes para sempre ([09:15] Diego, [09:16] Diego). Ver [ADR-003](./adrs/ADR-003-retry-com-backoff-e-dlq.md).
- **Trade-off:** eventos podem chegar com até cerca de 15 h de atraso, e a DLQ depende de acompanhamento manual.

#### Decisão: assinatura HMAC-SHA256 com secret por webhook
- **Justificativa:** padrão de mercado e o vazamento de uma secret afeta só um webhook ([09:20] Sofia, [09:21] Sofia). Ver [ADR-004](./adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md).
- **Trade-off:** a secret precisa ser guardada de forma recuperável e o cliente precisa implementar a verificação.

#### Decisão: entrega at-least-once com `X-Event-Id`
- **Justificativa:** evita perder eventos sem a complexidade de exactly-once; é o modelo usado por Stripe e GitHub ([09:25] Diego). Ver [ADR-005](./adrs/ADR-005-entrega-at-least-once-com-x-event-id.md).
- **Trade-off:** o cliente pode receber duplicatas e precisa deduplicar.

---

### Dependências

#### Organizacional: revisão de segurança
A engenheira de segurança (Sofia) precisa revisar o código de assinatura e de geração de secret, com pelo menos dois dias úteis reservados antes do deploy ([09:46] Sofia).

#### Organizacional: documentação para os clientes
A equipe de produto (Marcos) precisa publicar no portal do desenvolvedor como validar a assinatura e deduplicar eventos pelo `X-Event-Id` ([09:26] Marcos).

#### Externa: adaptação dos sistemas dos clientes
Atlas Comercial, MaxDistribuição e Nova Cargo precisam expor uma URL `https`, validar a assinatura e tratar eventos repetidos para aproveitar a feature.

#### Técnica: execução do processo worker
O ambiente de produção precisa executar e manter no ar um segundo processo (`npm run worker`) com acesso ao mesmo banco ([09:11] Larissa) **(hipótese: forma de implantação a definir com Plataforma)**.

---

### Riscos e mitigação

#### Perder a Atlas Comercial por atraso na entrega
- **Probabilidade:** media
- **Impacto:** perda de um cliente B2B para o concorrente ([09:00] Marcos).
- **Mitigação:**
  - Entregar por fatias, começando pelo registro de eventos e pelo envio ([09:46] Larissa).
  - Confirmar o prazo combinado com o cliente ([09:47] Marcos).
- **Plano de contingência:** liberar primeiro o envio com retentativas para a Atlas e completar rotação de secret e reprocessamento logo depois.

#### Processo de envio parado sem ninguém perceber
- **Probabilidade:** media
- **Impacto:** todas as notificações param, embora sem perda de eventos.
- **Mitigação:**
  - Alerta quando o evento pendente mais antigo passar de 60 s **(hipótese)**.
  - Reinício automático do processo.
- **Plano de contingência:** reiniciar o worker manualmente; os eventos acumulados são enviados em ordem.

#### Cliente processar o mesmo evento duas vezes
- **Probabilidade:** media
- **Impacto:** ações duplicadas no sistema do cliente.
- **Mitigação:**
  - `X-Event-Id` igual em todas as tentativas e no reenvio.
  - Documentação destacada no portal ([09:26] Marcos).
- **Plano de contingência:** orientar o cliente com base no histórico de entregas.

#### Vazamento de uma secret
- **Probabilidade:** baixa
- **Impacto:** terceiros poderiam forjar notificações para um cliente; já houve cliente que vazou secret em log ([09:22] Diego).
- **Mitigação:**
  - Secret única por webhook.
  - Rotação com período de transição de 24 h.
  - Revisão de segurança antes do deploy.
- **Plano de contingência:** rotacionar imediatamente a secret afetada e avisar o cliente.

#### Crescimento da tabela de eventos sobrecarregar o banco
- **Probabilidade:** media
- **Impacto:** lentidão nas operações de pedidos.
- **Mitigação:**
  - Filtrar eventos na origem, só para status assinados ([09:34] Bruno).
  - Índices por situação e data ([09:08] Diego).
  - Definir a política de arquivamento numa próxima fase.
- **Plano de contingência:** limpeza manual de eventos já entregues.

---

### Critérios de aceitação
Checklist objetivo que define se a feature está pronta.

- Toda mudança de status para um status assinado gera exatamente um evento por webhook interessado, e nenhuma mudança desfeita gera evento.
- Se o registro do evento falhar, o status do pedido não muda.
- Mudança para status não assinado não gera evento.
- Com o cliente disponível, a primeira tentativa de envio acontece em menos de 10 s (p95).
- Toda notificação enviada tem `X-Event-Id`, `X-Signature`, `X-Timestamp` e `X-Webhook-Id`, e a assinatura é validável com a secret do webhook.
- Cliente que não responde em 10 s recebe nova tentativa nos intervalos 1 min, 5 min, 30 min, 2 h e 12 h.
- Depois da última falha, o evento aparece na DLQ com motivo e horário.
- Reenvio da DLQ por ADMIN usa o mesmo `X-Event-Id` e registra quem o fez; usuário OPERATOR recebe acesso negado.
- Cadastro com URL `http` é recusado.
- A secret só aparece na resposta de criação e de rotação; nunca em listagens nem em logs.
- Após rotação, as duas secrets validam por 24 h e só a nova depois disso.
- O histórico mostra as últimas 100 entregas com resultado, resposta e tempo.
- Os testes existentes de pedidos continuam passando.

---

### Estratégia de testes e validação

Tipos de teste obrigatórios
- Testes de integração contra MySQL real, no padrão já usado pelo projeto, cobrindo registro do evento com sucesso e com rollback.
- Testes unitários para assinatura HMAC, cálculo de backoff e filtro de status.
- Testes ponta a ponta com um servidor HTTP falso simulando cliente disponível, lento (mais de 10 s) e fora do ar.
- Teste de autorização: reprocessamento da DLQ só para ADMIN.
- Revisão de segurança manual do código de assinatura e geração de secret ([09:46] Sofia).

Estratégia de validação
- Revisão do design com Bruno e Diego antes de iniciar o código ([09:50] Larissa).
- Validação em homologação com um dos clientes (por exemplo a Atlas), conferindo assinatura, deduplicação e retentativas **(hipótese)**.
- Acompanhamento das métricas de latência e DLQ nas primeiras semanas em produção.
