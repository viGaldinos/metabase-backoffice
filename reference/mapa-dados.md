# Mapa de dados — Metabase GCB

Levantado em 16/09/2026 por inspeção direta do Metabase. Os ids são estáveis; a
classificação de "fonte oficial" precisa ser confirmada pelo time e está marcada com
`[A CONFIRMAR]` onde ainda não foi.

## Índice
- Regra de ouro
- Schemas: usar e ignorar
- Bancos conectados
- Collections do backoffice
- Filtros obrigatórios em `tb_extract`
- Armadilhas conhecidas

---

## Regra de ouro

Se o domínio que você precisa não estiver marcado como confirmado abaixo,
**pergunte antes de escolher o banco.** Nomes parecidos escondem conteúdos
diferentes, e há uma migração em andamento.

---

## Schemas: usar e ignorar

Levantado no banco `PeerBR RedShift` (id 42), por contagem de tabelas:

### Usar

| Schema | Tabelas | Observação |
|---|---|---|
| `dw_mart` | 40 | Camada final modelada. **Primeira opção sempre.** |
| `dw_staging` | 23 | Staging tratado. Use só se `dw_mart` não cobrir. |
| `gcb_finance_public` | 70 | Domínio financeiro. `[A CONFIRMAR]` se é a fonte oficial |
| `fmi_public` | 174 | Domínio FMI/securitizadora. `[A CONFIRMAR]` |
| `public` | 194 | Misto, sem curadoria. Use por último e sempre confira a origem |

> **Tensão aberta `[A CONFIRMAR]`.** A regra acima manda preferir `dw_mart`, mas a
> investigação de novação/migração do time de dados foi feita inteiramente em `public`,
> sobre tabelas transacionais (`tb_underwritings`, `tb_extract`, `tb_novations`), e é de
> lá que vêm as definições em `metricas.md`. Não está decidido se o backoffice deve ler
> `public` nesses domínios ou se existe equivalente modelado em `dw_mart`.
> **Enquanto não estiver resolvido, pergunte.**

### Ignorar sempre

| Padrão | Tabelas | Por quê |
|---|---|---|
| `dw_dbt_test__audit` | 908 | Resultado de teste do dbt, não é dado de negócio |
| `dev_dbt_test__audit` | 903 | idem, em desenvolvimento |
| `dev_pr435_dbt_test__audit` | 819 | idem, de um Pull Request específico |
| `dev_*` (qualquer) | — | Ambiente de desenvolvimento |
| `dev_mart`, `dev_staging`, `dev_pr435_mart` | 48 / — / 28 | idem |
| `dbt_sl_dbt_test__audit` | 36 | idem |
| `__segment_reverse_etl` | 112 | Infraestrutura de tracking |
| `peerbr_mobile`, `peerbr_portal` | 249 / 200 | Eventos de produto (cliques, telas). Não são operações financeiras — use só para análise de comportamento no app |

**Mais de 2.600 das tabelas do ambiente são teste do dbt.** Se uma busca retornar
nomes começando com `not_null_` ou `unique_`, você está no lugar errado.

---

## Bancos conectados

São 40 no total. Os relevantes identificados:

| id | Nome | Engine | Uso |
|---|---|---|---|
| 42 | PeerBR RedShift | redshift | DW principal histórico |
| 60 | PeerBR & Finance RedShift | redshift | **Criado em 11/09/2026.** Consolidação de PeerBR + Finance. `[A CONFIRMAR]` se já é a fonte oficial ou ainda está em migração |
| 30 | Adiante RedShift | redshift | DW da Adiante Recebíveis |
| 54 | GCB RedShift | redshift | `[A CONFIRMAR]` |
| 53 | FMI RedShift | redshift | `[A CONFIRMAR]` |
| 17 | FMI PostgreSQL | postgres | Transacional FMI. Muito usado por perguntas antigas do backoffice |
| 16 | GCB Finance | postgres | `[A CONFIRMAR]` |
| 40 | Finance Summary | redshift | `[A CONFIRMAR]` |
| 43 | GCB BaaS | postgres | Onboarding / BaaS |
| 23 | GCB Pagamento | mysql | Pagamentos |
| 2 / 46 / 14 | Adiante Notas / Operações / Monitoramento | mysql | Transacionais Adiante |
| 47 | `[A IDENTIFICAR]` | — | Usado por perguntas de Captação e Ativações do backoffice |
| 13 | `[A IDENTIFICAR]` | — | Usado por perguntas antigas de Taxa Especial |

> Para listar todos: `read_resource` em `metabase://databases` e `metabase://databases?page=2`.

