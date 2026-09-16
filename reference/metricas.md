# Métricas canônicas — Backoffice GCB

Este arquivo é a **fonte única de verdade** das definições. Se um indicador não estiver
aqui, ele não tem definição oficial — nesse caso, pergunte à pessoa; não deduza.

> **Estado atual: parcialmente preenchido.** Duas definições (Novação e Migração) foram
> redigidas a partir de investigação documentada do time de dados, mas **nenhuma foi
> validada pelo backoffice ainda**. Todo campo não confirmado está marcado
> `[A CONFIRMAR]`. Para tudo que não está aqui, a skill opera em modo "sempre perguntar".

## Como preencher

Uma seção por métrica, sempre com todos os campos. Campo que você não sabe preencher
fica marcado `[A CONFIRMAR]` — nunca preenchido no chute.

---

## MODELO (copie este bloco)

### Nome da métrica

**Definição de negócio:** uma frase, na linguagem do backoffice, sem SQL.

**Fonte:** banco (id e nome) + schema + tabela.

**Janela temporal:** qual data é usada como referência e a partir de quando conta.

**Inclui:** o que entra na conta.

**Exclui:** o que fica de fora — cancelados, renegociados, testes, operações
específicas. Este campo é o que mais causa divergência; seja exaustivo.

**SQL de referência:**
```sql
-- consulta validada
```

**Valor de aferição:** um resultado conhecido numa data conhecida, para conferir se a
definição continua valendo. Ex.: "Em 31/08/2026 o valor era R$ X".

**Dono da definição:** quem no backoffice decide se esta regra muda.

**Revisado em:** data.

**Observações:** limitações, dados assumidos, o que não dá para afirmar com esta fonte.

---

## Filtro de higiene obrigatório

Vale para **toda** agregação de valor financeiro sobre `tb_extract` — captação, resgate,
saldo, valor investido, novação, migração. Sem ele a conta soma pendências e transações
que o banco não efetivou.

```sql
AND e.description NOT ILIKE '%processando%'
AND (e.baas_transaction_status IS NULL OR e.baas_transaction_status <> 'ERROR')
```

Detalhamento e números em `mapa-dados.md`, seção "Filtros obrigatórios em `tb_extract`".
**Não troque a segunda condição por `= 'CONFIRMED'`** — 73% dos lançamentos têm status
`NULL` por serem movimentos internos de razão, e são legítimos.

---

# Definições

## Novação

**Definição de negócio:** reperfilamento da posição de um investidor de uma debênture
para outra **sem liquidar** o papel de origem. O papel antigo é encerrado por mudança de
status; o papel novo recebe o crédito correspondente.

**Fonte:** banco PeerBR, schema `public` — `tb_novations`, `tb_extract`
(`extract_type_id = 31`), `tb_underwriting_migrations` como ponte.
`[A CONFIRMAR]` o id do banco no Metabase (42 × 60) e se o backoffice deve usar `public`
ou uma tabela equivalente em `dw_mart` — ver a tensão registrada em `mapa-dados.md`.

**Janela temporal:** `[A CONFIRMAR]` qual data é a oficial — `tb_novations.execution_date`
ou `tb_extract.executed_at`. O código de extract 31 só existe desde **22/12/2025**;
`[A CONFIRMAR]` se existem novações anteriores a essa data e como foram registradas.

**Inclui:**
- `tb_novations.status = 'PROCESSED'`
- **os dois** valores de `operation_type`: `'NOVATION'` e `'MIGRATION'` — ambos são
  família novação
- 1 crédito de `extract_type_id = 31` no underwriting de **destino**
  (`underwritings_id = result_underwriting_id`), cobertura 1:1 com as novações PROCESSED

**Exclui:**
- `status` `CANCELED` e pendentes
- migração propriamente dita: `tb_underwriting_migrations` com
  `underwriting_settlement_id` preenchido, e extracts 27/28/29/30 ou o par legado 5→6
- `tb_extract.deleted_at IS NOT NULL` (numa novação cancelada, destino e extract 31 são
  soft-deletados juntos)
- o filtro de higiene acima

**SQL de referência:** `[NÃO EXECUTADO]` — redigido a partir da investigação, ainda não
rodado contra a base.
```sql
SELECT date_trunc('month', e.executed_at) AS mes,
       count(*)                           AS qtd_novacoes,
       sum(e.value)                       AS valor
FROM public.tb_extract e
WHERE e.extract_type_id = 31          -- novation
  AND e.deleted_at IS NULL
  AND e.description NOT ILIKE '%processando%'
  AND (e.baas_transaction_status IS NULL OR e.baas_transaction_status <> 'ERROR')
GROUP BY 1
ORDER BY 1;
```

**Valor de aferição:** `[A CONFIRMAR]`. Ordem de grandeza conhecida (jul/2026, **não é
aferição validada**): 4.777 novações `PROCESSED` — 3.318 com `operation_type='MIGRATION'`
+ 1.459 `'NOVATION'`; 2.694 `CANCELED`; 725 pendentes.

**Dono da definição:** `[A CONFIRMAR]`

**Revisado em:** 2026-09-16 — redigido, **não validado pelo backoffice**.

**Observações:**
- `tokens_quantity` é **quantidade de tokens**, não reais. Nunca reconciliar contra `value`.
- `extract31.value` = `original_value` do destino em 99,96% dos casos.
- Novação **parcial** existe: o sinal correto é `tb_novations.percentage < 1` (30 casos
  em jul/2026). Não use `token_quantity < purchased_token`, que infla porque
  `purchased_token` pode incluir reinvestimento.
