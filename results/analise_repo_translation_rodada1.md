# Análise dos Resultados — Tradução de Repositórios (RepoTransBench — Rodada 1)

## 1. Contexto e Configuração Experimental

Esta avaliação mediu o desempenho do pipeline `repo_translation` sobre um subconjunto balanceado do benchmark **RepoTransBench**, focado exclusivamente nos pares **Java → Python** e **Python → Java**.

- **Modelo avaliado:** Google Gemini (`gemini-3.5-flash-lite`) via endpoint compatível com OpenAI (`temperature=0`, retry exponencial para `429 RateLimitError` e respostas vazias).
- **Amostra:** **20 repositórios** no total (**10 Java → Python** e **10 Python → Java**), ordenados por menor quantidade de arquivos-fonte (`--sort-by-size --max-source-files 10`, ignorando projetos com 0 arquivos-fonte).
- **Ambiente de execução dos testes:** Container Docker isolado sem rede (`--network none`), imagem `repotransbench-pyjava:latest` (baseada em `testing:t6` / Ubuntu 22.04, Python 3.10 + `pytest`, OpenJDK 11 + Maven com cache offline `.m2` contendo `junit-jupiter:5.9.3`, `junit:4.13.2`, `mockito:5.5.0`, `gson:2.10.1` e `jackson-databind:2.15.2`).
- **Configuração do pipeline:**
  - Até **3 iterações de correção funcional** (`--max-corrections 3`) guiadas pela saída de `bash run_tests.sh`.
  - Até **3 iterações de redução de code smells** (`--max-smell-iterations 3`) para projetos que passam nos testes: Pylint para alvos Python; PMD 7.1.0 desativado para alvos Java por ausência do binário no host.
  - Restrição de integridade: os arquivos de teste do benchmark (`tests/`, `public_tests/`, `original_tests/`, `run_tests.sh`) nunca são modificados pelo modelo.
- **Dados brutos consolidados:**
  - `results/repo_translation_summary_rodada1.csv`
  - `results/repo_translation_summary_rodada1.jsonl`

---

## 2. Resumo Quantitativo Comparativo

| Métrica | Java → Python (n = 10) | Python → Java (n = 10) | Total (n = 20) |
| --- | :---: | :---: | :---: |
| **Projetos aprovados — taxa bruta (`exit 0`)** | **6 / 10 (60,0%)** | **2 / 10 (20,0%)** | **8 / 20 (40,0%)** |
| **Projetos aprovados — taxa ajustada (`tests > 0`)** | **6 / 10 (60,0%)** | **1 / 10 (10,0%)** | **7 / 20 (35,0%)** |
| **Pass@1 (aprovado com 0 correções — bruto)** | 5 / 10 (50,0%) | 1 / 10 (10,0%) | 6 / 20 (30,0%) |
| **Pass@1 (aprovado com 0 correções — ajustado)** | **5 / 10 (50,0%)** | **0 / 10 (0,0%)** | **5 / 20 (25,0%)** |
| **Projetos resgatados pelo loop de correção** | +1 (`corbt_react-native-keep-awake`) | +1 (`djui_alias-tips`) | +2 (+10,0 pp) |
| **Falhas em compilação / testes (`failed`)** | 3 / 10 (30,0%) | 5 / 10 (50,0%) | 8 / 20 (40,0%) |
| **Erros de geração / parsing (`error`)** | 1 / 10 (10,0%) | 3 / 10 (30,0%) | 4 / 20 (20,0%) |
| **Testes unitários individuais aprovados** | **176 / 204 (86,3%)** | **7 / 7 (100,0% dos executados)** | **183 / 211 (86,7%)** |
| **Code smells nos projetos aprovados (Pylint)** | **52 → 18 (-65,4%)** | N/A (PMD não instalado) | — |

> **Nota sobre taxa bruta vs. ajustada:** No projeto `jmespath_jp` (Python → Java), o Maven retornou `BUILD SUCCESS` (`exit 0`), mas executou **`Tests run: 0`** porque o `@BeforeAll` da suíte de testes usa `Assumptions.assumeTrue(jpExists())`, exigindo o binário externo `./jp`. Embora tecnicamente o código tenha compilado sem erros, nenhum caso de teste funcional foi efetivamente validado — configurando um falso-positivo na métrica baseada apenas em código de saída `0`.

---

## 3. Resultados Detalhados — Java → Python (10 projetos)

