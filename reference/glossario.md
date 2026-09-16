# Glossário — termo de negócio → onde está no dado

Traduz o vocabulário do backoffice para tabela e coluna reais. Diferente de
`metricas.md`: aqui não há cálculo, só o mapeamento de "onde isso vive".

> **Estado atual: parcialmente preenchido.** Só o domínio de novação/migração foi
> mapeado. Se um termo não estiver aqui, pergunte à pessoa em vez de adivinhar a partir
> do nome da coluna.

## Formato

| Termo | Significa | Banco / schema / tabela | Coluna | Observação |
|---|---|---|---|---|
| exemplo | o que é no negócio | 42 / dw_mart / fct_x | col_y | pegadinha conhecida |

---

## Mapeado — domínio novação / migração (debêntures)

Banco PeerBR, schema `public`. Id do banco no Metabase `[A CONFIRMAR]` (42 × 60).

| Termo | Significa | Tabela | Coluna | Observação |
|---|---|---|---|---|
| Underwriting | a posição do investidor num papel | `tb_underwritings` | `id`, `customer_id`, `products_id`, `status`, `original_value`, `current_token` | ~60% ficam soft-deletados após novação/migração — não filtre por `deleted_at` ao olhar histórico |
| Novação | troca de papel **sem** liquidar a origem | `tb_novations` | `underwriting_id` (origem), `result_underwriting_id` (destino), `status`, `percentage` | ver `metricas.md` |
| Migração | troca de papel **com** liquidação da origem | `tb_underwriting_migrations` | `source_underwriting_id`, `result_underwriting_id`, `underwriting_settlement_id`, `reference_date` | ver `metricas.md` |
| Settlement / liquidação | liquidação de um underwriting | `tb_underwriting_settlement` | `underwriting_id`, `extract_id`, `settled_value`, `percentage_settled` | `percentage_settled = 0` costuma ser liquidação de **cupom**, não de principal |
| Extrato / lançamento | movimentação financeira | `tb_extract` | `underwritings_id`, `extract_type_id`, `value`, `credit_value`, `baas_transaction_status` | fonte durável do valor; sempre aplicar o filtro de higiene |
| Tipo de lançamento | natureza da movimentação | `tb_extract_types` | `id`, `name`, `operation_type` | dicionário abaixo |
| Cessão | transferência da posição para **outro investidor** | — | `extract_type_id = 28` | único subtipo que muda o cliente |
| Troca de opção | muda Reinvestir ↔ Cupom, mesmo papel e prazo | — | `extract_type_id = 30` | |
| Redução de taxa | renegociação que baixa a taxa contratada | — | `extract_type_id = 29` | |
| Rollover | migração para papel tipicamente mais longo | — | `extract_type_id = 27` | o subtipo mais comum |
| Token | fração da posição | `tb_underwritings`, `tb_novations` | `purchased_token`, `current_token`, `tokens_quantity` | **quantidade, não R$** — nunca reconciliar contra `value` |
| BaaS | parceiro bancário que executa o movimento de dinheiro | `tb_extract` | `baas_transaction_status` | `NULL` (73%) = movimento interno de razão, legítimo |
| DEBP | debênture PeerBR | `tb_products` | `icon` (prefixo `DEBP`) | novação e migração são 100% DEBP dos dois lados |

### Dicionário de `extract_type` (`public.tb_extract_types`)

| id | name | é | desde |
|---|---|---|---|
| 2 | débito resgate | saque | histórico |
| 5 | income | rendimento — **e** a perna de saída da migração legada | histórico |
| 6 | debit_purchase | investimento — **e** a perna de entrada da migração legada | histórico |
| 22 | coupon_settlement | liquidação de cupom (RF) | 2023 |
| 27 | migration | migração (rollover) | 2025-05-13 |
| 28 | cession | cessão | 2025-05-13 |
| 29 | tax_decrease | redução de taxa | 2025-05-13 |
| 30 | option_exchange | troca de opção | 2025-05-13 |
| 31 | novation | novação | 2025-12-22 |

---

## Termos com sentido ambíguo

Registre aqui todo termo que significa coisas diferentes em áreas diferentes. Estes
são os que mais geram número errado.

| Termo | Sentido A | Sentido B | Como desambiguar |
|---|---|---|---|
| **Migração** | `tb_novations.operation_type = 'MIGRATION'` — que é **família novação**, extract 31, sem settlement | migração de verdade — extract 27–30 (ou 5→6 legado), sempre com settlement na origem | pelo `underwriting_settlement_id` em `tb_underwriting_migrations`: `NULL` = novação, preenchido = migração. Separação 100% limpa |
| **`value` × `credit_value`** | `value` — magnitude, sempre positiva, idêntica nos dois lados do par | `credit_value` — o mesmo valor com sinal: `> 0` sai da origem, `< 0` entra no destino | use **sempre `credit_value`** para distinguir as pernas |
| **Rendimento (extract 5)** | rendimento de verdade | perna de saída de migração legada (pré-mai/2025) | só dá para separar via `tb_underwriting_migrations`; no extract isolado são indistinguíveis |
| **Investimento (extract 6)** | aporte novo | perna de entrada de migração legada | idem |

---

## Termos a mapear

Vocabulário de crédito privado e da operação da GCB que provavelmente aparece:

**Operação e crédito**
- Operação / underwriting *(parcialmente mapeado acima)*
- Cedente, sacado, tomador
- Duplicata / nota fiscal
- Precatório / ativo judicial
- CRI, CRA, debênture
- Operação estruturada
- Garantia
- Deságio, taxa, indexador

**Investidor**
- Aporte, captação bruta, captação líquida
- Alocação
- Ativação
- Posição / carteira
- Resgate, portabilidade
- Saldo com rendimento

**Estrutura e times**
- Assessor / banker
- Varejo, Private, WM (Wealth Management)
- DCM
- Patrimônio separado
- Canal único
- FP&A

**Siglas encontradas no ambiente** (confirmar significado antes de usar)
- `AuC`, `AuM`, `AuA`
- `IOP`
- `BaaS` — *Banking as a Service*, mapeado acima
- `TKM`
- `OE` (prefixo de operação estruturada — ex.: OE007)
- `GLPG`