### Decisão pendente que bloqueia tudo

**Qual é a fonte oficial hoje: banco 42 ou banco 60?**
Enquanto isso não estiver escrito aqui, sempre pergunte.

---

## Collections do backoffice

Existem **duas** collections chamadas "Backoffice", em árvores diferentes. Não
confundir.

### Árvore GCB / PeerBR — collection 435 (a principal)

| id | Nome |
|---|---|
| 435 | **Backoffice** (raiz, 64 itens) |
| 574 | 0. Recursos e Consultas Básicas |
| 569 | Rotinas Diárias |
| 576 | Contábil |
| 639 | Financeiro |
| 580 | Juridico |
| 659 | Comissão |
| 842 | DCM |
| 859 | FP&A |
| 632 | Patrimônio Separado |
| 773 | WM |
| 986 | Comercial |
| 593 | PeerBR |
| 623 | Canal único |
| 542 | Análise de Migração |
| 693 | Outros |
| 2300 | 🚨Alertas — *"Alertas de regras de negócio do time de backoffice"* |

> **A collection 2300 é a fonte mais rica de regra de negócio já escrita do time.**
> Ao preencher `metricas.md`, comece por ela.

### Árvore Adiante — collection 714

| id | Nome |
|---|---|
| 714 | **Backoffice** (raiz) |
| 716 | Backoffice Comercial |
| 715 | Contábil |
| 349 | Financeiro |
| 350 | Jurídico |

### Rascunho

`[A DEFINIR]` — criar uma collection de rascunho do backoffice e registrar o id aqui.
Até lá, salve na collection pessoal de quem está pedindo.

---

## Filtros obrigatórios em `tb_extract`

Vale para **toda** agregação de valor financeiro sobre `tb_extract` — captação, resgate,
saldo, valor investido, novação, migração. Sem estes dois filtros a conta soma pendências
e transações que o banco não efetivou.

```sql
AND e.description NOT ILIKE '%processando%'
AND (e.baas_transaction_status IS NULL OR e.baas_transaction_status <> 'ERROR')
```

**Filtro A — `NOT ILIKE '%processando%'`.** Remove ordens de investimento ainda em voo
(~13.992 registros): 100% `extract_type_id = 6`, 100% com `underwritings_id` NULL — a
posição ainda não existe e pode não se concretizar. Quando o investimento confirma, é o
lançamento definitivo "Investimento em …" que conta.

**Filtro B — `baas_transaction_status <> 'ERROR'`, mantendo `NULL`.** Remove movimentações
cuja transação bancária falhou (~4.478, 0,17%), sobretudo resgates (tipo 2) e aportes
(tipo 6). Aportes com `ERROR` não têm versão "boa" — é dinheiro que não se moveu.

> ⚠️ **Nunca troque por `= 'CONFIRMED'`.** 73% dos lançamentos têm status `NULL` por não
> passarem pela trilha bancária — são movimentos internos de razão (migração, novação,
> cupom, rendimento, reinvestimento, cessão) e são legítimos. Descartar `NULL` jogaria
> fora a maioria da base. Filtre **apenas** o `ERROR` explícito.

Fonte: `data-team-llm-wiki/wiki/peerbr-novacoes-migracoes.md`, seção 13.

---

## Armadilhas conhecidas

**Versões divergentes da mesma pergunta.** Na collection 435 existem, sobre o mesmo
assunto: `Auxiliar Renato M. - Taxa Especial no ato Peer`, `... Peer V2`,
`... Peer V2 - v2`, `... Peer V4` e `... no ato v2` — em três bancos diferentes
(13, 17, 42). Ao reaproveitar uma consulta existente, **confirme qual versão é a
vigente** em vez de pegar a primeira que aparecer.

**Divergência documentada e não resolvida.** A view `vw_customer_investment` traz na
própria descrição uma dúvida aberta sobre por que o valor comprado e o valor em
carteira de operações estruturadas divergem, com uma lista de operações a excluir
(OE007 a OE010 e OE019). Tratar como regra não fechada — não usar sem confirmar.

**Nomes iguais em bancos diferentes.** `tb_notas_deletadas` e `tb_codigos_retorno_banco`
existem em mais de um banco com conteúdos distintos.

**`deleted_at IS NULL` derruba histórico.** Em `tb_underwritings`, ~60% dos papéis ficam
soft-deletados depois de uma novação ou migração. Um `JOIN … WHERE deleted_at IS NULL`
sobre underwriting apaga a maior parte do histórico sem avisar. O registro durável do
valor é `tb_extract`, não o underwriting.
