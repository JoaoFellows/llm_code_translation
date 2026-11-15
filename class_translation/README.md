# Tradução de classes

Traduz uma classe Java para Python, repara até os testes passarem e depois reduz code smells sem quebrar esses testes. Os comandos abaixo rodam na raiz do repositório.

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
ClassEval_T/py/test/<Classe>.py
```

`CLASS_TRANSLATION_PROVIDER` ainda não é lido. Cada runner escolhe o preset sozinho.

## Testes locais, sem API

```powershell
pip install pytest
pytest class_translation
```

Usa um cliente falso e o fixture `class_translation/fixtures/counter`. Não precisa de chave nem do ClassEval-T.

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
