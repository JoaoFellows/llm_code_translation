# Class Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Traduzir uma classe Java para Python com um cliente falso, reparar com um grafo LangGraph até o unittest passar e reduzir smells com um segundo grafo que descarta refactor quebrado.

**Architecture:** `class_translation/` é um pacote novo. `run_task` chama a tradução holistic, o grafo de correção e o grafo de smells, e devolve um `TaskRecord`. Os grafos recebem um `ChatClient`. Os testes usam `ScriptedChatClient`. Nenhum módulo do pipeline antigo é importado ou editado.

**Tech Stack:** Python 3.10+, LangGraph, Pylint, unittest em subprocesso. Cliente OpenAI-compatível só como preset, sem chamada de rede nesta fase.

## Global Constraints

- Código novo só em `class_translation/` e nos dois Markdown de planejamento. Não alterar `main.py`, `config.py`, `run_translation.py`, `prepare_dataset.py`, `test_suit.py`, `run_code_smell_detection.py`, `utility.py`, `constants.py` nem `requirements.txt` da raiz.
- Direção executada: Java para Python. Estado com `source_lang` e `target_lang`. Outra direção levanta `NotImplementedError`.
- Tradução de uma classe por chamada. Prompt pede corretude e poucos code smells. Testes Java só como especificação. Oráculo: `unittest` Python.
- Correção: teto de 3 reparos, para quando todos os testes passam.
- Smells: teto de 3 refactors. Aceita só se a contagem cai e os testes passam. Senão restaura o snapshot anterior e tenta de novo até completar 3 voltas.
- Se a correção não deixar todos os testes verdes, o grafo de smells não roda.
- Sem download do ClassEval-T e sem chamada HTTP.
- Imports no topo do módulo.
- Sucesso: `pytest class_translation` passa.

---

### Task 1: Estado, fixture e loader

**Files:**
- Create: `class_translation/__init__.py`
- Create: `class_translation/state.py`
- Create: `class_translation/fixtures/counter/task.json`
- Create: `class_translation/fixtures/counter/Counter.java`
- Create: `class_translation/fixtures/counter/CounterTest.java`
- Create: `class_translation/fixtures/counter/oracle_counter.py`
- Test: `class_translation/tests/test_state.py`

**Interfaces:**
- Consumes: nada
- Produces: `ClassTask`, `TaskRecord`, `MAX_CORRECTION_ITERATIONS = 3`, `MAX_SMELL_ITERATIONS = 3`, `load_task(fixture_dir: Path) -> ClassTask`, `ensure_java_to_python(task: ClassTask) -> None`

- [ ] **Step 1: Write the failing test**

```python
def test_load_counter_fixture():
    task = load_task(FIXTURE)
    assert task.task_id == "counter"
    assert (task.source_lang, task.target_lang) == ("java", "python")
    assert "class Counter" in task.source_code
    assert "assertEquals" in task.source_tests
    assert "unittest" in task.oracle_tests

def test_reverse_direction_is_representable_and_refused():
    task = ClassTask("x", "python", "java", "box", "class Box {}", "tests", "oracle")
    with pytest.raises(NotImplementedError):
        ensure_java_to_python(task)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_state.py -v`
Expected: FAIL, módulos ausentes

- [ ] **Step 3: Write minimal implementation**

`ClassTask` e `TaskRecord` são dataclasses frozen. `TaskRecord.to_dict` devolve os nove campos do spec. `load_task` lê `task.json` e os três arquivos nomeados nele. `ensure_java_to_python` retorna se o par é `("java", "python")` e levanta `NotImplementedError` nos outros pares.

Fixture `counter`: `add(2)` seguido de `add(3)` resulta em 5, valor inicial 0. O oráculo importa `counter` e chama `getValue`. O arquivo do oráculo não começa com `test_`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_state.py -v`
Expected: PASS

### Task 2: Presets e cliente falso

**Files:**
- Create: `class_translation/providers.py`
- Test: `class_translation/tests/test_providers.py`

**Interfaces:**
- Consumes: nada
- Produces: `ChatClient` com `complete(messages) -> str`, `PRESETS`, `build_client(preset: str) -> ChatClient`, `ScriptedChatClient`

- [ ] **Step 1: Write the failing test**

```python
def test_presets_read_key_from_env():
    assert set(PRESETS) == {"openai", "openrouter", "deepseek", "gemini", "ollama"}
    assert PRESETS["deepseek"]["api_key_env"] == "DEEPSEEK_API_KEY"
    assert PRESETS["openai"]["base_url"].startswith("https://")

