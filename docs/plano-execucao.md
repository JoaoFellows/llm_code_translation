# Plano de execução

Documento para um chat novo que só tem este repositório. Leia este arquivo inteiro antes de editar. O desenho do corte de classes está em `docs/class-translation.md`.

Há três frentes. Duas podem ser escritas ao mesmo tempo, em branches e diretórios diferentes. A terceira espera a primeira.

## Estado do git

Conferir com `git status`, `git branch -vv` e `git log --oneline`. Na escrita deste plano:

- `main` está em `178db07` e acompanha `upstream/main` (`codetranslation/llm_code_translation`).
- `TAES/class-translation` acompanha `origin/TAES/class-translation` (`JoaoFellows/llm_code_translation`) e contém o corte Java para Python, dois commits à frente de `main`.
- `docs/class-translation.md`, `docs/superpowers/plans/2026-11-15-class-translation.md` e `docs/superpowers/specs/2026-11-15-class-translation-design.md` estavam fora do git. Se ainda estiverem untracked, o primeiro commit é só desses três arquivos, em `TAES/class-translation`, antes de criar `TAES/python-to-java`.
- `.env` está no `.gitignore`. Não commitar chave.

`class_translation/` não importa `main.py`, `config.py` nem `run_translation.py`. O pipeline antigo não importa `class_translation/`. Manter essa separação.

## Branches

| Branch | Sai de | Recebe o merge | Quando criar |
|---|---|---|---|
| `TAES/class-translation` | `main` | branch de integração do corte de classes | já existe |
| `TAES/python-to-java` | `TAES/class-translation` | `TAES/class-translation` | agora, depois do commit de `docs/` |
| `TAES/paper-models` | `main` (`178db07`) | `main` do fork | agora, só para a auditoria |
| `TAES/repo-translation` | `TAES/class-translation` depois da volta mergeada | `TAES/class-translation` | só quando JUnit e PMD existirem |

Não criar `TAES/paper-models` a partir de `TAES/class-translation`. O diff misturaria as 94 classes com a troca de modelo do paper. Não criar `TAES/repo-translation` agora: ela edita `testing.py`, `smells.py` e `state.py`, os mesmos arquivos da volta.

## Agentes em paralelo

Dois agentes ao mesmo tempo, mais um terceiro só depois. Quem dispara é uma pessoa, num único terminal, antes de abrir os chats. Os agentes não criam a branch um do outro e não fazem o commit inicial de `docs/`.

### Preparo, uma vez só

Na pasta `C:\llm_code_translation`, branch `TAES/class-translation`:

```powershell
git add docs/class-translation.md docs/plano-execucao.md docs/superpowers/plans/2026-11-15-class-translation.md docs/superpowers/specs/2026-11-15-class-translation-design.md
git commit -m "docs: record class-translation design and the execution plan"
git branch TAES/python-to-java
git branch TAES/paper-models main
git worktree add C:\llm_code_translation-py2java TAES/python-to-java
git worktree add C:\llm_code_translation-paper TAES/paper-models
```

`TAES/paper-models` sai de `main` e não contém este arquivo. O chat dessa frente recebe o escopo na mensagem colada abaixo. Não copiar o plano para essa branch.

### Dois chats

Abrir duas janelas do Cursor. Em cada uma, File, Open Folder, na pasta do worktree. Um Agent chat novo em cada janela. Colar a mensagem correspondente e enviar as duas. Não continuar neste chat.

Agente A, pasta `C:\llm_code_translation-py2java`:

```text
Leia docs/plano-execucao.md e execute só a frente 1, na branch TAES/python-to-java, neste worktree. Não crie outra branch. Não edite o pipeline original nem docs/plano-execucao.md. Não rode a bateria das 94 classes. Commit por etapa, com pytest class_translation verde.
```

Agente B, pasta `C:\llm_code_translation-paper`:

```text
Você está em C:\llm_code_translation-paper, branch TAES/paper-models, saída de main. Não há docs/plano-execucao.md aqui. Execute só a auditoria da frente 2: confira base_path_data, base_path_testing_docker, tco_path, os quatro datasets e a imagem Docker testing:t6. Não edite class_translation/. Não troque a lista LLMs. Não chame API de modelo. Não crie outra branch. Escreva o que está no disco e o que falta. Pare se um dataset ou a imagem não existir.
```

