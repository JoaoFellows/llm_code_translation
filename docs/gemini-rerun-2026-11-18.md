# Nova execução ClassEval-T com Gemini — 18/11/2026

> Este documento registra a interrupção por cota na primeira chave. A execução foi retomada com uma nova chave e concluída. Veja o [relatório final](gemini-rerun-final-2026-11-18.md) e o [JSONL completo](../reports/classeval_gemini_2026-11-18_complete.jsonl).

## Modelo e método

- Provedor: Gemini, modelo **`gemini-3.5-flash-lite`**.
- Credencial: `GEMINI_API_KEY` de `.env`; seu valor não foi exibido nem gravado nos resultados.
- Benchmark: [ClassEval-T](https://github.com/wLinHoo/ClassEval-T), commit `fd41d22e6ee2e7497087f4724d4d0a8292ec9491`, com 94 classes por direção.
- Pipeline: tradução, até três correções, até três tentativas de reduzir smells, execução dos testes de destino e contagem final de smells. Python usa unittest/Pylint; Java usa JUnit/PMD.
- Arquivo consolidado desta rodada: [`reports/classeval_gemini_2026-11-18_partial.jsonl`](../reports/classeval_gemini_2026-11-18_partial.jsonl). Ele contém uma linha por classe e direção, com a tentativa mais recente.

## Resultados obtidos até o bloqueio de cota

| Direção | Classes com registro | `passed` | `failed` | Erro de API | Casos de teste aprovados |
| --- | ---: | ---: | ---: | ---: | ---: |
| Java → Python | 78/94 | 48 | 28 | 2 | 1.474/1.608 nos registros com testes |
| Python → Java | 25/94 | 17 | 8 | 0 | 387/397 |

O piloto `AvgPartition` passou em ambas as direções: 11/11 testes em Java→Python e 12/12 em Python→Java. As linhas `failed` representam traduções executadas cujos testes não passaram por completo. As duas linhas `error` de Java→Python (`StockPortfolioTracker` e `StudentDatabaseProcessor`) ocorreram por `429` da API, sem resultado funcional final.

Restam **16 classes sem registro e 2 com erro de API** em Java→Python, além de **69 sem registro** em Python→Java: 87 classes/direções ainda precisam de uma execução válida. A lista exata está em [`reports/classeval_gemini_2026-11-18_pending.json`](../reports/classeval_gemini_2026-11-18_pending.json). Estes resultados são **parciais** e não representam a taxa final das 94 classes em cada direção.

## Por que a execução parou

O endpoint de geração do Gemini respondeu `429 RESOURCE_EXHAUSTED` e informou que a cota gratuita de **500 solicitações de geração por dia** para `gemini-3.5-flash-lite` havia sido excedida. No momento do diagnóstico, a API indicou espera de aproximadamente **11 horas e 32 minutos**. Os processos foram interrompidos após salvar os resultados já concluídos. A listagem de modelos e uma chamada isolada chegaram a responder, mas o limite diário voltou a bloquear as gerações seguintes; a resposta nativa da API confirmou a métrica diária.

Nenhuma das 87 tarefas restantes foi marcada como falha de tradução por causa da cota. Os JSONL brutos preservam todas as tentativas, inclusive erros transitórios e repetições:

- [`reports/classeval_gemini_2026-11-18.jsonl`](../reports/classeval_gemini_2026-11-18.jsonl): Java→Python e o piloto `AvgPartition` Python→Java.
- [`reports/classeval_gemini_py2java_2026-11-18.jsonl`](../reports/classeval_gemini_py2java_2026-11-18.jsonl): início de Python→Java.
- [`reports/classeval_gemini_py2java_60-94_2026-11-18.jsonl`](../reports/classeval_gemini_py2java_60-94_2026-11-18.jsonl): faixa final de Python→Java.

## Retomada após a renovação da cota

Os comandos abaixo reutilizam os JSONL brutos e pulam itens com resultado funcional; itens com `status=error` são repetidos. Execute-os em sequência para respeitar a cota da conta. Se a cota terminar outra vez, os arquivos continuam retomáveis.

```powershell
.\.venv\Scripts\python.exe -m scripts.run_classeval_gemini_fresh --output reports/classeval_gemini_2026-11-18.jsonl --direction java_to_python
.\.venv\Scripts\python.exe -m scripts.run_classeval_gemini_fresh --output reports/classeval_gemini_py2java_2026-11-18.jsonl --direction python_to_java --start 1 --stop 59
.\.venv\Scripts\python.exe -m scripts.run_classeval_gemini_fresh --output reports/classeval_gemini_py2java_60-94_2026-11-18.jsonl --direction python_to_java --start 60 --stop 94
```

Depois, consolide novamente:

```powershell
.\.venv\Scripts\python.exe -m scripts.finalize_classeval_results --input reports/classeval_gemini_2026-11-18.jsonl --input reports/classeval_gemini_py2java_2026-11-18.jsonl --input reports/classeval_gemini_py2java_60-94_2026-11-18.jsonl --output reports/classeval_gemini_2026-11-18_partial.jsonl --benchmark-root benchmarks/ClassEval-T --pending-output reports/classeval_gemini_2026-11-18_pending.json
```

Os registros antigos em `class_translation/results/` não foram sobrescritos.
