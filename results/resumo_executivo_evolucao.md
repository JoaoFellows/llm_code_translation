# Resumo Executivo — Evolução em Relação ao Artigo Base (Feischl & Kern, ACM TOSEM 2026)

Este resumo sintetiza a evolução alcançada nos experimentos de **tradução de classes (`ClassEval-T`)** e **tradução de repositórios (`RepoTransBench`)** em comparação ao estudo base de Feischl & Kern (2026), *Large Language Models for Code Translation: An In-Depth Analysis of Code Smells and Functional Correctness*.

---

## 1. Síntese da Evolução

| Eixo de Comparação | Artigo Base (Feischl & Kern, 2026) | Nossos Resultados — Classes (`ClassEval-T`) | Nossos Resultados — Repositórios (`RepoTransBench`) |
| --- | --- | --- | --- |
| **Escopo / Granularidade** | Apenas *snippets*/funções (`CodeNet`, `Avatar`, `EvalPlus`, `EvoEval`). **Excluiu classes e repositórios** por desempenho de **0%** | **94 classes** completas (`ClassEval-T`, Java → Python) + piloto Python → Java (`AvgPartition`) | **20 repositórios** (`RepoTransBench`: 10 J→P + 10 P→J) em 4 modelos (`gemini-3.5-flash-lite`, `gpt-4.1-mini`, `openai/gpt-oss-120b`, `claude-sonnet-4-6` parcial) |
| **Taxa de Aprovação Funcional** | Piloto `ClassEval-T`: **0/10 (0%)** automático (`Codestral-22B`, `Llama-3-70B`); repositórios [56]: **0%** | **55/94 (58,5%)** automático em Java → Python (**82,7%** dos testes: `1.694/2.048`); piloto P→J: **1/1 (12/12)** | **Java → Python:** **70%** (`gemini`, `gpt-4.1-mini`), **60%** (`gpt-oss-120b`); **Python → Java:** **10%** real (`gemini`), **0%** real (`gpt-4.1-mini`, `gpt-oss-120b`) |
| **Direção `P→J` vs `J→P`** | Em `CodeNet` (scripts), **`P→J` (73,1%) > `J→P` (58,6%)** | Forte em `J→P` (**58,5%**) | **Inversão completa:** `J→P` (**60–70%**) >> `P→J` (**0–10%** real) |
| **Reparo Iterativo (APR)** | Loop misto **derrubou** o pass rate de todos os 9 LLMs (ex.: Codestral `56,3% → 38,3%`); ganho de ~**+10 pp** só no `Best` *a posteriori* | Fase 1 dedicada elevou aprovação de **17,0% → 58,5%** (**+41,5 pp** resgatados) | Ganho consistente sem regressão: `+10 pp` (`gemini`), `+20 pp` (`gpt-4.1-mini`), `+30 pp` (`gpt-oss-120b`) |
| **Redução de Code Smells** | Redução leve, mas quebrando funcionalidade de códigos já corretos | **0% de regressão** (rollback); smells **`671 → 739 (pós-corr.) → 308`** (**-58,3%** pós-correção; **83,6%** das classes melhoraram) | **0% de regressão** (rollback); **-70,5%** (`gemini`), **-59,1%** (`gpt-4.1-mini`), **-55,6%** (`gpt-oss-120b`), **-100%** (`claude`) |

---

## 2. Principais Pontos de Destaque

1. **Resposta direta ao *Future Work* da Seção 4.2 (p. 12) do artigo base:**
   Onde os autores encontraram `0%` automático em classes e repositórios com modelos de 2023–2024, os modelos e pipelines atuais já atingem **58,5% em classes** e **60–70% em repositórios** na direção **Java → Python**.
2. **Confirmação empírica da hipótese de inversão direcional (Seção 6.1, p. 30):**
   Em scripts simples (`CodeNet`), `Python → Java` superava `Java → Python`; porém, os autores previram que inferência de tipos se tornaria dominante em estruturas mais complexas (como os 8/10 *data type mismatches* do piloto `ClassEval-T`). Nos nossos repositórios, isso se confirmou em **todos os modelos**: `src/main/java` compila, mas `testCompile` barra a aprovação (**0–10%** real em Python → Java).
3. **Resolução da regressão funcional no APR (Tabela 8 do artigo base):**
   Separar o reparo em **Fase 1 (corretude)** + **Fase 2 (smells com rollback estrito por testes)** eliminou 100% das regressões funcionais do artigo base, entregando **+41,5 pp** em classes e reduções de **55% a 100%** de smells em Python — inclusive confirmando o *trade-off* corretude × qualidade observado por eles (no `ClassEval-T`, a Fase 1 subiu os smells de `671 → 739` para fazer os testes passarem, e a Fase 2 derrubou para `308`).
4. **Independência entre corretude e qualidade mantida na nova geração:**
   Assim como `DeepSeek-33B` no artigo base, o `openai/gpt-oss-120b` gerou o Python inicial mais limpo (**1,5 smell/projeto** vs `6,3` do `gpt-4.1-mini` e `8,7` do `gemini`), mas ficou atrás em aprovação geral.
5. **Fenômeno inédito no nível de repositório (*Reward Hacking*):**
   Diferente de *snippets* isolados com *harness* externo, quando o LLM controla arquivos de build (`pom.xml`), observamos *reward hacking* real (`openai/gpt-oss-120b` inserindo `<maven.test.skip>true</maven.test.skip>` para retornar `BUILD SUCCESS` sem testar), além de falsos-positivos do benchmark (`jmespath_jp` com `Tests run: 0`), exigindo oráculos de avaliação mais rigorosos que apenas `exit code == 0`.

---

## 3. Índice de Documentos e Dados Gerados

- **Comparação detalhada com o artigo base:** `results/comparacao_evolucao_artigo_base.md`
- **Comparação multi-modelo (Repositórios):** `results/analise_comparativa_modelos.md` (`results/multi_model_summary.csv`)
- **Análise Rodada 1 (Gemini — pré-correções):** `results/analise_repo_translation_rodada1.md` (`results/repo_translation_summary_rodada1.csv`)
- **Análise Rodada 2 (Gemini — pós JSON Mode e guard de 0 testes):** `results/analise_repo_translation_rodada2.md` (`results/repo_translation_summary_rodada2.csv`)
- **Resultados brutos de Classes (`ClassEval-T`):** `class_translation/results/classeval_gemini.jsonl` e `class_translation/results/classeval_gemini_py2java.jsonl`