### O que pode ocorrer junto

Os dois agentes editam árvores diferentes e podem commitar ao mesmo tempo. O agente A só em `class_translation/` e no README desse pacote. O agente B só em `config.py`, `prepare_dataset.py`, `run_translation.py`, `datastructures/` e num `docs/paper-datasets.md` criado nesta branch, e somente se a auditoria precisar registrar um caminho. Nenhum dos dois dá merge, push, nem mexe em `.env`.

Não rodam juntos: a classe real `AvgPartition` na volta e qualquer chamada de API do paper. A auditoria do agente B não usa API. A fumaça de um modelo novo só começa depois que o agente A tiver terminado a chamada de `AvgPartition`, ou numa chave diferente.

### Terceiro agente

Não abrir enquanto o agente A não tiver mergeado `TAES/python-to-java` em `TAES/class-translation`. Aí sim, a partir dessa branch atualizada:

```powershell
git branch TAES/repo-translation TAES/class-translation
git worktree add C:\llm_code_translation-repo TAES/repo-translation
```

Agente C, pasta `C:\llm_code_translation-repo`:

```text
Leia docs/plano-execucao.md e execute só a frente 3, na branch TAES/repo-translation. A frente 1 já está mergeada. Não altere o pipeline original nem a lista de modelos do paper. Não edite docs/plano-execucao.md.
```

## Frente 1 — `TAES/python-to-java`

Objetivo: os mesmos dois grafos passam a aceitar `source_lang=python` e `target_lang=java`. A fonte é a solução Python do ClassEval-T. O oráculo é o JUnit. O linter é o PMD. A direção Java para Python continua funcionando, inclusive `class_translation/results/classeval_gemini.jsonl`.

Não implementar repositórios. Não alterar `main.py`, `config.py`, `run_translation.py`, `prepare_dataset.py`, `test_suit.py`, `run_code_smell_detection.py` nem `datastructures/`.

### O que já existe

`run_task` em `class_translation/pipeline.py` traduz a classe, conta smells, chama `correct` (até 3 voltas) e, se todos os testes passam, chama `reduce_smells` (até 3 voltas). Se a correção termina com falha, o grafo de smells não roda.

Travas atuais, todas presas a Python:

- `ensure_java_to_python` em `class_translation/state.py` levanta `NotImplementedError` para qualquer outro par. `test_reverse_direction_is_representable_and_refused` em `class_translation/tests/test_state.py` afirma essa recusa. Esse teste muda quando a volta existir.
- `extract_python` em `class_translation/extract.py` só reconhece cerca `python`.
- `translation_messages`, `repair_messages` e `smell_messages` em `class_translation/prompts.py` pedem "Print only the Python class" e citam Pylint.
- `run_unittest` em `class_translation/testing.py` grava o código, copia o oráculo para `test_counter.py` e roda `unittest` em subprocesso, timeout 30s. O relatório é `passed`, `total`, `feedback`.
- `count_smells` em `class_translation/smells.py` chama `python -m pylint --output-format=json`.
- `correct` e `reduce_smells` chamam `extract_python`, `run_unittest` e `count_smells` direto.
- `load_classeval_task` em `class_translation/classeval.py` lê só Java como fonte e Python como oráculo. O diretório Java do benchmark se chama `solutuon` (grafia do dataset).

### Layout do ClassEval-T

`CLASSEVAL_T_PATH` no `.env` da raiz. Se vazio, os runners usam `C:\ClassEval-T`. Para a classe `AvgPartition`:

```text
ClassEval_T/java/solutuon/AvgPartition.java      fonte da ida, pacote org.example
ClassEval_T/java/test/AvgPartitionTest.java      oráculo da volta, pacote org.example
ClassEval_T/py/solution/AvgPartition.py          fonte da volta
ClassEval_T/py/test/AvgPartition.py              oráculo da ida
```

