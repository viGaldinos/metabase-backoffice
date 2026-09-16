# Guia de preenchimento — skill metabase-backoffice

Este arquivo é para você, não para a skill. Não empacote junto (o `release.py` já o
deixa de fora).

## O que já está pronto e o que falta

**Pronto** (verificado por execução real no Metabase em 16/09/2026):
- Sequência técnica de criação de pergunta e dashboard
- Configurações de gráfico
- Mapa de schemas do banco 42: o que usar e o que ignorar
- Ids das duas collections de backoffice e suas subpastas
- Protocolo de validação e regras de segurança de dado

**Redigido a partir da wiki do time de dados, aguardando validação do backoffice:**
- `reference/metricas.md` — Novação e Migração
- `reference/glossario.md` — domínio novação/migração + termos ambíguos
- `reference/mapa-dados.md` — filtros obrigatórios de `tb_extract`, armadilha de
  soft-delete

**Falta** — e só o time de backoffice pode preencher:
- As outras dez métricas de `reference/metricas.md`
- O resto de `reference/glossario.md`
- Em `reference/mapa-dados.md`, tudo marcado `[A CONFIRMAR]` e `[A IDENTIFICAR]`
- Validar as duas definições redigidas: dono, valor de aferição, e rodar o SQL (está
  marcado `[NÃO EXECUTADO]`)

A skill está desenhada para funcionar mesmo vazia: sem definição registrada, ela
pergunta em vez de inventar. Ela fica útil quando você preenche, mas não fica perigosa
antes disso.

## As quatro perguntas que destravam mais coisa

1. **Banco 42 ou banco 60?** O `PeerBR & Finance RedShift` foi criado em 11/09/2026.
   Enquanto não se souber qual é a fonte oficial, toda resposta fica sob ressalva.
2. **`public` ou `dw_mart`?** `mapa-dados.md` manda preferir `dw_mart`, mas as definições
   de novação/migração vêm de investigação feita sobre tabelas transacionais em `public`.
   Não está decidido qual camada o backoffice deve ler nesses domínios.
3. **Quais são os bancos 47 e 13?** Perguntas de Captação, Ativações e Taxa Especial
   do backoffice apontam para eles e não consegui identificá-los.
4. **Qual versão da "Taxa Especial no ato" é a vigente?** Existem pelo menos cinco
   variantes em três bancos diferentes.

## Ordem sugerida

1. Criar a collection de rascunho do backoffice e anotar o id em `mapa-dados.md`
2. Levar Novação e Migração para o backoffice validar — são as duas primeiras entradas
   escritas, e servem de modelo do nível de detalhe esperado nas outras
3. Varrer a wiki do time de dados (`data-team-llm-wiki`) por outros domínios já
   documentados — é a fonte de melhor qualidade porque já passa por revisão em PR
4. Abrir a collection **🚨Alertas (id 2300)** — a descrição dela é literalmente
   "Alertas de regras de negócio do time de backoffice". É o ponto de partida mais
   rico dentro do próprio Metabase
5. Varrer o SQL das perguntas salvas por tema (`search` com `search_native_query`) e
   montar o quadro de divergências
6. Levar o quadro para o backoffice decidir — você não decide, você instrui a decisão
7. Preencher `metricas.md` com o que for decidido, incluindo o **valor de aferição**
8. Preencher `glossario.md` com o vocabulário que apareceu no caminho

### Fontes de preenchimento, em ordem de qualidade

1. `data-team-llm-wiki` — wiki do time de dados, revisada por Pull Request
2. Collection 🚨Alertas (id 2300) no Metabase
3. SQL das perguntas salvas nas subpastas do backoffice
4. Descrições de dashboards existentes
5. Projeto `data-engineering-dbt`

## Antes de distribuir

- Confirmar o plano da GCB (Team ou Enterprise) e se "Code execution and file creation"
  e "Skills" estão habilitados nas configurações da organização — skills exigem
  execução de código
- Rodar como piloto com 2 pessoas do backoffice antes de pedir provisionamento
- Manter o repositório com revisão por Pull Request de alguém do backoffice

## Empacotar para distribuir

```bash
python3 release.py
```

O `.zip` é o que o admin sobe em Organization settings > Skills > "+ Add".
O Git é a fonte canônica; o `.zip` é só o artefato de release e não é versionado.

## Três prompts para entregar junto no piloto

Entregue estes para colar, não um manual:

- "Quanto foi a captação bruta do mês passado? Me mostra o SQL e confere contra o
  fechamento."
- "Monta um dashboard de rascunho com comissão por assessor nos últimos 3 meses."
- "Quais perguntas salvas existem sobre liquidação e qual delas é a versão mais
  recente?"

O terceiro é o melhor teste: ele exercita a busca dentro do SQL salvo e expõe
divergência de versão, que é o problema real do ambiente.
