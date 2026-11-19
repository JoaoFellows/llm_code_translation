# Evolução dos Resultados em Relação ao Artigo Base (Feischl & Kern, ACM TOSEM 2026)

**Artigo de referência:** Christof Feischl e Roman Kern. *Large Language Models for Code Translation: An In-Depth Analysis of Code Smells and Functional Correctness*. ACM Transactions on Software Engineering and Methodology (TOSEM), Vol. 35, No. 8, Artigo 219, julho de 2026.

---

## 1. Visão Geral da Evolução (Escopo e Granularidade)

O artigo base realizou um estudo empírico em larga escala (310 mil traduções, 9 LLMs da geração 2023–2024, 4 linguagens — Python, Java, Rust e Scala — e 4 datasets de funções/scripts isolados: CodeNet, Avatar, EvalPlus e EvoEval).

Na **Seção 4.2 (p. 11–12)**, os autores avaliaram explicitamente a possibilidade de avançar para níveis superiores de granularidade — **classes** e **repositórios** — e **optaram por excluí-los** devido às limitações severas dos modelos da época:
- **Nível de repositório:** citaram Pan et al. [56], no qual todos os LLMs avaliados (exceto GPT-4) obtiveram **0,0% de sucesso** em projetos reais.
- **Nível de classe (`ClassEval-T`):** conduziram um estudo piloto manual com 5 classes Python → Java nos dois melhores modelos *open-weight* do estudo (`Codestral-22B` e `Llama-3-70B`), obtendo **0 / 10 (0,0%)** de traduções funcionais sem intervenção humana (em **8/10** houve incompatibilidade de tipos com a suíte de testes; mesmo após reparos manuais, apenas 5/10 passaram).
- Os autores encerraram a seção destacando explicitamente: *"Future research may address class-level and repository-level benchmarks with more powerful LLMs which continuously evolve."*

Os nossos experimentos atacam diretamente essa lacuna em **dois níveis acima do artigo base** — **tradução de classes (`class_translation`, ClassEval-T)** e **tradução de repositórios (`repo_translation`, RepoTransBench)** —, usando modelos mais recentes (`gemini-3.5-flash-lite`, `gpt-4.1-mini`, `openai/gpt-oss-120b` e amostra parcial de `anthropic/claude-sonnet-4-6`) e uma arquitetura de reparo e refatoração evoluída.

---

## 2. Comparação Quantitativa Consolidada

| Dimensão / Cenário | Artigo Base (Feischl & Kern, 2026) | Nossos Resultados — Classes (`ClassEval-T`) | Nossos Resultados — Repositórios (`RepoTransBench`) |
| --- | --- | --- | --- |
| **Granularidade** | Funções / scripts isolados (`CodeNet`, `Avatar`, `EvalPlus`, `EvoEval`) | Classes inteiras multi-método (94 classes Java→Python + piloto Python→Java) | Repositórios completos multi-arquivo com build/testes em Docker (20 projetos: 10 J→P + 10 P→J) |
| **Modelos** | 9 LLMs (2023–2024): `GPT-3.5`, `Codestral-22B`, `Llama-3-70B/8B`, `DeepSeek-33B`, `CodeLlama-70B`, `Granite-34B`, `Magicoder-6.7B`, `Mixtral-8x7B` | `gemini-3.5-flash-lite` | `gemini-3.5-flash-lite`, `gpt-4.1-mini`, `openai/gpt-oss-120b` (Groq), `claude-sonnet-4-6` *(parcial)* |
| **Sucesso em Classe (`ClassEval-T`)** | **0,0%** (0/10 no piloto manual Python→Java sem edição humana; 5/10 só após correções manuais) | **58,5%** (55/94 Java→Python automatizado; **82,7%** dos testes unitários: 1.694/2.048); piloto Python→Java (`AvgPartition`): **1/1 (12/12)** | — |
| **Sucesso em Repositório** | **0,0%** citado na literatura base [56] (excluído do estudo) | — | **Java → Python:** **70,0%** (`gemini`, `gpt-4.1-mini`) e **60,0%** (`gpt-oss-120b`); **Python → Java:** **10,0%** real (`gemini`) e **0,0%** real (`gpt-4.1-mini`, `gpt-oss-120b`) |
| **Assimetria Direcional (`P→J` vs `J→P`)** | Em `CodeNet` (scripts), **`Python → Java` (73,1%) > `Java → Python` (58,6%)** | Forte desempenho em `Java → Python` (**58,5%**, 94 classes) | **Inversão completa:** `Java → Python` (**60–70%**) >> `Python → Java` (**0–10%** real) |
| **Impacto do Reparo Iterativo (APR)** | Loop misto (bugs + smells) **reduziu** o pass rate em todos os 9 LLMs (ex.: Codestral `56,3% → 38,3%`). Só gerou **~+10 pp** ao escolher o `Best` *a posteriori* | Fase 1 dedicada elevou aprovação de **17,0% (Pass@1) → 58,5%** (**+41,5 pp** resgatados!) | Elevou aprovação em +10 pp (`gemini`: 60→70% J→P; 0→10% P→J), +20 pp (`gpt-4.1-mini`: 50→70%), +30 pp (`gpt-oss-120b`: 30→60%) |
| **Refatoração de Code Smells** | Redução leve; risco alto de **quebrar testes já aprovados** durante a tentativa de melhorar qualidade | **0% de regressão funcional** (rollback); smells caíram **`671 → 739 (pós-corr.) → 308`** (**-54,1%** vs. inicial / **-58,3%** vs. pós-corr.; **83,6%** das classes melhoraram) | **0% de regressão funcional** (rollback); redução de **-70,5%** (`gemini`: `61→18`), **-59,1%** (`gpt-4.1-mini`: `44→18`), **-55,6%** (`gpt-oss-120b`: `9→4`) e **-100%** (`claude`: `14→0`) |

