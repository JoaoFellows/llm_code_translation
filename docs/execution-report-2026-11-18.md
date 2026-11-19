# Relatório de execução e testes — 18/11/2026

> Este relatório registra a execução local anterior, sem modelo real. A rodada concluída com `gemini-3.5-flash-lite` está documentada no [relatório final](gemini-rerun-final-2026-11-18.md).

## Escopo e ambiente

- Checkout do projeto: `ac2b32566295bebf2097334aa5ad377ef19e2c0b`.
- Python 3.12, JDK 21, JUnit 4.13.1, JUnit Platform Console 1.8.1 e PMD 7.1.0.
- Benchmark [ClassEval-T](https://github.com/wLinHoo/ClassEval-T) clonado em `benchmarks/ClassEval-T`, commit `fd41d22e6ee2e7497087f4724d4d0a8292ec9491`.
- Dependências Python instaladas em `.venv/`; ferramentas Java instaladas em `class_translation/tools/`. Esses diretórios são ignorados pelo Git.

## Resultado desta execução

| Execução | Cobertura | Resultado | Modelo usado |
| --- | --- | --- | --- |
| `python -m pytest class_translation repo_translation -q` | Toda a suíte local | **37 passaram, 0 falharam** (134,52 s) | Nenhum; testes usam respostas predefinidas quando precisam de chat |
| Pipeline completo da fixture `counter` | Java → Python | **2/2 testes**, status `passed`; smells 5 → 6 → 5 | Nenhum; `ScriptedChatClient` |
| Pipeline completo da fixture `box` | Python → Java | **2/2 testes**, status `passed`; smells 0 → 1 → 0 | Nenhum; `ScriptedChatClient` |
| Soluções de referência ClassEval-T, alvo Python | 94 classes | **73/94 classes** com todos os testes aprovados; 1.796/1.952 casos aprovados após normalizar uma contagem inválida | Nenhum; código de referência do benchmark |
| Soluções de referência ClassEval-T, alvo Java | 94 classes | **72/94 classes** com todos os testes aprovados; 1.569/1.652 casos aprovados; 15 classes não chegaram a executar testes | Nenhum; código de referência do benchmark |

As duas fixtures executaram tradução, correção, análise de smells e testes de destino. As respostas de tradução foram fornecidas pelo cliente determinístico dos testes. Os detalhes estão em [`reports/fixture_translations.json`](../reports/fixture_translations.json).

Os 188 testes de referência verificaram os runners Python e Java contra as soluções originais do benchmark. Eles **não** representam traduções produzidas por modelo. O resultado por classe, com feedback, está em [`reports/classeval_reference_tests.jsonl`](../reports/classeval_reference_tests.jsonl). A contagem Python exibida no terminal pelo script foi 1.781/1.952, pois o runner retornou `-15` testes aprovados para `StudentDatabaseProcessor`. Para o agregado acima, esse valor inválido foi tratado como zero. O arquivo JSONL mantém o valor bruto para investigação. Das 21 classes de referência que não passaram por completo no alvo Python, algumas falharam na importação do teste ou por dependências; das 22 no alvo Java, 15 tiveram zero testes executados por problemas de compilação ou descoberta de testes. Esses casos impedem interpretar a taxa de aprovação como precisão do tradutor.

## Resultados anteriores encontrados no repositório

Os arquivos abaixo já existiam antes desta execução. Não há data nem hash do benchmark registrados nas linhas, portanto não são diretamente comparáveis com os testes de referência acima.

| Arquivo | Modelo registrado | Resultado histórico |
| --- | --- | --- |
| [`class_translation/results/classeval_gemini.jsonl`](../class_translation/results/classeval_gemini.jsonl) | `gemini-3.5-flash-lite` | 94 classes Java → Python; 55 `passed`, 39 `failed`; 1.694/2.048 casos aprovados |
| [`class_translation/results/classeval_gemini_py2java.jsonl`](../class_translation/results/classeval_gemini_py2java.jsonl) | `gemini-3.5-flash-lite` | 1 classe Python → Java (`AvgPartition`), `passed`, 12/12 casos |

Esses registros contêm métricas, mas não preservam o código traduzido. Por isso, não foi possível repetir seus testes diretamente.

## Traduções com modelo real e demais pipelines

**Nenhuma chamada a modelo real foi realizada nesta execução.** Não há `.env` nem variáveis de ambiente de provedor configuradas. A tentativa de usar uma chave encontrada em `.env.example` para uma chamada curta à OpenAI foi **rejeitada pela revisão automática**: a autorização para usar essa credencial específica não estava explícita, e a chamada poderia gerar cobrança ou expor a chave. Nenhuma chamada foi enviada. Para executar as 94 traduções com um modelo real, é necessária autorização explícita para a credencial e o gasto correspondente; recomenda-se usar uma chave nova em `.env`, pois `.env.example` contém valores com aparência de credenciais.

O `main.py` do artigo não foi executado: `config.py` deixa `base_path_data`, `base_path_testing_docker` e `tco_path` vazios, e os CSVs/árvores de CodeNet, Avatar, EvalPlus e EvoEval não estão presentes. O fluxo RepoTransBench também não foi executado: não há dataset `RepoTransBench-data` nem comando Docker disponível neste ambiente. Assim, seus testes de integração locais passaram, mas não houve tradução nem execução de projeto desse benchmark.

## Como reproduzir

Na raiz do repositório, com as dependências descritas acima:

```powershell
.\.venv\Scripts\python.exe -m pytest class_translation repo_translation -q
.\.venv\Scripts\python.exe -m scripts.run_fixture_translations reports/fixture_translations.json
.\.venv\Scripts\python.exe -m scripts.audit_classeval_references benchmarks/ClassEval-T reports/classeval_reference_tests.jsonl
```

Os scripts [`scripts/run_fixture_translations.py`](../scripts/run_fixture_translations.py) e [`scripts/audit_classeval_references.py`](../scripts/audit_classeval_references.py) registram os resultados desta execução.
