# Análise Comparativa — RepoTransBench (Rodada 1 vs. Rodada 2)

## 1. Correções Aplicadas Entre a Rodada 1 e a Rodada 2

A partir do diagnóstico documentado em `results/analise_repo_translation_rodada1.md`, duas correções foram implementadas e validadas com testes unitários (`7/7 passed`):

1. **JSON Mode nativo + retry de parse JSON (`class_translation/providers.py` e `repo_translation/pipeline.py`):**
   - Ativação de `response_format={"type": "json_object"}` nas requisições ao Gemini feitas pelo pipeline de tradução de repositórios (com fallback automático caso um provedor não suporte o parâmetro).
   - Inclusão de 1 retentativa explícita caso ainda ocorra `JSONDecodeError`.
2. **Bloqueio de falsos-positivos com 0 testes executados (`repo_translation/evaluation.py`):**
   - Quando `bash run_tests.sh` retorna código `0`, o avaliador agora inspeciona a saída do Maven (`Tests run: 0`) e do `pytest` (`collected 0 items` / `no tests ran`), classificando a execução como `failed` com o marcador `[EVAL] Marked as failed: test runner exited 0 but executed 0 tests.`

Os projetos afetados pelas correções (os 4 que haviam encerrado como `error` + `jmespath_jp`) foram reexecutados na mesma amostra de **20 projetos** (**10 Java → Python** e **10 Python → Java**).

- **Dados consolidados (Rodada 2):**
  - `results/repo_translation_summary_rodada2.csv`
  - `results/repo_translation_summary_rodada2.jsonl`

---

## 2. Comparativo Quantitativo — Rodada 1 vs. Rodada 2

### 2.1 Java → Python (n = 10)

| Métrica | Rodada 1 | Rodada 2 | Variação |
| --- | :---: | :---: | :---: |
| **Projetos aprovados (`passed`)** | 6 / 10 (60,0%) | **7 / 10 (70,0%)** | **+10,0 pp** |
| **Pass@1 (`0` correções)** | 5 / 10 (50,0%) | **6 / 10 (60,0%)** | **+10,0 pp** |
| **Falhas em testes (`failed`)** | 3 / 10 (30,0%) | 3 / 10 (30,0%) | 0 |
| **Erros de geração / JSON (`error`)** | 1 / 10 (10,0%) | **0 / 10 (0,0%)** | **-10,0 pp (zerado)** |
| **Testes unitários aprovados (`pytest`)** | 176 / 204 (86,3%) | **216 / 244 (88,5%)** | **+40 testes aprovados (+2,2 pp)** |
| **Code smells (projetos aprovados — Pylint)** | 52 → 18 (-65,4%) | **61 → 18 (-70,5%)** | **4 de 7 projetos zerados (0 smells)** |

### 2.2 Python → Java (n = 10)

| Métrica | Rodada 1 | Rodada 2 | Variação |
| --- | :---: | :---: | :---: |
| **Projetos aprovados (bruto `exit 0`)** | 2 / 10 (20,0%)* | **1 / 10 (10,0%)** | Falso-positivo (`jmespath_jp`) corrigido |
| **Projetos aprovados (reais, `tests > 0`)** | 1 / 10 (10,0%) | **1 / 10 (10,0%)** | Métrica bruta = métrica real |
| **Erros de serialização JSON (`JSONDecodeError`)** | 2 / 10 (20,0%) | **0 / 10 (0,0%)** | **-20,0 pp (zerado)** |
| **Erros totais (`error`)** | 3 / 10 (30,0%) | **1 / 10 (10,0%)** | Restou apenas repo sem lógica Java (`tiangolo`) |
| **Testes unitários executados e aprovados (JUnit 5)** | 7 / 7 | **34 / 35 (97,1%)** | **+27 testes aprovados (`arthepsy_ssh-audit`)** |

### 2.3 Total Geral (n = 20)

| Métrica | Rodada 1 | Rodada 2 |
| --- | :---: | :---: |
| **`JSONDecodeError` em toda a amostra** | **3 / 20 (15,0%)** | **0 / 20 (0,0%)** |
| **Falsos-positivos (`exit 0` com `0` testes)** | **1 / 20 (5,0%)** | **0 / 20 (0,0%)** |
| **Projetos aprovados reais (`tests > 0`)** | **7 / 20 (35,0%)** | **8 / 20 (40,0%)** |
| **Testes unitários individuais aprovados** | **183 / 211 (86,7%)** | **250 / 279 (89,6%)** |

---

## 3. Impacto Projeto a Projeto nos Casos Reexecutados

| Par | Projeto | Rodada 1 | Rodada 2 | O que mudou |
| --- | --- | :---: | :---: | --- |
| **Java → Python** | `c0ny1_chunked-coding-converter` | `ERROR` (`JSONDecodeError`) | **PASSED** (`40/40`, Pass@1, smells `9 → 0`) | JSON Mode eliminou erro de escape; passou nos 40 testes de 1ª e zerou smells em 2 iterações |
| **Python → Java** | `arthepsy_ssh-audit` | `ERROR` (`JSONDecodeError` ~30 KB) | `FAILED` (**27 / 28** testes JUnit = **96,4%**) | JSON Mode permitiu traduzir e compilar tudo (`main` + `test`); falhou em apenas 1 caso de borda (`TestSoftware.test_software_parse_invalid_input`) |
| **Python → Java** | `initstring_linkedin2username` | `ERROR` (`JSONDecodeError`) | `FAILED` (`testCompile`) | JSON Mode eliminou erro de geração; `main` compilou, falhou em `testCompile` por divergência de tipo (`assertArrayEquals` esperando `String[]`) |
| **Python → Java** | `jmespath_jp` | `PASSED*` (falso-positivo, `0` testes) | `FAILED` (`0` testes detectado) | Guard em `evaluation.py` impediu falso-positivo quando `Assumptions.assumeTrue("./jp")` pulou a suíte |
| **Python → Java** | `tiangolo_meinheld-gunicorn-flask-docker` | `ERROR` (`No Java source files`) | `ERROR` (`No Java source files`) | Confirmado como limitação do repositório (apenas scripts/config de container Python, sem classes traduzíveis) |