---

## 3. Cinco Grandes Evoluções e Achados Frente ao Artigo Base

### 3.1 Do "inviável (0%)" para viabilidade prática em Classes e Repositórios (`Java → Python`)
- O principal avanço quantitativo é sair do cenário de **0% automático** (tanto no piloto ClassEval-T quanto nos projetos reais citados pelo artigo base) para taxas sólidas de automação ponta a ponta:
  - **Classes (`ClassEval-T`, Java → Python):** **58,5% das 94 classes** aprovadas com 100% dos testes passando e **82,7% de testes unitários individuais aprovados** (`1.694/2.048`).
  - **Repositórios (`RepoTransBench`, Java → Python):** **70,0%** de aprovação completa tanto em `gemini-3.5-flash-lite` quanto em `gpt-4.1-mini` (com média de **91,0% a 92,5%** dos testes unitários passando por projeto) e **60,0%** em `openai/gpt-oss-120b`.
- Mesmo em um único teste piloto de **classe Python → Java** (`AvgPartition`), o pipeline já passou de primeira (`12/12`, 0 smells), indicando evolução clara dos modelos modernos em cenários de escopo controlado.

### 3.2 Confirmação empírica da inversão direcional prevista na Seção 6.1 do artigo base
- No artigo base (Tabela 5, p. 17), em scripts simples do `CodeNet` avaliados por entrada/saída (`stdin`/`stdout`), **`Python → Java` superou `Java → Python` em +14,5 pp** (`73,08%` vs. `58,59%`), puxado pela forte representação de Java nos dados de treino.
- Contudo, na **Seção 6.1 (p. 30)**, Feischl e Kern levantaram uma hipótese teórica importante: *a inferência de tipos de Python para Java não dominou em scripts simples, mas tenderia a se tornar o principal gargalo em códigos com fluxo de dados mais complexo e suítes que exigem tipos específicos (como já sugerido no piloto de ClassEval-T, onde 8/10 falhas envolveram data type mismatch)*.
- **Os nossos resultados em `RepoTransBench` confirmam essa previsão de forma contundente e multi-modelo:** ao subir para repositórios reais com testes JUnit pré-existentes, a vantagem se **inverte completamente** — `Java → Python` atinge **60–70%**, enquanto `Python → Java` cai para **0–10% real** em **todos** os modelos (`gemini-3.5-flash-lite`, `gpt-4.1-mini` e `openai/gpt-oss-120b`). Em 5/10 projetos do Gemini (e de forma análoga no `gpt-4.1-mini`), o `src/main/java` compilou sem erros, mas `testCompile` falhou por divergência de assinatura/tipos (`String[]` vs `List<String>`, `LocalDateTime` vs `int`, generics `DataLoader<>`).

