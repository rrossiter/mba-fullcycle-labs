# ADR-004: Autenticação HMAC-SHA256 com secret por endpoint

**Data:** Desconhecida (reunião técnica de webhooks, quinta-feira, 09:00)
**Related to:**
- [ADR-005: Garantia de entrega at-least-once com X-Event-Id](./ADR-005-entrega-at-least-once-com-x-event-id.md)

## Status

Aceito

## Contexto

Os webhooks enviam dados de pedidos para endpoints fora da nossa infraestrutura. O cliente precisa conseguir verificar duas coisas: que a requisição veio de nós (autenticidade) e que o corpo não foi alterado no caminho (integridade).

Já houve um cliente que vazou uma secret no log da própria aplicação. Por isso, o vazamento de uma secret precisa ter impacto limitado, e a troca de secret precisa ser possível sem interromper a integração.

## Direcionadores da Decisão

- Permitir ao cliente validar origem e integridade de cada requisição.
- Usar um padrão de mercado com biblioteca disponível em qualquer linguagem.
- Limitar o impacto do vazamento de uma secret.
- Permitir rotacionar a secret sem tirar a integração do ar.
- Garantir transporte criptografado.

## Alternativas Consideradas

1. HMAC-SHA256 sobre o corpo, com secret por endpoint e rotação com prazo de 24 horas (opção escolhida)
2. HMAC com uma secret global única da plataforma
3. Assinatura assimétrica (par de chaves, por exemplo Ed25519 ou RSA)
4. Apenas TLS, sem assinatura

## Decisão

Opção escolhida: "HMAC-SHA256 sobre o corpo, com secret por endpoint e rotação com prazo de 24 horas", porque é o padrão de mercado, simples de validar pelos clientes, e restringe o impacto de um vazamento a um único endpoint.

Detalhes da decisão:

- A assinatura é calculada sobre o corpo da requisição e enviada no header `X-Signature`.
- Cada endpoint de webhook tem uma secret única, gerada pela plataforma e devolvida ao cliente na criação.
- A tabela de configuração armazena url, secret, customer_id e estado ativo.
- A secret pode ser rotacionada pela API. Depois da rotação, a secret antiga continua válida por 24 horas em paralelo com a nova e então é descartada.
- A URL de destino precisa ser HTTPS. Uma URL `http` é recusada na validação do schema Zod.
- O código de assinatura e de geração de secret passa por revisão de segurança antes do deploy, com dois dias úteis reservados para isso.

## Prós e Contras das Opções

### HMAC-SHA256 com secret por endpoint

- Bom, porque é o padrão de mercado e qualquer cliente tem biblioteca para validar.
- Bom, porque um vazamento compromete só um endpoint.
- Bom, porque a rotação com prazo de 24 horas permite trocar a secret sem interrupção.
- Ruim, porque a secret precisa ser guardada de forma recuperável, para assinar, e não como hash.

### Secret global única

- Bom, porque é mais simples de gerenciar.
- Ruim, porque um vazamento comprometeria todos os clientes de uma vez.

### Assinatura assimétrica

- Bom, porque dispensa compartilhar segredo e oferece não repúdio.
- Ruim, porque é menos comum em webhooks e mais difícil de implementar para os clientes.

### Apenas TLS

- Bom, porque não exige nada do cliente além de HTTPS.
- Ruim, porque protege o transporte, mas não prova ao cliente que foi a plataforma quem chamou.

## Consequências

O cliente passa a validar origem e integridade com uma biblioteca padrão. Junto com o header `X-Timestamp` (ADR-005), ele também consegue detectar ataques de replay, se quiser.

Em contrapartida, as secrets ficam armazenadas de forma recuperável e passam a ser dados sensíveis no banco. Durante a rotação há duas secrets válidas ao mesmo tempo, e é preciso definir com qual o worker assina nesse período. A segurança depende de o cliente validar corretamente, com comparação em tempo constante e sobre o corpo bruto da requisição. Há também mais endpoints e regras para manter.

O trade-off é optar por segredo compartilhado simétrico, mais simples e universal, em vez da não repudiação da criptografia assimétrica. O risco do segredo compartilhado é mitigado por uma secret por endpoint e pela rotação com prazo de transição.

## Referências

- TRANSCRICAO.md (trechos 09:19 a 09:23 e 09:44 a 09:46)
- src/middlewares/validate.middleware.ts