O teste Java usa JUnit 4 (`org.junit.Test`) e JUnit Jupiter (`org.junit.jupiter.api.Test`) no mesmo arquivo. A classe traduzida precisa estar em `package org.example`, senão não compila com o teste. As versões de dependência estão em `ClassEval-T/BatchTestTool/java/java automated tester/pom.xml`: JUnit 4.13.1 e JUnit Jupiter 5.8.1. O clone não guarda os `.jar` dentro de `ClassEval_T/`. O runner precisa de um classpath real (Maven desse `pom.xml`, ou jars já resolvidos). Se `javac` ou esse classpath não existirem, parar e dizer o que falta. Não simular teste verde.

O PMD do paper é o 7.1.0, comando de referência em `datastructures/Codesample.py`:

```text
pmd check -d <arquivo.java> -R rulesets/java/quickstart.xml -f json
```

No paper isso roda dentro do Docker, em `/root/pmd-bin-7.1.0/bin/pmd`. Nesta frente o PMD é local, no mesmo papel do `python -m pylint`: subprocesso, timeout 60s, contagem de violações. Se o binário não estiver no `PATH`, parar.

### Contratos que não mudam

- `ClassTask` e `TaskRecord` em `state.py` permanecem. `TaskRecord.to_dict()` continua o formato do jsonl.
- `MAX_CORRECTION_ITERATIONS` e `MAX_SMELL_ITERATIONS` continuam 3.
- O grafo de smells só aceita o refactor se os testes do destino passam e a contagem de smells cai. Senão restaura o último código que passava.
- O modelo traduz só a classe. Os testes de origem entram no prompt como especificação e não são traduzidos.
- `pytest class_translation` segue sem rede, com `ScriptedChatClient`.

### Dispatch por `target_lang`

Não duplicar `build_correction_graph` nem `build_smell_graph`. Introduzir um ponto único de teste e um ponto único de smell, escolhidos por `task.target_lang`:

- teste: `run_unittest` para `python`; runner JUnit para `java`. Os dois devolvem o mesmo `TestReport` (`passed`, `total`, `feedback`, `ok`).
- smell: Pylint para `python`; PMD para `java`. Os dois devolvem o mesmo `SmellReport` (`count`, `feedback`).
- extração: a cerca segue `target_lang` (`python` ou `java`). Sem cerca, o texto inteiro continua valendo, como hoje.

`pipeline.py`, `correction.py` e `smell_graph.py` passam a chamar esses pontos. `ensure_java_to_python` passa a aceitar `("java", "python")` e `("python", "java")`. Qualquer outro par continua `NotImplementedError`.

### Ordem dos commits

Um commit por etapa. `pytest class_translation` verde antes do próximo.

1. Direção. Aceitar `python` para `java` em `state.py`. Reescrever `test_reverse_direction_is_representable_and_refused`: o par agora é aceito; um par desconhecido (por exemplo `rust` para `go`) ainda levanta `NotImplementedError`.
2. Prompt e extrator. `prompts.py` e `extract.py` usam `target_lang`. A ida Java para Python continua extraindo Python. Atualizar `test_translate.py`.
3. JUnit. Runner com `javac` e o classpath do JUnit, timeout 30s, mesmo `TestReport`. Teste local com um `.java` mínimo que passa e um que falha, sem API e sem ClassEval-T.
4. PMD. Contagem no formato de `SmellReport`. Teste local com um Java limpo e um com smell, se o binário existir. Se não existir, o teste pula de forma explícita e a etapa não é dada como pronta.
5. Loader. `load_classeval_task` ganha a direção. Ida: fonte `java/solutuon/<id>.java`, especificação `java/test/<id>Test.java`, oráculo `py/test/<id>.py`, com o `from <id> import <id>` que já é inserido quando falta. Volta: fonte `py/solution/<id>.py`, especificação `py/test/<id>.py`, oráculo `java/test/<id>Test.java`.
6. Fixture `class_translation/fixtures/box` (ou nome equivalente), espelhando `fixtures/counter`, com `source_lang=python` e `target_lang=java`. Testes sem API para tradução, correção e rollback de smells nessa direção. Os testes da ida continuam verdes.
7. Runner `python -m class_translation.run_classeval_java`, saída em `class_translation/results/classeval_gemini_py2java.jsonl`. Não abrir `classeval_gemini.jsonl` para escrita. Mesma regra de retomar: pular `task_id` já gravado.

