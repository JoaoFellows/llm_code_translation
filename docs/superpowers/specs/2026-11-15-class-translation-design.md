# Tradução de classes Java para Python

Data: 2026-11-15

Corte inicial de tradução de classes, separado do pipeline de problemas estilo competição. Este documento fecha as decisões. A implementação segue o plano em `docs/superpowers/plans/2026-11-15-class-translation.md`.

## Objetivo

Traduzir uma classe Java inteira para Python, reparar até os testes passarem e, em seguida, reduzir code smells sem quebrar os testes. Nesta fase o modelo é um cliente falso, sem rede e sem chave de API. O registro de uma tarefa já sai no formato que um benchmark futuro vai agregar.

## Contexto

O pipeline existente (`main.py`, `config.py`, `run_translation.py`, `prepare_dataset.py`, `test_suit.py`, `run_code_smell_detection.py`) traduz um arquivo de CodeNet, Avatar, EvalPlus ou EvoEval, executa casos stdin/stdout em Docker e mede smells. A unidade dele é um programa com `main`, não uma classe com suíte de unidade.

O código novo mora em `class_translation/` na raiz. Os módulos existentes permanecem intocados. Nenhum import cruza do pacote novo para o pacote antigo.

## Decisões

- Escopo deste corte: classes, direção Java para Python. O estado carrega `source_lang` e `target_lang`. A direção inversa cabe nesse estado e não é executada.
- Tradução inicial holistic: a classe inteira numa chamada. O prompt pede equivalência funcional e poucos code smells.
- O modelo traduz só a classe. Os testes Java entram no prompt como especificação de comportamento. O oráculo é o `unittest` Python do fixture. Uma suíte produzida pelo modelo não decide corretude.
- Dois grafos LangGraph separados, nesta ordem, depois da tradução inicial.
  - Correção: roda o `unittest`. Em falha, pede reparo. Teto de 3 reparos. Para quando todos os testes passam.
  - Smells: roda o Pylint. Pede refactor que preserve o comportamento. Teto de 3 refactors. Aceita o snapshot só quando a contagem de smells cai e os testes continuam passando. Se o teste quebra, ou a contagem não cai, descarta o snapshot, fica com o anterior e tenta outro refactor até completar as 3 voltas.
- Se a correção termina com algum teste falhando, o grafo de smells não roda. A contagem final de smells repete a contagem pós-correção e as voltas de smell ficam em zero.
- Dataset alvo futuro: ClassEval-T (`https://github.com/wLinHoo/ClassEval-T`), estratégia holistic, oráculo nos testes Python do próprio benchmark. Nesta fase o dataset não é baixado e nenhuma API é chamada.
- Fixture mínimo, versionado, no lugar do dataset: uma classe Java, os testes Java (só especificação) e o `unittest` Python (oráculo).
- Cliente de chat único, no formato da API OpenAI. Presets que leem a chave de variável de ambiente: OpenAI, OpenRouter, DeepSeek, Gemini e Ollama. Cada preset guarda `base_url`, `model` e `api_key_env`. Os nomes de modelo são placeholders. Um cliente falso, sem rede, devolve respostas enfileiradas.
- Sucesso desta fase: `pytest class_translation` prova a tradução inicial, o loop de correção e o loop de smells com rollback, e confere um registro por tarefa. Sem chave, sem as 94 tarefas, sem tabela de benchmark.

## Fora de escopo

- Tradução Python para Java, Scala e Rust.
- Repositórios, ordem de dependência entre arquivos e build Maven/Gradle.
- Estratégias min-dependency e standalone do ClassEval-T.
- Chamada real de API, download do ClassEval-T e tabela agregada de pass rate.
- Docker, stdin/stdout e os analisadores PMD, Scalastyle e Clippy.
- Alteração de `main.py`, `config.py` e dos outros módulos do pipeline antigo.

## Arquitetura

Um orquestrador linear chama três peças que não se conhecem por dentro. Elas trocam código-fonte e relatórios.

```text
ClassTask
  -> translate_class          # uma chamada, classe inteira
  -> correction graph         # unittest até passar, ou 3 reparos
  -> smell graph              # pylint até 3 refactors, com rollback e nova tentativa
  -> TaskRecord
```

O cliente de chat entra por parâmetro. Os testes passam o cliente falso. `build_client` só existe para quando houver chave. Nenhum teste chama `build_client`.

## Estado e direção

`ClassTask` é o insumo imutável:

- `task_id`, `source_lang`, `target_lang`, `module_name`
- `source_code` (classe Java)
- `source_tests` (testes Java, especificação)
- `oracle_tests` (fonte do `unittest` Python)

`run_task` recusa qualquer par que não seja `java` → `python` com `NotImplementedError`. O tipo aceita outros pares para a direção inversa poder ser ligada depois sem redesenhar o estado.

Tetos, constantes do corte: 3 reparos de correção e 3 refactors de smell.

## Registro

Uma tarefa produz um `TaskRecord`:

| Campo | Significado |
|---|---|
| `task_id` | id do fixture |
| `tests_passed` / `tests_total` | `unittest` no código final |
| `status` | `passed` se todos passam, senão `failed` |
| `smells_after_translation` | Pylint no código da tradução inicial |
| `smells_after_correction` | Pylint no código que saiu da correção |
| `smells_after_smell_graph` | Pylint no código final |
| `correction_iterations` | reparos pedidos |
| `smell_iterations` | refactors pedidos, inclusive o descartado |

As três contagens são recalculadas pelo orquestrador em cima dos três snapshots, não copiadas da memória interna do grafo.

## Grafos

### Correção

Estado: código atual, linguagens, classe de origem, testes Java, oráculo, `module_name`, voltas, teto, `passed`, `total`, feedback, status.

```text
START -> run_tests
run_tests -> repair    se algum teste falha e voltas < 3
run_tests -> END       se todos passam, ou o teto foi atingido
repair -> run_tests
```

`repair` incrementa a volta e substitui o código pela resposta do modelo. O prompt leva a classe Java, os testes Java, o Python atual e o traceback. Não leva o arquivo do oráculo Python.

### Smells

Estado: código atual, snapshot anterior, contagens atual e anterior, feedback do Pylint, voltas, teto, oráculo, `module_name`, status.

```text
START -> lint
lint -> END         se a contagem é 0 ou as voltas atingiram 3
lint -> refactor    caso contrário
refactor -> evaluate
evaluate -> lint      se os testes passam e a contagem caiu
evaluate -> rollback  se o teste quebra ou a contagem não cai
rollback -> lint
```

`refactor` guarda o código e a contagem atuais, incrementa a volta e aplica a resposta do modelo. `rollback` restaura esse par guardado e volta para `lint`. O lint seguinte encerra quando as 3 voltas já foram usadas ou quando não há smell. O prompt de refactor leva o Python atual e as mensagens do Pylint, e pede para preservar o comportamento. Não pede testes novos.

## Cliente

`ChatClient.complete(messages) -> str`.

Presets:

| Nome | base_url | model (placeholder) | api_key_env |
|---|---|---|---|
| openai | `https://api.openai.com/v1` | `gpt-4.1-mini` | `OPENAI_API_KEY` |
| openrouter | `https://openrouter.ai/api/v1` | `openai/gpt-4.1-mini` | `OPENROUTER_API_KEY` |
| deepseek | `https://api.deepseek.com` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-3.5-flash-lite` | `GEMINI_API_KEY` |
| ollama | `http://127.0.0.1:11434/v1` | `qwen2.5-coder` | `OLLAMA_API_KEY` |

`build_client` lê a variável. Sem valor, OpenAI, OpenRouter, DeepSeek e Gemini levantam `RuntimeError` antes de qualquer requisição. Ollama, sem variável, usa a chave local `"ollama"`, porque o servidor local não exige segredo. Nesta fase nenhum teste constrói esse cliente.

`ScriptedChatClient` guarda uma fila de strings e devolve a próxima. É o cliente falso.

Respostas podem vir em cerca markdown. `extract_python` fica com o primeiro bloco e, sem cerca, com o texto inteiro.

## Ferramentas

`run_unittest` grava o código como `{module_name}.py` e o oráculo como `test_counter.py` num diretório temporário, executa um runner em subprocesso e lê uma linha JSON com `passed`, `total` e `feedback`. Timeout vira 0 testes passados e o feedback do erro.

`count_smells` roda `python -m pylint` com `--output-format=json` no mesmo tipo de diretório. A contagem é o número de mensagens. Saída que não é JSON conta como 1, com o texto bruto no feedback, para o grafo continuar.

## Fixture

`class_translation/fixtures/counter/`:

- `task.json` com id `counter`, módulo `counter`, `java` → `python`
- `Counter.java`, classe com `add` e `getValue`
- `CounterTest.java`, JUnit descrevendo `add(2)` depois `add(3)` igual a 5, e valor inicial 0
- `oracle_counter.py`, o mesmo comportamento em `unittest`

O arquivo do oráculo não se chama `test_*.py` para o pytest da raiz não coletá-lo. O runner de teste copia o conteúdo para `test_counter.py` no diretório temporário.

## Critério de pronto

`pytest class_translation` passa e o teste de pipeline confere, para o fixture `counter` e o cliente falso, um `TaskRecord` com:

- `tests_passed == tests_total == 2`
- `status == "passed"`
- `correction_iterations == 1`
- `smell_iterations == 3`
- `smells_after_smell_graph < smells_after_correction`

A fila do cliente falso é: tradução com bug de lógica, reparo correto com variável não usada, refactor que remove a variável, e dois refactors que zeram o contador e são descartados. O código final é o refactor aceito.

## Dependências

`class_translation/requirements.txt` lista `langgraph`, `openai` e `pylint`. O `requirements.txt` da raiz do pipeline antigo não muda.
