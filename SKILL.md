---
name: metabase-backoffice
description: "Analisar dados e criar perguntas, gráficos e dashboards no Metabase da GCB Investimentos usando as regras de negócio do time de backoffice. Use SEMPRE que a pessoa pedir qualquer número, análise, relatório, gráfico ou dashboard sobre operações, liquidação, conciliação, comissão, captação, alocação, resgate, inadimplência, cadastro de cliente, patrimônio separado, DCM, fechamento contábil ou financeiro — mesmo que não cite o Metabase pelo nome, e mesmo que pareça uma pergunta simples de SQL. Use também quando pedirem para montar painel, salvar uma consulta, comparar mês a mês, ou 'puxar' um dado do data warehouse. O ambiente da GCB tem 40 bancos conectados e milhares de tabelas, então responder sem esta skill produz número errado com alta confiança."
---

# Metabase Backoffice — GCB Investimentos

> Esta skill pressupõe o **conector Metabase da organização no claude.ai / Cowork**.
> As ferramentas citadas em `reference/receitas-tecnicas.md` existem nesse ambiente e
> não no Claude Code, cujo MCP do Metabase é somente leitura e execução.

Esta skill existe por um motivo específico: **no ambiente da GCB é fácil gerar um número
que parece certo e está errado.** São 40 bancos conectados, schemas de produção e de
desenvolvimento lado a lado, milhares de tabelas de teste do dbt, e várias versões
divergentes da mesma pergunta salva. Sem orientação explícita, a escolha errada de
banco ou de schema passa despercebida e vira decisão.

O time de backoffice trabalha com conciliação, liquidação, comissão, fechamento e
patrimônio separado. Número errado aqui não é um gráfico feio — é uma decisão errada.

---

## As cinco regras invioláveis

**1. Nunca invente uma definição de negócio.**
Se a métrica pedida não estiver em `reference/metricas.md`, NÃO deduza a partir dos
nomes das colunas. Pergunte à pessoa qual definição usar, ou ofereça mostrar as
versões que já existem salvas no Metabase para ela escolher. Uma pergunta a mais é
sempre mais barata que um número errado.

**2. Sempre mostre o SQL antes de apresentar o resultado.**
Exiba a consulta usada junto com o número. A pessoa do backoffice sabe reconhecer um
filtro errado quando vê, mesmo sem escrever SQL.

**3. Sempre confira contra um número conhecido.**
Antes de apresentar, compare o total com algum valor que o time já conhece (o
fechamento do mês anterior, um relatório existente). Se divergir, diga que divergiu —
não silencie a diferença nem ajuste o filtro até bater.

**4. Nunca use schema de desenvolvimento ou de teste.**
Ver `reference/mapa-dados.md`. Regra curta: nada que comece com `dev_`, nada que
termine em `_dbt_test__audit`, nada de `__segment_reverse_etl`.

**5. Toda pergunta e todo dashboard nasce em rascunho.**
Nada é criado direto numa collection oficial do backoffice. Ver "Onde salvar" abaixo.

---

## Fluxo obrigatório para criar uma pergunta ou dashboard

A sequência não é óbvia e não pode ser pulada. `create_question` **não aceita SQL
direto** — ele exige um identificador de consulta gerado antes.

```
1. search / read_resource        → descobrir banco, schema, tabela e colunas reais
2. execute_sql                   → RODAR a consulta e conferir o resultado
3. construct_native_query        → devolve um query_handle (UUID)
   (ou construct_query para MBQL)
4. create_question               → salva a pergunta, usando o query_handle do passo 3
5. create_dashboard              → cria o dashboard passando question_ids
```

O passo 2 é obrigatório: **nunca salve uma pergunta cuja consulta você não executou.**

Detalhes técnicos, configurações de gráfico e exemplos prontos:
→ leia `reference/receitas-tecnicas.md`

---

## Roteamento: qual banco usar

Este é o erro mais caro do ambiente. Há 40 bancos conectados, com nomes parecidos e
conteúdo sobreposto (por exemplo `FMI PostgreSQL`, `FMI RedShift`, `PeerBR RedShift`,
`PeerBR & Finance RedShift`, `GCB RedShift`, `GCB Finance`, `Finance Summary`).

**Nunca escolha o banco por semelhança de nome.** Consulte `reference/mapa-dados.md`.
Se o caso não estiver mapeado lá, pergunte à pessoa qual banco o time usa para aquele
relatório — ou localize uma pergunta existente sobre o mesmo tema e use o mesmo banco
que ela usa.

Há uma migração em andamento (o banco `PeerBR & Finance RedShift` foi criado em
setembro de 2026). Enquanto `reference/mapa-dados.md` não declarar a fonte oficial de
um domínio, **pergunte antes de assumir**.

---

## Onde salvar

| Situação | Destino |
|---|---|
| Qualquer coisa criada nesta conversa | Collection de rascunho do backoffice |
| Só depois de revisão humana | Collection oficial correspondente |

Nunca salve direto em: Contábil, Financeiro, Jurídico, Comissão, DCM, FP&A,
Patrimônio Separado, Rotinas Diárias, ou 🚨Alertas. Essas são pastas de números
oficiais e têm dono.

Os ids das collections estão em `reference/mapa-dados.md`.

**Padrão de nomenclatura:**
- Pergunta: `[Assunto] — [recorte]` — ex.: `Comissão — por assessor, mensal`
- Dashboard: `[Área] — [tema]` — ex.: `Backoffice — Fechamento Comissão`
- Rascunho: prefixo `[RASCUNHO]`

**Descrição é obrigatória** em toda pergunta e todo dashboard, e precisa conter:
fonte (banco e tabela), regra de negócio aplicada, e qualquer limitação conhecida do
dado. Já existem bons exemplos desse padrão no Metabase da GCB — siga-os.

---

## Protocolo de resposta

Ao entregar qualquer número, estruture assim:

1. **O número**, com a unidade e o período explícitos
2. **A definição usada**, em uma frase de negócio (não em SQL)
3. **O SQL**
4. **A aferição**: contra o que foi conferido e se bateu
5. **As ressalvas**: o que ficou de fora, o que é estimativa, o que não dá para afirmar

Se algum desses cinco itens não puder ser preenchido, diga isso explicitamente em vez
de omitir.

---

## Quando NÃO usar esta skill

- Perguntas conceituais sobre o mercado financeiro sem consulta a dado
- Trabalho em Redshift/AWS fora do Metabase (pipelines, dbt, Step Functions)
- Qualquer pedido que envolva alterar dado de origem — esta skill é somente leitura no
  banco; a única escrita permitida é criar objetos no próprio Metabase

---

## Dados sensíveis

O ambiente contém CPF, saldo, posição e dados cadastrais de clientes.

- Prefira sempre resultados **agregados**. Só traga linha a linha se a pessoa pedir
  explicitamente e a tarefa exigir
- Nunca inclua CPF, e-mail, telefone ou endereço num dashboard sem que tenha sido
  pedido de forma explícita
- Nunca exporte base completa de clientes
- Na dúvida sobre exposição de dado pessoal, pergunte antes

---

## Arquivos de referência

Leia sob demanda, não todos de uma vez:

| Arquivo | Quando ler |
|---|---|
| `reference/mapa-dados.md` | Sempre, antes da primeira consulta da conversa |
| `reference/metricas.md` | Sempre que a pessoa pedir um indicador nomeado |
| `reference/glossario.md` | Quando aparecer um termo de negócio que você não mapeia para tabela/coluna |
| `reference/receitas-tecnicas.md` | Ao criar ou editar pergunta, gráfico ou dashboard |
