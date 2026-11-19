# ClassEval-T — BankAccount com gpt-4.1-mini

Execução em 18/11/2026 (horário de São Paulo), usando a API oficial da OpenAI. A classe e os testes vêm do benchmark público ClassEval-T. Cada direção foi executada uma vez com a mesma configuração do pipeline.

## Resultado final

| Direção | Acertos nos testes | Taxa | Code smells finais | Correções | Loops de smells | Estado |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Python → Java | 23/23 | 100% | 0 | 0 | 0 | Passou |
| Java → Python | 9/22 | 40,9% | 8 | 3 | 0 | Falhou |

## Evolução por loop

| Direção | Fase | Iteração | Acertos | Code smells |
| --- | --- | ---: | ---: | ---: |
| Python → Java | Tradução inicial | 0 | 23/23 | 0 |
| Java → Python | Tradução inicial | 0 | 9/22 | 8 |
| Java → Python | Correção | 1 | 12/22 | 7 |
| Java → Python | Correção | 2 | 12/22 | 7 |
| Java → Python | Correção | 3 | 9/22 | 8 |

Python → Java passou em todos os testes e teve 0 smells já na primeira tradução. Java → Python alcançou seu melhor resultado na primeira e na segunda correção, com 12/22 testes e 7 smells, mas a terceira correção piorou o resultado final. O pipeline limita a correção a 3 iterações e só inicia o grafo de redução de smells quando os testes passam; por isso não houve loops de smells em nenhuma direção.

Os acertos são os testes do benchmark para a linguagem de destino: JUnit em Java e `unittest` em Python. Os smells foram contados pelo PMD 7.1.0 para Java e pelo Pylint para Python. As contagens de ferramentas diferentes não são diretamente comparáveis entre as duas direções.

Dados completos da execução: `classeval_openai_gpt41mini_bankaccount_2026-11-18.jsonl`.