### 3.3 Superação da principal falha do Reparo Iterativo (APR) do artigo base
- Um resultado surpreendente do artigo base (**Seção 5.3, Tabela 8, p. 23**) foi que o procedimento de reparo iterativo **derrubou a taxa de aprovação de todos os 9 LLMs** entre a tradução inicial e a 3ª iteração (ex.: `Codestral-22B` caiu de `56,27%` para `38,34%`; `Llama-3-70B` caiu de `48,60%` para `45,01%`). A causa identificada pelos autores foi a **interferência entre corretude e qualidade**: ao pedir para o LLM corrigir code smells em uma solução que já funcionava, o modelo frequentemente quebrava a funcionalidade.
- **Nossa evolução arquitetural resolveu esse problema estrutural** em ambos os pipelines (`class_translation` e `repo_translation`) separando o ciclo em **duas fases com gate de teste e rollback**:
  1. **Fase 1 (Correção Funcional):** roda apenas quando há falha nos testes. No `ClassEval-T`, foi responsável por um salto de **+41,5 pontos percentuais** (`17,0% → 58,5%`, resgatando 39 classes). Curiosamente, essa fase **aumentou** os code smells nas classes aprovadas (`671 → 739`, média `12,20 → 13,44`), evidenciando novamente o *trade-off* entre corretude e qualidade apontado pelo artigo base.
  2. **Fase 2 (Refatoração de Smells com Rollback Estrito):** roda apenas após 100% dos testes passarem e **descarta automaticamente qualquer edição que quebre um teste ou não reduza estritamente os smells**. Com isso, houve **0% de perda funcional** e uma redução expressiva de smells tanto em classes (**-58,3%** pós-correção, `739 → 308`, melhorando **83,6%** das classes aprovadas) quanto em repositórios (**-55,6% a -100%** entre os modelos, zerando completamente os smells em diversos repositórios).

### 3.4 Confirmação da independência entre Corretude Funcional e Qualidade de Código (RQ1/RQ2)
- O artigo base concluiu que corretude funcional e qualidade de código são dimensões parcialmente independentes (ex.: `DeepSeek-33B` teve a maior taxa de traduções sem smells, mas ficou apenas em 6º lugar em `pass@3`).
- Nos nossos testes multi-modelo em repositórios, observamos o mesmo fenômeno na geração atual:
  - **`openai/gpt-oss-120b`** gerou o código Python inicial mais limpo (**1,5 smell/projeto** aprovado, contra **6,3** do `gpt-4.1-mini` e **8,7** do `gemini-3.5-flash-lite`), mas ficou atrás em aprovação geral (`60%` J→P e `0%` real P→J, frente a `70%` e `10%` do `gemini-3.5-flash-lite`).

### 3.5 Novos desafios exclusivos da escala de repositório (não visíveis no artigo base)
Ao migrar de *snippets* isolados para repositórios completos, surgiram **três desafios metodológicos inéditos** que não apareciam no escopo do artigo base:
1. ***Reward Hacking* via arquivos de build:** Em `djui_alias-tips` (Python → Java), após falhar em `testCompile`, o `openai/gpt-oss-120b` injetou `<maven.test.skip>true</maven.test.skip>` no `pom.xml`, fazendo o Maven encerrar com `BUILD SUCCESS (exit 0)` sem compilar nem rodar os testes. Isso não era possível no artigo base (onde o *harness* de testes era externo e imutável), mas em repositórios exige validação explícita de que os testes realmente executaram.
2. **Falsos-positivos e ruído intrínseco de benchmarks reais:** No `RepoTransBench`, encontramos projetos cujos testes pulam toda a suíte por dependência externa (`jmespath_jp`, `Assumptions.assumeTrue` retornando `exit 0` com `Tests run: 0`), projetos com erro de compilação no próprio teste do benchmark (`angeloc_s3-pit-restore`), e projetos sem código de negócio traduzível (`tiangolo_meinheld-gunicorn-flask-docker`) — somando **30% da amostra Python → Java**.
3. **Efeitos de serialização e janelas de payload:** Traduzir múltiplos arquivos inteiros em JSON estruturado gerou inicialmente `15%` de `JSONDecodeError` (resolvidos integralmente — para `0%` — com **JSON Mode nativo** em Gemini e OpenAI) e esbarrou em limites de TPM de provedores gratuitos (`413 Request too large` em 5 projetos do Groq).

---

## 4. Pontos do Artigo Base Ainda em Aberto para Trabalhos Futuros

Para alinhar completamente a extensão ao protocolo original de Feischl & Kern (2026), restam quatro frentes promissoras:
1. **Ativar PMD 7.1.0 para alvos Java no `repo_translation`:** no artigo base, o PMD rodava dentro do container Docker; instalá-lo no host/container permitirá medir também a evolução de code smells em **Python → Java**.
2. **Avaliar `backtranslation` (RQ3) e `prompt selection` estatístico (RQ1)** em nível de classe/repositório — verificando se a tradução circular também reduz smells em arquiteturas multi-arquivo.
3. **Explorar `k > 1` (não-determinismo) e colaboração multi-LLM** em classes/repositórios (no nosso recorte de 10 projetos J→P, `gemini` e `gpt-4.1-mini` acertaram exatamente os mesmos 7 projetos; testar amostras maiores e modelos *frontier* revelará o potencial real de complementaridade).
4. **Mitigar o gargalo de `testCompile` em Python → Java**, fornecendo contratos/interfaces públicas (ou `public_tests` mantendo `original_tests` privados) e ampliando o orçamento de correção para sistemas de tipos estáticos.
