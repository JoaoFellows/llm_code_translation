# Tradução de classes: mudanças, resultados e próximos passos

Este documento descreve o corte novo em `class_translation/`. O pipeline antigo (`main.py`, `config.py`, `run_translation.py`, `prepare_dataset.py`, `test_suit.py`, `run_code_smell_detection.py`) não foi alterado.

## Mudanças

O corte traduz uma classe Java inteira para Python, repara até os testes passarem e depois reduz code smells sem quebrar esses testes.

- A unidade de trabalho é uma classe com suíte de unidade, não um programa de competição com `main` e casos stdin/stdout.
- A tradução inicial é holistic: a classe inteira numa chamada. O prompt pede corretude e poucos code smells. Os testes Java entram só como especificação. O oráculo é o `unittest` Python do benchmark.
- Dois grafos LangGraph rodam em seguida.
  - Correção: roda o `unittest`. Se falha, pede reparo e volta a testar, até 3 vezes. Para antes se todos os testes passam.
  - Smells: roda o Pylint. Aceita o refactor só se a contagem cai e os testes continuam passando. Se o teste quebra, ou a contagem não cai, restaura o último snapshot que passava e tenta de novo, até 3 vezes.
- Se a correção termina com algum teste falhando, o grafo de smells não roda.
- O estado guarda `source_lang` e `target_lang`. A direção Python para Java cabe nesse estado e ainda não é executada.
- O cliente de chat é compatível com a API da OpenAI. Os presets leem a chave de `.env`: OpenAI, OpenRouter, DeepSeek, Gemini e Ollama. O arquivo `.env` está no `.gitignore`.
- Há um cliente falso, sem rede, usado pelo `pytest`. Os 15 testes em `class_translation/tests/` cobrem a tradução, o loop de correção, o rollback do grafo de smells e o registro da tarefa.
- O loader `class_translation/classeval.py` lê uma tarefa do [ClassEval-T](https://github.com/wLinHoo/ClassEval-T) (clone em `CLASSEVAL_T_PATH`) e monta o mesmo `ClassTask` do fixture local. Os comandos são `python -m class_translation.run_classeval` e `python -m class_translation.run_classeval_batch`.

### Rodada no ClassEval-T

Uma classe, `AvgPartition`, foi o primeiro teste com API. A conta da OpenAI está sem crédito (`credit_balance_exhausted`). A rodada completa usou o Gemini `gemini-3.5-flash-lite`. O preset antigo `gemini-2.0-flash` não existe mais para essa chave.

Das 94 classes, 55 passaram em todos os testes (58,5%) e 39 ficaram com alguma falha depois das três voltas de correção. Nas que passaram, a média de smells foi 12,2 depois da tradução, 13,4 depois da correção e 5,6 depois do grafo de smells. A correção usou cerca de uma volta. O grafo de smells usou as três.

Seis classes não passaram em teste nenhum: `BookManagementDB`, `CSVProcessor`, `CamelCaseMap`, `ExcelProcessor`, `Thermostat` e `UserLoginDB`. Várias dependem de banco ou de arquivo.

O registro por classe está em `class_translation/results/classeval_gemini.jsonl`.

## Próximos passos

### Python para Java

Mesmos dois grafos, no nível de classe. O que troca é o executor da linguagem de destino:

- o prompt pede Java
- o oráculo passa a ser o JUnit do ClassEval-T, com `javac`
- a contagem de smells passa a ser o PMD, no mesmo papel do Pylint

O modelo continua traduzindo só a classe. A suíte Java do benchmark julga a tradução. Isso vem antes de repositório, porque a forma dos grafos permanece e só o comando de teste e o linter mudam.

### Repositórios

A unidade deixa de ser um `source_code` único. Um repositório é uma árvore, com imports entre arquivos e um comando de build (`pytest` ou `mvn test`).

A ordem se mantém: traduzir, corrigir com o teste do projeto até três voltas, reduzir smells até três voltas sem quebrar esse teste. A tradução deixa de ser uma chamada só. Os arquivos entram por ordem de dependência, e cada chamada recebe as assinaturas já traduzidas. Os grafos rodam no projeto inteiro, quando o build é o oráculo.

O dataset também muda. ClassEval-T é classe. Repositório pede um benchmark dessa escala, num plano separado.

### Ordem

1. Python para Java nas classes do ClassEval-T.
2. Repositório, reusando os dois grafos em cima de um diretório.
3. Quando houver crédito na OpenAI, ou outro provedor, repetir uma amostra das 94 classes para comparar modelos. O registro já tem o formato dessa comparação.

## O experimento original com modelos atuais

O repositório original mede corretude funcional e code smells na tradução de um arquivo por problema, nos datasets CodeNet, Avatar, EvalPlus e EvoEval. O teste é stdin/stdout em Docker. Os smells são Pylint, PMD, Scalastyle e Clippy. O reparo iterativo e a backtranslation escolhem a melhor amostra pela fração de testes e, em empate, pela quantidade de smells.

Os modelos gravados em `config.py` são de 2023 e início de 2024: DeepSeek-Coder 33B, Mixtral 8x7B, Granite 34B Code, Magicoder 6.7B, CodeLlama 70B, Llama 3 8B e 70B, Codestral 22B. Eles rodam por vLLM local, ou pela API antiga da OpenAI quando o nome começa com `openai_`.

Esta seção é repetir esse experimento, não substituí-lo pelo corte de classes. Dataset, harness, linters e métricas ficam os mesmos, para o número ser comparável ao paper. O que muda é o modelo.

Passos:

1. Manter `prepare_datasets` em CodeNet, Avatar, EvalPlus e EvoEval, com os dados no `base_path_data` que o `config.py` já espera.
2. Trocar a lista `LLMs` por modelos atuais de código, acessíveis por API ou por um endpoint compatível com a API da OpenAI. Candidatos do mesmo tipo dos presets já usados no corte novo: um modelo forte de código da OpenAI, DeepSeek atual, Gemini atual e um modelo local via Ollama. O nome exato entra na configuração no momento da rodada, porque a lista de modelos muda.
3. Rodar a tradução, o teste em Docker e a detecção de smells pelos mesmos passos do `main.py`. O reparo iterativo continua com o teto já existente de iterações do paper, para a comparação não misturar protocolo novo com modelo novo.
4. Publicar a mesma leitura do paper: fração de testes que passam, contagem de smells e o efeito do reparo. Uma tabela por dataset e por par de linguagens (Java, Python, Scala, Rust), ao lado dos números dos modelos antigos.

O corte de classes não entra nessa tabela. Ele responde outra pergunta: classe com teste de unidade, dois grafos e modelos de API. O experimento original responde se modelos atuais melhoram a tradução de problema estilo competição que o paper já mediu.
