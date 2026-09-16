# Skill `metabase-backoffice`

Skill do Claude para o time de backoffice da GCB Investimentos: analisar dados e criar
perguntas, gráficos e dashboards no Metabase seguindo as regras de negócio do time.

Existe porque no ambiente da GCB é fácil gerar um número que parece certo e está errado
— 40 bancos conectados, schemas de produção e desenvolvimento lado a lado, mais de 2.600
tabelas de teste do dbt e várias versões divergentes da mesma pergunta salva.

## Plataforma-alvo

**claude.ai / Claude Cowork, instalada na organização.** O `reference/receitas-tecnicas.md`
pressupõe o conector Metabase da organização (`construct_native_query`, `create_question`,
`read_resource` com URIs `metabase://…`).

**Não instale esta skill no Claude Code.** Lá o MCP do Metabase expõe outro conjunto de
ferramentas (`search`, `list`, `retrieve`, `execute`, `export`, sem nenhum `create_*`) e
as receitas técnicas não se aplicam. Para esse caso existe a skill `dashboard-maker`,
pessoal, que escreve no Metabase via `MetabaseClient` em Python.

## Estrutura

```
SKILL.md                      # entrada da skill: regras, fluxo, protocolo de resposta
reference/
  mapa-dados.md               # bancos, schemas, collections, armadilhas
  metricas.md                 # definições canônicas de indicador
  glossario.md                # termo de negócio -> tabela/coluna
  receitas-tecnicas.md        # como criar pergunta/dashboard via conector
GUIA-DE-PREENCHIMENTO.md      # roteiro de manutenção — fora do pacote
release.py                    # gera o .zip de distribuição
```

## Estado

`metricas.md` e `glossario.md` estão parcialmente preenchidos, e `mapa-dados.md` tem
itens `[A CONFIRMAR]` / `[A IDENTIFICAR]`. A skill é desenhada para operar segura mesmo
incompleta: sem definição registrada, ela pergunta em vez de deduzir.

Ver `GUIA-DE-PREENCHIMENTO.md` para o que falta e em que ordem atacar.

## Publicar uma versão

```bash
python3 release.py
```

Gera `metabase-backoffice.zip` na raiz (fora do Git). O `.zip` é o que o admin sobe em
**Organization settings > Skills > "+ Add"**. O Git é a fonte canônica; o `.zip` é só o
artefato de release.

Pré-requisitos na organização: plano Team ou Enterprise, com "Code execution and file
creation" e "Skills" habilitados.

## Contribuir

Toda mudança em `metricas.md` entra por Pull Request com revisão de alguém do backoffice
— é lá que mora a definição oficial de indicador, e mudança silenciosa vira número errado
em decisão.