| # | Projeto | Status | Pass@1 | Iter. Correção | Iter. Smell | Testes (`pytest`) | Smells (Inic. → Pós-Corr. → Final) | Categoria / Diagnóstico |
| :-: | --- | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| 1 | `JakeWharton_picasso2-okhttp3-downloader` | **PASSED** | Sim | 0 | 2 | 26 / 26 (100%) | `7 → 7 → 0` | Aprovado de 1ª; smells zerados |
| 2 | `aegis1980_WifiHotSpot` | **PASSED** | Sim | 0 | 3 | 22 / 22 (100%) | `17 → 17 → 0` | Aprovado de 1ª; smells zerados |
| 3 | `code-not-found_spring-kafka` | **PASSED** | Sim | 0 | 1 | 20 / 20 (100%) | `5 → 5 → 0` | Aprovado de 1ª; smells zerados |
| 4 | `chiteroman_BootloaderSpoofer` | **PASSED** | Sim | 0 | 3 | 8 / 8 (100%) | `7 → 7 → 7` | Aprovado de 1ª; refatorações revertidas ou sem redução líquida |
| 5 | `alexjlockwood_adp-path-morph-play-to-pause` | **PASSED** | Sim | 0 | 0 | 6 / 6 (100%) | `8 → 8 → 8` | Aprovado de 1ª; erro de JSON no loop de smells encerrado com preservação |
| 6 | `corbt_react-native-keep-awake` | **PASSED** | Não | 1 | 2 | 16 / 16 (100%) | `8 → 14 → 3` | Resgatado na 1ª iteração de correção; smells reduzidos de `14 → 3` |
| 7 | `agarciadom_xeger` | FAILED | Não | 3 | 0 | 31 / 40 (77,5%) | `75 → 71 → 71` | Falha lógica em random walk com comprimento limitado (`FailedRandomWalkException`) |
| 8 | `andydevacc_MentionEditText` | FAILED | Não | 3 | 0 | 28 / 43 (65,1%) | `38 → 40 → 40` | Divergências comportamentais na manipulação de texto/menções |
| 9 | `aventrix_jnanoid` | FAILED | Não | 3 | 0 | 19 / 23 (82,6%) | `7 → 13 → 13` | Divergência em validação/exceções (`ValueError: random cannot be null.`) |
| 10 | `c0ny1_chunked-coding-converter` | ERROR | Não | — | — | 0 / 0 | — | `JSONDecodeError: Expecting ',' delimiter` na geração inicial |

### Análise de Java → Python
- **Alta taxa de acerto funcional em nível de caso de teste:** Nos 9 projetos que executaram `pytest`, **176 de 204 testes unitários passaram (86,3%)**. Mesmo nos 3 projetos com status final `failed`, a taxa média de acerto por teste unitário foi de **73,6% (78/106)**, demonstrando que o mapeamento de módulos, imports (`PYTHONPATH=.` + `project_structure.txt`) e estrutura de classes funcionou consistentemente.
- **Efetividade do loop de code smells:** Nos 6 projetos aprovados, o total de avisos do Pylint caiu de **52 para 18 (-65,4%)**, com **3 projetos chegando a 0 smells** sem qualquer regressão funcional (o mecanismo de rollback garantiu preservação de 100% dos testes).
- **Custo-benefício do loop de correção:** Resgatou `corbt_react-native-keep-awake` em apenas 1 iteração (elevando a taxa de aprovação de 50% para 60%). Nos 3 projetos que permaneceram `failed`, todas as 3 iterações foram consumidas sem convergir totalmente para os casos de borda restantes.

---

## 4. Resultados Detalhados — Python → Java (10 projetos)