Código e testes novos em inglês. Atualizar `class_translation/README.md` em português com o comando novo e as dependências de JDK, classpath JUnit e PMD.

### Pronto quando

- `pytest class_translation` passa.
- Uma classe real, `AvgPartition`, roda na volta e gera uma linha no jsonl novo.
- A linha tem `provider`, `task_id`, `status`, testes e as três contagens de smells.
- O jsonl da ida não muda.

Merge em `TAES/class-translation` só nesse estado. A bateria das 94 classes vem depois do merge, e não junto com a bateria do paper.

## Frente 2 — `TAES/paper-models`

Objetivo: repetir o experimento do paper com modelos atuais. CodeNet, Avatar, EvalPlus e EvoEval. Teste stdin/stdout na imagem Docker `testing:t6`. Smells com Pylint, PMD, Scalastyle e Clippy. Três tentativas. O mesmo reparo. O corte de classes não entra nessa tabela.

Não editar `class_translation/`. Não importar `class_translation`. Não trocar a lista `LLMs` antes da auditoria.

### Auditoria, primeiro commit

`config.py` deixa `base_path_data`, `base_path_testing_docker` e `tco_path` vazios. `prepare_dataset.py` espera, para cada dataset em `config["steps"]["prepare_datasets"]`:

- `translation_data_<dataset>.csv` dentro de `<base_path_data>/<dataset>/`
- fontes em `data/`
- casos em `test_cases/`

Avatar ainda separa AtCoder e Codeforces nesse layout. Confirmar no disco, não pelo código.

Entregável da auditoria, escrito no PR ou num `docs/paper-datasets.md` desta branch:

- o caminho real de cada um dos quatro datasets, ou a ausência
- se um problema de cada um carrega com `prepare_dataset.load_to_cache`
- se a imagem `testing:t6` existe (`docker image inspect testing:t6`)
- se um teste de uma submissão original chega a rodar

Se um item faltar, parar nessa frente. Não inventar amostra nem apontar `base_path_data` para um diretório parcial.

### Modelos, só depois da auditoria

A lista atual em `config.py` fica intacta: DeepSeek-Coder 33B, Mixtral 8x7B, Granite 34B Code, Magicoder 6.7B, CodeLlama 70B, Llama 3 8B, Llama 3 70B, Codestral 22B. A lista nova entra ao lado, sem apagar a antiga.

`run_translation.run_translations` manda o modelo para `GPTOpenAI` quando o nome contém `openai_`, e para `HFLLM` (vLLM) nos demais. `GPTOpenAI` constrói `OpenAI()` sem `base_url`, então Gemini, DeepSeek e Ollama não passam por ele. Modelos locais continuam no vLLM. Modelos de API ganham `base_url` nesse cliente, ou um cliente compatível novo dentro de `datastructures/LLM.py`. Não reutilizar `class_translation/providers.py` enquanto as branches estiverem separadas.

Fumaça antes da matriz: um dataset, um par de linguagens, um modelo, poucas tarefas em `config["steps"]["specific_tasks"]`. O protocolo (número de traduções, teto de reparo, métricas) não muda no mesmo commit que troca o modelo.

## Frente 3 — `TAES/repo-translation`

Não criar a branch e não escrever código até a frente 1 estar mergeada em `TAES/class-translation`. O executor de Java (JUnit e PMD) precisa existir no mesmo contrato de `TestReport` e `SmellReport`.

Até lá, o único trabalho é escolher o benchmark e anotar a escolha em `docs/`, sem código. ClassEval-T não serve: a unidade deixa de ser um `source_code` único. O desenho já está em `docs/class-translation.md`, seção "Repositórios": traduzir arquivo a arquivo em ordem de dependência, passar as assinaturas já traduzidas, e rodar os mesmos dois grafos com o build do projeto (`pytest` ou `mvn test`) como oráculo.

## O que não fazer

- Não desenvolver as duas frentes no mesmo worktree.
- Não rodar a bateria de API da volta e a do paper ao mesmo tempo.
- Não alterar `classeval_gemini.jsonl`.
- Não apagar os ids de modelo do paper.
- Não mudar o número de tentativas do paper no commit que troca o modelo.
- Não começar o tradutor de repositório em cima de `run_unittest` e Pylint apenas.
