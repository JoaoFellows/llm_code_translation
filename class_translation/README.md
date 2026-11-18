# Tradução de classes

Traduz uma classe entre Java e Python, repara até os testes passarem e depois reduz code smells sem quebrar esses testes. Os comandos abaixo rodam na raiz do repositório.

## Preparar

Python 3.10 ou mais novo.

```powershell
pip install -r class_translation/requirements.txt
copy .env.example .env
```

Preencha no `.env` a chave do provedor que for usar. `CLASSEVAL_T_PATH` é a raiz do clone do [ClassEval-T](https://github.com/wLinHoo/ClassEval-T). Se ficar vazio, os runners usam `C:\ClassEval-T`. O loader espera esta árvore:

```text
ClassEval_T/java/solutuon/<Classe>.java
ClassEval_T/java/test/<Classe>Test.java
ClassEval_T/py/solution/<Classe>.py
ClassEval_T/py/test/<Classe>.py
```

`CLASS_TRANSLATION_PROVIDER` ainda não é lido. Cada runner escolhe o preset sozinho.

## Testes locais, sem API

```powershell
pip install pytest
pytest class_translation
```

Usa um cliente falso e os fixtures `class_translation/fixtures/counter` (Java para Python) e `class_translation/fixtures/box` (Python para Java). Não precisa de chave nem do ClassEval-T. Os testes da volta precisam do JDK, do classpath JUnit e do PMD descritos abaixo.

## Uma classe

`run_classeval` tenta OpenAI (`gpt-4.1-mini`) e, se a conta estiver sem crédito, cai para Gemini (`gemini-3.5-flash-lite`). Preencha `OPENAI_API_KEY` e `GEMINI_API_KEY`. Sem argumento, a classe é `AvgPartition`.

```powershell
python -m class_translation.run_classeval
python -m class_translation.run_classeval AvgPartition
```

A saída é um JSON com `provider`, `task_id`, `status`, testes passados e a contagem de smells depois da tradução, da correção e do grafo de smells.

## As 94 classes

`run_classeval_batch` usa só o Gemini e grava uma linha por classe em `class_translation/results/classeval_gemini.jsonl`. Classes já presentes nesse arquivo são puladas, então o comando pode ser interrompido e retomado. Exige `GEMINI_API_KEY`.

```powershell
python -m class_translation.run_classeval_batch
```

## Python para Java

O mesmo pipeline traduz a solução Python (`ClassEval_T/py/solution`) para Java. A especificação continua sendo o teste Python. O oráculo é o JUnit em `ClassEval_T/java/test` e os smells saem do PMD. A classe traduzida precisa declarar `package org.example`. A direção Java para Python não muda, e `classeval_gemini.jsonl` não é aberto para escrita.

Além do Python, esta direção precisa de:

- JDK com `javac` no `PATH`.
- Classpath JUnit em `class_translation/tools/junit/` (a pasta `class_translation/tools/` está no `.gitignore`; os jars não entram no git):
  - `junit-4.13.1.jar`
  - `hamcrest-core-1.3.jar`, dependência do JUnit 4
  - `junit-platform-console-standalone-1.8.1.jar`, alinhado ao Jupiter 5.8.1 / platform 1.8.1, capaz de rodar `org.junit.Test` e `org.junit.jupiter.api.Test` no mesmo arquivo
- PMD 7.1.0 descompactado em `class_translation/tools/pmd-bin-7.1.0/`. A contagem chama `bin/pmd.bat` (ou `bin/pmd`) com `check -d <arquivo.java> -R rulesets/java/quickstart.xml -f json`.

Maven não é necessário. Sem o `javac`, sem esses jars ou sem o binário do PMD, a etapa correspondente não fica verde.

`run_classeval_java` grava uma linha por classe em `class_translation/results/classeval_gemini_py2java.jsonl`. Um `task_id` já presente nesse arquivo é pulado. Sem argumento, a classe é `AvgPartition`. O preset tenta OpenAI e, sem crédito, cai para o Gemini, como em `run_classeval`.

```powershell
python -m class_translation.run_classeval_java
python -m class_translation.run_classeval_java AvgPartition
```