| # | Projeto | Status | Pass@1 | Iter. Correção | Testes (JUnit 5) | Categoria / Diagnóstico |
| :-: | --- | :---: | :---: | :---: | :---: | --- |
| 1 | `djui_alias-tips` | **PASSED** | Não | 1 | **7 / 7 (100%)** | Compilou e passou 4 testes originais + 3 públicos após 1 iteração de correção |
| 2 | `jmespath_jp` | **PASSED*** | Sim* | 0 | **0 / 0** | Falso-positivo: `main` e `test` compilaram, mas `Assumptions.assumeTrue("./jp")` pulou todos os testes |
| 3 | `Shpota_github-activity-generator` | FAILED | Não | 3 | 0 / 0 | `mvn compile` OK; Mockito resolvido offline; restou 1 erro em `testCompile` (`LocalDateTime` vs `int`) |
| 4 | `syrusakbary_aiodataloader` | FAILED | Não | 3 | 0 / 0 | `mvn compile` OK; `testCompile` falhou na inferência de generics (`DataLoader<>`) |
| 5 | `rveachkc_pymsteams` | FAILED | Não | 3 | 0 / 0 | `mvn compile` OK; `testCompile` falhou em tipo (`List<T>` vs `String`) |
| 6 | `stjordanis_betterprompt` | FAILED | Não | 3 | 0 / 0 | `mvn compile` OK; `testCompile` falhou em assinatura (`DummyCompletion` vs `Class<?>`) |
| 7 | `angeloc_s3-pit-restore` | FAILED | Não | 0 | 0 / 0 | Bug nos testes originais do benchmark (`FileWriter` usado sem `import` em `src/test/...`) |
| 8 | `arthepsy_ssh-audit` | ERROR | Não | — | 0 / 0 | `JSONDecodeError: Invalid \escape` em arquivo grande (~30 KB) |
| 9 | `initstring_linkedin2username` | ERROR | Não | — | 0 / 0 | `JSONDecodeError: Expecting ':' delimiter` (~11 KB) |
| 10 | `tiangolo_meinheld-gunicorn-flask-docker` | ERROR | Não | — | 0 / 0 | Modelo não gerou arquivos `.java` (repositório contém apenas configuração Python/Docker) |

### Análise de Python → Java
- **Gargalo dominante (`testCompile` — 5/5 falhas):** Em **100% dos projetos que falharam**, o código principal traduzido (`src/main/java`) compilou sem erros (`maven-compiler-plugin:compile` bem-sucedido). As falhas ocorreram na fase `testCompile` por incompatibilidades estritas de assinatura entre a API Java gerada a partir de Python dinamicamente tipado e as assinaturas rígidas esperadas pelos testes JUnit do benchmark (tipos de parâmetros, sobrecargas e generics).
- **Impacto da correção do cache offline do Maven / Mockito:** O projeto `Shpota_github-activity-generator`, que inicialmente falhava por ausência de `org.mockito` no `pom.xml`, passou a resolver todas as dependências JUnit 5 + Mockito offline e reduziu a falha a apenas 1 incompatibilidade de tipo (`LocalDateTime` vs `int`).

---

## 5. Taxonomia das Falhas (Todos os 20 Projetos)

| Categoria | Java → Python | Python → Java | Total | % do Total |
| --- | :---: | :---: | :---: | :---: |
| Aprovado com testes reais (`passed`, `tests > 0`) | 6 | 1 | **7** | 35,0% |
| Falso-positivo (`exit 0`, `Tests run: 0`) | 0 | 1 | **1** | 5,0% |
| Falha em asserções de teste em runtime (`pytest`) | 3 | 0 | **3** | 15,0% |
| Incompatibilidade de assinatura/tipo em `testCompile` (Java) | 0 | 4 | **4** | 20,0% |
| Bug nos próprios testes do benchmark (`src/test`) | 0 | 1 | **1** | 5,0% |
| Erro de serialização JSON na resposta do LLM (`JSONDecodeError`) | 1 | 2 | **3** | 15,0% |
| Repositório sem lógica traduzível para Java (`No Java source files`) | 0 | 1 | **1** | 5,0% |

---

## 6. Recomendações de Melhoria (Próxima Rodada)

Com base nos dados acima, duas correções cirúrgicas têm alto impacto direto na confiabilidade da avaliação e na redução de erros de infraestrutura:

1. **Ativar JSON Mode (`response_format={"type": "json_object"}`) + retry de parse JSON:**
   - **Problema endereçado:** 3 dos 20 projetos (**15%**) falharam antes mesmo de rodar os testes devido a erros de escape JSON em saídas grandes (`c0ny1_chunked-coding-converter`, `arthepsy_ssh-audit`, `initstring_linkedin2username`).
   - **Ação:** Adicionar suporte opcional a `json_mode=True` em `OpenAICompatibleClient.complete` (`class_translation/providers.py`), ativá-lo nas chamadas de `repo_translation/pipeline.py` e incluir 1 retentativa automática quando ocorrer `JSONDecodeError`.
2. **Detectar e bloquear falsos-positivos de 0 testes executados em `evaluation.py`:**
   - **Problema endereçado:** `jmespath_jp` foi registrado como `passed` apesar de executar `Tests run: 0` (pulado por `Assumptions.assumeTrue`).
   - **Ação:** Em `repo_translation/evaluation.py`, quando `returncode == 0`, verificar se a saída do Maven reporta `Tests run: 0` (sem nenhum teste executado) ou se o `pytest` reporta `collected 0 items` / `no tests ran`, tratando esses casos como `passed=False` com diagnóstico explícito no feedback.