def test_build_client_requires_key_without_network(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        build_client("openai")

def test_scripted_client_returns_queued_text():
    client = ScriptedChatClient(["first", "second"])
    assert client.complete([{"role": "user", "content": "a"}]) == "first"
    assert client.complete([{"role": "user", "content": "b"}]) == "second"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_providers.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Tabela de presets exatamente como o spec. `build_client` lê `api_key_env`. Vazio e preset diferente de `ollama` levanta `RuntimeError` com o nome da variável, antes de instanciar o SDK. `ScriptedChatClient.complete` guarda as mensagens e dá `pop(0)` na fila. `OpenAICompatibleClient` existe e só é construído por `build_client` quando há chave. Nenhum teste chama `complete` nele.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_providers.py -v`
Expected: PASS

### Task 3: Extração de código e tradução inicial

**Files:**
- Create: `class_translation/extract.py`
- Create: `class_translation/prompts.py`
- Create: `class_translation/translate.py`
- Test: `class_translation/tests/test_translate.py`

**Interfaces:**
- Consumes: `ClassTask`, `ChatClient`, `ensure_java_to_python`
- Produces: `extract_python(text: str) -> str`, `translation_messages(task) -> list[dict]`, `translate_class(task, client) -> str`

- [ ] **Step 1: Write the failing test**

```python
def test_extract_python_prefers_fenced_block():
    text = "nota\n```python\nclass Counter:\n    pass\n```\nfim"
    assert extract_python(text).startswith("class Counter:")

def test_translate_sends_java_spec_and_returns_code():
    task = load_task(FIXTURE)
    client = ScriptedChatClient(["```python\nclass Counter:\n    pass\n```"])
    code = translate_class(task, client)
    prompt = client.prompts[0][-1]["content"]
    assert "class Counter" in prompt and "assertEquals" in prompt
    assert "code smell" in prompt.lower() or "code smells" in prompt.lower()
    assert code.startswith("class Counter:")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_translate.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`extract_python` usa a primeira cerca ` ```python ` ou ` ``` `. Sem cerca, devolve o texto removendo espaços das pontas e garante `\n` final.

`translation_messages` tem system pedindo corretude funcional e poucos code smells, e user com a classe Java e os testes Java. `translate_class` chama `ensure_java_to_python`, completa o chat e extrai o Python.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_translate.py -v`
Expected: PASS

### Task 4: Runner de unittest

**Files:**
- Create: `class_translation/testing.py`
- Test: `class_translation/tests/test_testing.py`
- Create: `class_translation/tests/samples.py`

**Interfaces:**
- Consumes: código Python e o oráculo do fixture
- Produces: `TestReport(passed, total, feedback)` e `run_unittest(code, oracle_tests, module_name) -> TestReport`. `samples.BUGGY`, `samples.SMELLY`, `samples.CLEAN`, `samples.BROKEN`

- [ ] **Step 1: Write the failing test**

```python
def test_clean_code_passes_oracle():
    task = load_task(FIXTURE)
    report = run_unittest(CLEAN, task.oracle_tests, task.module_name)
    assert report.passed == report.total == 2

def test_buggy_code_fails_oracle():
    task = load_task(FIXTURE)
    report = run_unittest(BUGGY, task.oracle_tests, task.module_name)
    assert report.total == 2 and report.passed < report.total
    assert report.feedback
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_testing.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Subprocesso com `sys.executable` num diretório temporário. Grava `{module_name}.py`, `test_counter.py` e um runner que imprime `CLASS_TRANSLATION_RESULT ` mais JSON. Timeout de 30s produz `TestReport(0, 0, ...)`.

Amostras: `BUGGY` faz `self.value = amount`. `SMELLY` incrementa e tem `unused = amount`. `CLEAN` incrementa sem variável morta. `BROKEN` faz `self.value = 0` dentro de `add`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_testing.py -v`
Expected: PASS

### Task 5: Contagem de smells

**Files:**
- Create: `class_translation/smells.py`
- Create: `class_translation/requirements.txt`
- Test: `class_translation/tests/test_smells.py`

**Interfaces:**
- Consumes: código Python
- Produces: `SmellReport(count, feedback)`, `count_smells(code, module_name) -> SmellReport`

- [ ] **Step 1: Write the failing test**

```python
def test_unused_variable_increases_smell_count():
    smelly = count_smells(SMELLY, "counter")
    clean = count_smells(CLEAN, "counter")
    assert smelly.count > clean.count
    assert "unused-variable" in smelly.feedback
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_smells.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`python -m pylint {module}.py --output-format=json --score=n` no diretório temporário. Contagem = `len(messages)`. Feedback = uma linha `symbol: message` por item. JSON inválido vira contagem 1 e o texto bruto. `requirements.txt` lista `langgraph`, `openai` e `pylint`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_smells.py -v`
Expected: PASS

### Task 6: Grafo de correção

**Files:**
- Create: `class_translation/correction.py`
- Test: `class_translation/tests/test_correction.py`

**Interfaces:**
- Consumes: `ChatClient`, `run_unittest`, `extract_python`, `ClassTask`, teto 3
- Produces: `build_correction_graph(client)`, `correct(task, code, client) -> CorrectionResult` com `code`, `iterations`, `passed`, `total`, `status`

- [ ] **Step 1: Write the failing test**

```python
def test_repair_stops_when_tests_pass():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([CLEAN])
    result = correct(task, BUGGY, client)
    assert result.iterations == 1
    assert result.passed == result.total == 2
    assert result.status == "passed"

def test_repair_stops_at_three_failures():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BUGGY, BUGGY, BUGGY, CLEAN])
    result = correct(task, BUGGY, client)
    assert result.iterations == 3
    assert result.status == "failed"
    assert len(client.prompts) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_correction.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`StateGraph` com `run_tests` e `repair`. Aresta condicional: todos passam, ou `iterations >= 3`, encerra. Senão repara e volta a testar. O quarto item da fila do segundo teste não é consumido. O prompt de reparo contém o traceback e os testes Java, e não contém o texto `import unittest` do oráculo.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_correction.py -v`
Expected: PASS

### Task 7: Grafo de smells

**Files:**
- Create: `class_translation/smell_graph.py`
- Test: `class_translation/tests/test_smell_graph.py`

**Interfaces:**
- Consumes: `ChatClient`, `run_unittest`, `count_smells`, `extract_python`, teto 3
- Produces: `reduce_smells(task, code, client) -> SmellResult` com `code`, `iterations`, `status`

- [ ] **Step 1: Write the failing test**

```python
def test_rollback_restores_previous_code_when_tests_break():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BROKEN, BROKEN, BROKEN])
    result = reduce_smells(task, SMELLY, client)
    assert result.iterations == 3
    assert result.status == "rolled_back"
    assert len(client.prompts) == 3
    assert "unused = amount" in result.code
    report = run_unittest(result.code, task.oracle_tests, task.module_name)
    assert report.passed == report.total