---

## 4. Tabela Consolidada Final (Rodada 2 — Todos os 20 Projetos)

### Java → Python
| # | Projeto | Status | Correções | Testes (`pytest`) | Smells (Inic. → Final) |
| :-: | --- | :---: | :---: | :---: | :---: |
| 1 | `JakeWharton_picasso2-okhttp3-downloader` | **PASSED** | 0 | 26 / 26 | `7 → 0` |
| 2 | `aegis1980_WifiHotSpot` | **PASSED** | 0 | 22 / 22 | `17 → 0` |
| 3 | `c0ny1_chunked-coding-converter` | **PASSED** | 0 | 40 / 40 | `9 → 0` |
| 4 | `code-not-found_spring-kafka` | **PASSED** | 0 | 20 / 20 | `5 → 0` |
| 5 | `chiteroman_BootloaderSpoofer` | **PASSED** | 0 | 8 / 8 | `7 → 7` |
| 6 | `alexjlockwood_adp-path-morph-play-to-pause` | **PASSED** | 0 | 6 / 6 | `8 → 8` |
| 7 | `corbt_react-native-keep-awake` | **PASSED** | 1 | 16 / 16 | `8 → 3` |
| 8 | `agarciadom_xeger` | FAILED | 3 | 31 / 40 | `75 → 71` |
| 9 | `andydevacc_MentionEditText` | FAILED | 3 | 28 / 43 | `38 → 40` |
| 10 | `aventrix_jnanoid` | FAILED | 3 | 19 / 23 | `7 → 13` |

### Python → Java
| # | Projeto | Status | Correções | Testes (JUnit 5) | Causa principal |
| :-: | --- | :---: | :---: | :---: | --- |
| 1 | `djui_alias-tips` | **PASSED** | 1 | 7 / 7 | Aprovado após 1 correção |
| 2 | `arthepsy_ssh-audit` | FAILED | 3 | **27 / 28** | 1 asserção falhando em runtime (`expected: not <null>`) |
| 3 | `Shpota_github-activity-generator` | FAILED | 3 | 0 / 0 | `testCompile`: tipo de parâmetro (`LocalDateTime` vs `int`) |
| 4 | `syrusakbary_aiodataloader` | FAILED | 3 | 0 / 0 | `testCompile`: inferência de generics (`DataLoader<>`) |
| 5 | `rveachkc_pymsteams` | FAILED | 3 | 0 / 0 | `testCompile`: tipo de retorno (`List<T>` vs `String`) |
| 6 | `stjordanis_betterprompt` | FAILED | 3 | 0 / 0 | `testCompile`: assinatura (`DummyCompletion` vs `Class<?>`) |
| 7 | `initstring_linkedin2username` | FAILED | 3 | 0 / 0 | `testCompile`: tipo de retorno (`String[]` em `assertArrayEquals`) |
| 8 | `angeloc_s3-pit-restore` | FAILED | 0 | 0 / 0 | Bug no teste original do benchmark (`FileWriter` sem `import`) |
| 9 | `jmespath_jp` | FAILED | 1 | 0 / 0 | `Tests run: 0` bloqueado corretamente (binário `./jp` ausente) |
| 10 | `tiangolo_meinheld-gunicorn-flask-docker` | ERROR | — | 0 / 0 | Repositório sem código traduzível para Java |

---

## 5. Conclusões

1. **Zero erros de JSON em 20 repositórios:** O JSON Mode nativo eliminou **100% dos `JSONDecodeError`** (de `3/20` para `0/20`), desbloqueando traduções grandes de até ~30 KB (`arthepsy_ssh-audit` e `c0ny1_chunked-coding-converter`).
2. **Avaliação metodologicamente limpa:** A checagem de `Tests run: 0` eliminou o falso-positivo de `jmespath_jp`, garantindo que todo projeto marcado como `passed` tenha efetivamente executado e aprovado testes reais.
3. **Desempenho sólido em Java → Python (70% de repositórios aprovados; 88,5% dos testes unitários; -70,5% de smells):** O pipeline de tradução + correção + refatoração de smells com Pylint funciona de forma altamente consistente nesse sentido.
4. **Principal barreira remanescente em Python → Java (5/10 falhas em `testCompile`):** Como o código Python não declara tipos estáticos, o modelo traduz corretamente a lógica (compilando `src/main/java` em todos os casos), mas diverge das assinaturas exatas exigidas pelos testes JUnit (arrays vs listas, generics, tipos de data). Fornecer assinaturas públicas esperadas ou aumentar o orçamento de iterações de correção para alvos estaticamente tipados é o próximo vetor mais promissor de ganho.
