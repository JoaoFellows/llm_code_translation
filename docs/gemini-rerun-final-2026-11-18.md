# Resultado final ClassEval-T com Gemini — 18/11/2026

## Execução

- Modelo: **`gemini-3.5-flash-lite`**, acessado pelo provedor Gemini configurado no projeto.
- A nova `GEMINI_API_KEY` de `.env` respondeu HTTP 200 ao consultar o modelo e ao fazer uma geração mínima. O valor da chave não foi exibido nem gravado.
- Benchmark: [ClassEval-T](https://github.com/wLinHoo/ClassEval-T), commit `fd41d22e6ee2e7497087f4724d4d0a8292ec9491`.
- Pipeline: tradução, correção, redução de smells e testes de destino, com os limites de iteração definidos no projeto. O lote foi retomado pelos JSONL existentes e não repetiu resultados funcionais já salvos.
- A execução começou com uma chave e foi concluída após a troca por uma nova chave. Todas as linhas finais registram o mesmo modelo; os valores das chaves não constam dos arquivos.

## Resultados finais

| Direção | Classes | `passed` | `failed` | Erro de API | Casos de teste aprovados | Classes com zero testes executados |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Java → Python | 94/94 | **56** | 38 | 0 | 1.754/2.051 | 0 |
| Python → Java | 94/94 | **49** | 45 | 0 | 1.140/1.208 | 33 |
| Total | **188/188** | **105** | 83 | **0** | **2.894/3.259** | 33 |

O arquivo final contém **188 chaves únicas** (classe + direção), todas com `model=gemini-3.5-flash-lite` e `status` funcional (`passed` ou `failed`). O [manifesto de pendências](../reports/classeval_gemini_2026-11-18_pending.json) contém zero itens nas duas direções. O resultado consolidado está em [`reports/classeval_gemini_2026-11-18_complete.jsonl`](../reports/classeval_gemini_2026-11-18_complete.jsonl).

`failed` significa que a tradução não passou por todos os testes de destino. Em 33 classes Python → Java, o runner registrou zero testes, geralmente quando o código ou os testes não chegam à etapa de execução válida; o JSONL atual não guarda o feedback detalhado para distinguir as causas por classe. O pipeline também não preserva o código gerado, apenas as métricas. Assim, este relatório mede o comportamento do pipeline nesta execução, não oferece uma auditoria manual do código traduzido.

Para `StudentDatabaseProcessor` em Java → Python, o runner bruto retornou `tests_passed=-16`, valor impossível. No arquivo final, `tests_passed` foi normalizado para zero e o valor original foi mantido em `raw_tests_passed`. O total agregado acima usa zero para essa classe.

## Arquivos e reprodução

- [Resultado final](../reports/classeval_gemini_2026-11-18_complete.jsonl): uma linha por classe e direção, após escolher a última tentativa e normalizar a contagem inválida.
- [Execução bruta Java → Python](../reports/classeval_gemini_2026-11-18.jsonl), [Python → Java 1–59](../reports/classeval_gemini_py2java_2026-11-18.jsonl) e [Python → Java 60–94](../reports/classeval_gemini_py2java_60-94_2026-11-18.jsonl): 194 tentativas no total, incluindo repetições após erros transitórios.
- [Runner retomável](../scripts/run_classeval_gemini_fresh.py) e [consolidador](../scripts/finalize_classeval_results.py).

O [relatório de testes locais e referências](execution-report-2026-11-18.md) documenta os 37 testes de integração aprovados e as limitações dos próprios testes de referência do benchmark. Os JSONL históricos em `class_translation/results/` não foram sobrescritos.
