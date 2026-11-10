# Da Reunião ao Documento: Design Docs Gerados por IA

Pacote de design docs da feature **Webhooks de Notificação de Pedidos** do `order-management-api`, produzido com IA a partir da transcrição de uma reunião técnica e do código existente.

---

## Sobre o desafio

Uma empresa que opera um OMS (Order Management System / sistema de gestão de pedidos) precisa notificar três clientes B2B sempre que o status de um pedido muda. Hoje eles consultam a API repetidamente. A decisão técnica já tinha sido tomada numa reunião de cerca de 55 minutos entre tech lead, PM, engenheiros e segurança, mas nada foi registrado além da transcrição (`TRANSCRICAO.md`).

A tarefa foi transformar essa conversa, junto com a leitura do código base (Node.js, Express, Prisma, MySQL), num pacote de documentação acionável: PRD, RFC, FDD, ADRs e um tracker que liga cada item à sua origem na reunião ou no código. A IA foi a ferramenta principal de produção. O meu papel foi orientar, validar e corrigir.

A atividade ensina a usar a IA para transformar, passo a passo, a transcrição de uma agenda em um material entregável.   

---

## Ferramentas de IA utilizadas

| Ferramenta | Papel |
|---|---|
| **Claude Code** (CLI, modelo Claude Opus 5.5) | Agente principal: leu o código e a transcrição, escreveu os documentos e rodou as validações automáticas |
| **Plugin `adrs-management`** (marketplace `fullcycle-claude-marketplace`) | Pipeline de ADRs em 4 fases: `/adr-map`, `/adr-identify`, `/adr-generate`, `/adr-link` |
| Subagentes `adr-analyzer`, `adr-generator`, `adr-linker` | Executaram as fases do plugin, até 13 em paralelo |
| **Skill `skill-creator`** | Transformou os prompts do curso para FDD e PRD em skills reutilizáveis |
| **Skills próprias `fdd-generator` e `prd-generator`** | geraram o `docs/FDD.md` e o `docs/PRD.md` |

---

## Workflow adotado

A ordem foi: primeiro entender o código e registrar as decisões fechadas (ADRs), depois a proposta (RFC), a implementação (FDD), o produto (PRD) e, por fim, a rastreabilidade (Tracker).

1. **Mapear o código** com `/adrs-management:adr-map`. A descoberta mais importante foi que a feature de webhooks não existe no código, então as decisões só podiam vir da transcrição. O ponto de integração é `OrderService.changeStatus`.
2. **Identificar decisões** com `/adrs-management:adr-identify` nos 11 módulos, em paralelo. Resultado: 15 potenciais ADRs e achados colaterais de qualidade, como o registro público que permite criar ADMIN.
3. **Gerar e linkar ADRs** com `/adr-generate` (13 ADRs em pt-BR) e `/adr-link` (13 relações bidirecionais).
4. **Escrever os 6 ADRs da entrega** em `docs/adrs/`, a partir da transcrição, no formato do modelo gerado pelo plugin e com as seções exigidas.
5. **RFC** a partir dos ADRs: abordagem, alternativas descartadas e questões em aberto, com siglas expandidas em inglês e pt-BR.
6. **Skill de FDD:** o prompt do curso virou a skill `fdd-generator`. A skill foi validada contra o enunciado e executada com os mínimos explícitos.
7. **Skill de PRD:** o prompt do curso virou a skill `prd-generator`, executada da mesma forma.
8. **Tracker** montado no fim, varrendo os documentos prontos. Cada citação `[hh:mm] Nome` foi conferida por script contra a transcrição.

**Como organizei a interação com a IA**

- Colei os requisitos do enunciado como instrução em cada etapa, para a IA conferir o resultado contra eles.
- Pedi validações sem alteração ("apenas valide e retorne") antes de executar, para enxergar lacunas.
- Usei as skills em "modo fontes": elas leem transcrição, ADRs e código e só perguntam o que falta, em vez de me entrevistar de novo.
- Tudo o que não tem origem na reunião ou no código foi marcado como **(hipótese)** nos documentos e listado à parte no tracker.

---

## Prompts customizados

**1. Gerar os ADRs da entrega a partir do requisito do desafio**

```
Mantenha 6 ADRs em arquivos separados dentro de docs/adrs/, nomeados no formato
ADR-NNN-titulo-em-kebab-case.md (ex: ADR-001-outbox-no-mysql.md).
Garanta que as ADRs sigam o formato MADR (ou variante padrão) com no mínimo as seções:
Status, Contexto, Decisão, Alternativas Consideradas (pelo menos 1 alternativa real
discutida ou plausível), Consequências (positivas e negativas, com trade-off explícito).
```

**2. Executar a skill garantindo os critérios do desafio**

```
/prd-generator execute a skill e garanta que as regras abaixo sejam atendidas:
[seções obrigatórias do PRD]
A seção "Fora de escopo" deve listar explicitamente pelo menos 2 itens descartados
ou adiados durante a reunião.
para gerar o PRD use os documentos do diretorio docs/
```

---

## Iterações e ajustes

| # | O que a IA gerou | Problema | Como corrigi |
|---|---|---|---|
| 1 | ADRs do plugin | Ficavam em subpastas, numerados `ADR-XXXX`; não atendiam o formato da entrega | 6 ADRs reescritos em `docs/adrs/` a partir da transcrição |
| 2 | ADRs no formato do modelo | Títulos ("Opções Consideradas", "Resultado da Decisão") não batiam com o critério de aceite | Seções renomeadas para Status, Contexto, Alternativas Consideradas, Decisão, Consequências |
| 3 | Skill `fdd-generator` | A validação mostrou que não fixava os mínimos do desafio (fluxos, `WEBHOOK_*`, número de endpoints e de caminhos) | Mínimos passados explicitamente na execução; FDD conferido por script |
| 4 | PRD | O esqueleto da skill agrupava "Público-alvo" e "Problema" sob outro título | Títulos ajustados para os nomes exatos exigidos pelo enunciado |

**Iterações principais:** cerca de 6 rodadas sobre os ADRs, 2 sobre o RFC, 1 sobre o FDD, 2 sobre o PRD e 2 sobre o Tracker.

---

## Como navegar a entrega

**Ordem sugerida de leitura**

1. [`TRANSCRICAO.md`](TRANSCRICAO.md): a reunião, fonte das decisões.
2. [`docs/PRD.md`](docs/PRD.md): por que a feature existe, o que precisa fazer e como saber que está pronta.
3. [`docs/RFC.md`](docs/RFC.md): proposta técnica, alternativas descartadas e questões em aberto.
4. [`docs/adrs/`](docs/adrs/README.md): as 6 decisões fechadas.
   - [ADR-001 Outbox no MySQL](docs/adrs/ADR-001-outbox-no-mysql.md)
   - [ADR-002 Worker separado em polling](docs/adrs/ADR-002-worker-separado-em-polling.md)
   - [ADR-003 Retry com backoff e DLQ](docs/adrs/ADR-003-retry-com-backoff-e-dlq.md)
   - [ADR-004 HMAC-SHA256 com secret por endpoint](docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md)
   - [ADR-005 Entrega at-least-once com X-Event-Id](docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md)
   - [ADR-006 Reuso dos padrões existentes](docs/adrs/ADR-006-reuso-dos-padroes-existentes.md)
5. [`docs/FDD.md`](docs/FDD.md): como implementar (fluxos, contratos, erros `WEBHOOK_*`, observabilidade, integração com o código).
6. [`docs/TRACKER.md`](docs/TRACKER.md): de onde veio cada item.

