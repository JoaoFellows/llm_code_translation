# Resultados de tradução de classes

Os arquivos JSONL têm uma linha por classe e direção. Os relatórios Markdown resumem os testes e os code smells; os JSONL preservam os registros por execução.

## Execuções completas

| Modelo | Classes × direções | Relatório | Dados |
| --- | ---: | --- | --- |
| GPT-4.1 mini, 19/11/2026 | 94 × 2 | [Relatório completo](relatorio_gpt41mini_classeval_94_2026-11-19.md) | [Python→Java, classes 1–50](classeval_openai_gpt41mini_2026-11-19.jsonl), [51–94](classeval_openai_gpt41mini_python_to_java_51-94_2026-11-19.jsonl); [Java→Python, classes 1–50](classeval_openai_gpt41mini_java_to_python_2026-11-19.jsonl), [51–94](classeval_openai_gpt41mini_java_to_python_51-94_2026-11-19.jsonl) |
| Gemini 3.5 Flash Lite, 18/11/2026 | 94 × 2 | [Relatório da execução](../docs/gemini-rerun-final-2026-11-18.md) | [JSONL completo](classeval_gemini_2026-11-18_complete.jsonl) |

Para reproduzir a consolidação do GPT-4.1 mini, execute `python -m scripts.summarize_classeval_openai_batch` na raiz do projeto. O runner `python -m scripts.run_classeval_openai_batch` usa o clone local do ClassEval-T e `OPENAI_API_KEY` no `.env`. Ele grava checkpoints e pula classes já concluídas.

## Outros registros

Os arquivos `partial`, `pending` e os JSONL de uma única direção ou classe são registros intermediários e testes exploratórios. `classeval_reference_tests.jsonl` guarda a auditoria dos testes de referência; `fixture_translations.json` guarda o teste local com respostas simuladas.