def test_accepts_refactor_that_lowers_smells_and_keeps_tests():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([CLEAN])
    result = reduce_smells(task, SMELLY, client, max_iterations=1)
    assert result.iterations == 1
    assert "unused = amount" not in result.code
    assert count_smells(result.code, "counter").count < count_smells(SMELLY, "counter").count
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_smell_graph.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Nós `lint`, `refactor`, `evaluate`, `rollback`. `evaluate` aceita só com testes verdes e contagem estritamente menor que `previous_smell_count`. Rejeição vai para `rollback`, que restaura o snapshot e volta para `lint`. O lint encerra se a contagem é 0 ou se as voltas já são 3. Aceite também volta para `lint`. `reduce_smells` usa teto 3 por omissão.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation/tests/test_smell_graph.py -v`
Expected: PASS

### Task 8: Orquestração e registro

**Files:**
- Create: `class_translation/pipeline.py`
- Test: `class_translation/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `translate_class`, `correct`, `reduce_smells`, `count_smells`, `run_unittest`, `load_task`
- Produces: `run_task(task, client) -> TaskRecord`

- [ ] **Step 1: Write the failing test**

```python
def test_pipeline_record_for_scripted_counter():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BUGGY, SMELLY, CLEAN, BROKEN, BROKEN])
    record = run_task(task, client)
    assert record.task_id == "counter"
    assert record.tests_passed == record.tests_total == 2
    assert record.status == "passed"
    assert record.correction_iterations == 1
    assert record.smell_iterations == 3
    assert record.smells_after_smell_graph < record.smells_after_correction
    assert record.to_dict()["status"] == "passed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest class_translation/tests/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

`run_task` traduz, conta smells nesse snapshot, corrige, conta de novo. Com `status == "passed"`, roda `reduce_smells`. Senão reusa o código da correção, com `smell_iterations == 0`. As três contagens vêm de `count_smells` nos três snapshots. O `unittest` final define `tests_passed`, `tests_total` e `status`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest class_translation -v`
Expected: PASS em todos os testes do pacote

- [ ] **Step 5: Commit**

Não criar commit nesta fase. O commit só acontece se for pedido à parte.