- ~60% dos papéis ficam soft-deletados em `tb_underwritings` após a operação. Um
  `JOIN … WHERE deleted_at IS NULL` sobre underwriting derruba a maior parte do histórico
  — o registro durável do valor é `tb_extract`.
- Exclusivo de **debêntures** (produtos com `icon` prefixo `DEBP`).

**Origem desta definição:** `data-team-llm-wiki/wiki/peerbr-novacoes-migracoes.md`
(atualizado 2026-07-13), seções 1, 3, 5, 10 e 12.

---

## Migração

**Definição de negócio:** movimentação da posição de um investidor de uma debênture para
outra **com liquidação do papel de origem**. Diferente de novação: aqui a origem passa
por settlement.

**Fonte:** banco PeerBR, schema `public` — `tb_underwriting_migrations`,
`tb_underwriting_settlement`, `tb_extract`. Mesmas ressalvas de banco e schema da Novação.

**Janela temporal:** `tb_underwriting_migrations.reference_date`. `[A CONFIRMAR]` se o
fechamento usa essa data ou a do extract — há 8 casos conhecidos de defasagem de 1 dia
entre as duas.

**Inclui:**
- `tb_underwriting_migrations.underwriting_settlement_id` **preenchido** (é isto que
  separa migração de novação, sem exceção conhecida)
- os quatro subtipos: 27 migração · 28 cessão · 29 redução de taxa · 30 troca de opção
- as **migrações legadas** (anteriores a 13/05/2025), lançadas como par de extract
  tipo 5 (saída) → tipo 6 (entrada) — **~61% do total**

**Exclui:**
- novação (`underwriting_settlement_id IS NULL`)
- ao somar valor: a **perna de entrada** (`credit_value < 0`, no destino). Some só a
  perna de saída (`credit_value > 0`), senão a operação é contada duas vezes
- `deleted_at IS NOT NULL`
- o filtro de higiene acima

**SQL de referência:** `[NÃO EXECUTADO]` — redigido a partir da investigação, ainda não
rodado contra a base.
```sql
-- Universo de migrações (conta pela tabela de migração, não pelo extract:
-- as legadas não têm código de extract próprio)
SELECT date_trunc('month', m.reference_date) AS mes,
       count(*)                              AS qtd_migracoes,
       sum(m.value)                          AS valor
FROM public.tb_underwriting_migrations m
WHERE m.underwriting_settlement_id IS NOT NULL   -- migração, não novação
  AND m.deleted_at IS NULL
GROUP BY 1
ORDER BY 1;
```

**Valor de aferição:** `[A CONFIRMAR]`. Ordem de grandeza conhecida (jul/2026, **não é
aferição validada**): 5.768 migrações ativas (`settlement` preenchido), contra 4.777 da
família novação. Volumes por subtipo, população 2025+ classificável: 27 ≈ 1.714 ·
30 ≈ 497 · 28 ≈ 48 · 29 ≈ 13.

**Dono da definição:** `[A CONFIRMAR]`

**Revisado em:** 2026-09-16 — redigido, **não validado pelo backoffice**.

**Observações:**
- **Não dá para contar migração só pelo `tb_extract`.** As legadas (61%) usam tipos 5 e
  6, indistinguíveis de rendimento e de compra. Sempre passe por
  `tb_underwriting_migrations`.
- Extract 27–30 **nem sempre tem settlement** — só a perna de saída, e nem sempre:
  27 ≈ 99,8% · 29 = 100% · 30 ≈ 84% · 28 ≈ 46%. Cessão e troca de opção às vezes são só
  reclassificação, sem resgate de principal.
- **Consolidação N→1:** vários papéis de origem podem convergir para um único destino
  (até 51→1). Logo há mais lançamentos `+` que `-` nos tipos 27 e 30 — isso é esperado,
  não é erro.
- ~152 migrações apontam para settlement de **cupom** (tipo 22, `percentage_settled = 0`),
  não do principal. É a principal fonte de divergência entre `migration.value` e
  `settled_value`.
- Cessão (28) tem 107 lançamentos com `underwritings_id` **nulo** — é a perna de caixa do
  cliente, sem produto associado.
- Conciliação de pares deveria usar janela de **±1 dia**, não data exata: dos 15 pares
  descasados conhecidos, 8 são só defasagem de 1 dia. Nenhum é transação perdida.
- Exclusivo de **debêntures** (100% `DEBP` nos dois lados). Nunca muda
  `products_type_id`, `modality_id` nem `correction_index_id`.

**Origem desta definição:** `data-team-llm-wiki/wiki/peerbr-novacoes-migracoes.md`
(atualizado 2026-07-13), seções 1, 2, 6, 7, 8, 9, 11 e 12.

---

## Métricas a preencher

Lista inicial sugerida, a ser ajustada com o time. Comece pelos relatórios que o
backoffice refaz manualmente com mais frequência.

- [ ] Captação bruta
- [ ] Captação líquida
- [ ] Alocação
- [ ] Ativações
- [ ] Comissão por assessor
- [ ] Liquidação de operação
- [ ] Inadimplência
- [ ] Resgate / portabilidade
- [ ] Posição do cliente
- [ ] Patrimônio separado
- [x] Novação — redigida, **aguarda validação do backoffice**
- [x] Migração — redigida, **aguarda validação do backoffice**
- [ ] Taxa especial

> Fontes para o preenchimento, em ordem de qualidade: (1) a wiki do time de dados
> (`data-team-llm-wiki`), que já passa por revisão em Pull Request; (2) a collection
> 🚨Alertas (id 2300), que documenta regras de negócio do time; (3) o SQL das perguntas
> salvas nas subpastas do backoffice; (4) as descrições de dashboards existentes;
> (5) o projeto dbt (`data-engineering-dbt`).
