# Skill `metabase-backoffice`

Skill do Claude para o time de backoffice da GCB Investimentos: analisar dados e criar
perguntas, gráficos e dashboards no Metabase seguindo as regras de negócio do time.

Existe porque no ambiente da GCB é fácil gerar um número que parece certo e está errado
— 40 bancos conectados, schemas de produção e desenvolvimento lado a lado, mais de 2.600
tabelas de teste do dbt e várias versões divergentes da mesma pergunta salva.

## Onde roda

Em qualquer superfície do Claude com o **conector Metabase da GCB acoplado**:
Claude Desktop / claude.ai e Claude Code. O `reference/receitas-tecnicas.md` usa as
ferramentas desse conector (`construct_native_query`, `create_question`,
`create_dashboard`, `read_resource` com URIs `metabase://…`).

Sem o conector acoplado a skill não tem como executar nada — as receitas técnicas
dependem dele.

### Instalar

- **Claude Desktop / claude.ai (pessoal):** `python3 release.py` e suba o zip em
  *Customize > Skills > "+" > Create skill > Upload a skill*. Para atualizar, suba o zip
  de novo por cima.
- **Organização (Team/Enterprise):** o admin sobe o mesmo zip em
  *Organization settings > Skills*. Fica habilitada por padrão para todo mundo.
- **Claude Code:** aponte a pasta de skills para este repo —
  `ln -s <caminho-do-repo> ~/.claude/skills/metabase-backoffice`. Symlink em vez de cópia
  faz a skill acompanhar o repo sem reinstalar.

Pré-requisito na organização: "Code execution and file creation" e "Skills" habilitados
em *Organization settings > Skills*.

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

Gera `metabase-backoffice.zip` na raiz, com a pasta-raiz e o layout que o upload exige.
Fica fora do Git: o repositório é a fonte canônica, o `.zip` é só artefato de release.

Não há sync automático entre este repo e a skill instalada — depois de mudar algo aqui,
gere o zip e suba de novo.

## Contribuir

Toda mudança em `metricas.md` entra por Pull Request com revisão de alguém do backoffice
— é lá que mora a definição oficial de indicador, e mudança silenciosa vira número errado
em decisão.
