# Receitas técnicas — MCP do Metabase

Ferramentas do conector Metabase. Tudo aqui foi verificado por execução real no
Metabase da GCB em 16/09/2026.

## Índice
- Sequência de criação
- Configuração de gráfico
- Montar e editar dashboard
- Arquivar
- Descoberta do ambiente
- Erros comuns

---

## Sequência de criação

`create_question` **não aceita SQL como texto.** Ele exige um `query_handle`, que é um
UUID devolvido por um passo anterior. Pular isso é o erro mais frequente.

```
execute_sql(database_id, sql)
  → RODA a consulta. Sempre faça isto primeiro e confira o resultado.

construct_native_query(database_id, sql)
  → devolve {"query_handle": "uuid"}
  → NÃO executa nada

create_question(collection_id, name, description, display,
                query = <query_handle>, visualization_settings)
  → devolve id da pergunta + URL

create_dashboard(collection_id, name, description,
                 question_ids = [id1, id2, ...])
  → devolve id do dashboard + URL. Os cards são posicionados automaticamente.
```

Para MBQL em vez de SQL, troque `construct_native_query` por `construct_query`. Note
que MBQL exige referência de campo no formato portátil de 4 segmentos
`["field", {}, [banco, schema, tabela, coluna]]`, com o mapa de opções vazio `{}`
obrigatório na posição 1.

**Regra:** salvar pergunta exige permissão de native query no banco alvo.

---

## Configuração de gráfico

Sem `visualization_settings`, o gráfico sai como tabela mesmo com `display` definido.
É preciso dizer qual coluna é o eixo e qual é a medida.

```json
{"graph.dimensions": ["coluna_do_eixo"], "graph.metrics": ["coluna_do_valor"]}
```

Valores aceitos em `display`:
`table`, `bar`, `line`, `pie`, `scatter`, `area`, `row`, `combo`, `pivot`,
`scalar`, `smartscalar`, `gauge`, `progress`, `funnel`, `map`, `waterfall`, `sankey`

Escolha por intenção:

| Intenção | display |
|---|---|
| Um número único (total do mês) | `scalar` |
| Número com comparação de período | `smartscalar` |
| Série temporal | `line` |
| Comparação entre categorias | `bar` (ou `row` se os rótulos forem longos) |
| Progresso contra meta | `progress` |
| Etapas de um funil | `funnel` |
| Composição de uma variação | `waterfall` |
| Detalhe linha a linha | `table` |

Evite `pie` — com mais de quatro fatias fica ilegível; prefira `bar`.

---

## Montar e editar dashboard

`update_dashboard` aceita mutações de card via `dashcards`:

```json
[{"action": "add", "card_id": 123, "display_size": "wide"},
 {"action": "remove", "dashcard_id": 456},
 {"action": "move", "dashcard_id": 789, "position": "top"}]
```

`display_size` aceita `wide`, `tall` e `full`.
Para descobrir os `dashcard_id`, leia `metabase://dashboard/{id}/items`.

Ordem recomendada de leitura num dashboard de backoffice, de cima para baixo:
1. Números-chave em `scalar` / `smartscalar`
2. Evolução temporal em `line`
3. Quebras por categoria em `bar` / `row`
4. Detalhe em `table`, por último

---

## Arquivar

Não existe exclusão definitiva pelo MCP. O que existe é arquivamento, que manda para a
lixeira do Metabase e é reversível pela interface.

```
update_dashboard(id, archived = true)
update_question(id, archived = true)
```

---

## Descoberta do ambiente

```
search(term_queries=[...], semantic_queries=[...])
  → tabelas, perguntas, dashboards e collections
  → use search_native_query para procurar DENTRO do SQL das perguntas salvas
     (é assim que se descobre a regra de negócio que o time realmente usa)

read_resource(uris=[...])   # até 5 URIs por chamada, listas limitadas a 25 itens
  metabase://databases
  metabase://database/{id}/tables
  metabase://collection/{id}/items      (append ?page=2 para paginar)
  metabase://dashboard/{id}/items
  metabase://question/{id}
  metabase://table/{id}/fields
```

---

## Erros comuns

| Sintoma | Causa | Correção |
|---|---|---|
| `create_question` recusa a consulta | Passou SQL em vez de `query_handle` | Rode `construct_native_query` antes |
| Gráfico sai como tabela | Faltou `visualization_settings` | Informe `graph.dimensions` e `graph.metrics` |
| Pergunta some | Salva na collection pessoal | `collection_id` omitido salva no pessoal; `null` salva na raiz |
| Resultado vazio ou estranho | Schema de dev ou de teste | Confira em `mapa-dados.md` |
| Número não bate com o relatório do time | Banco errado entre os 40 | Localize a pergunta existente do time e use o mesmo banco |
| Busca só retorna `not_null_*` / `unique_*` | Caiu nas tabelas de teste do dbt | Refaça a busca restringindo a `dw_mart` |
