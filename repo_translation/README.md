# RepoTransBench: tradução de repositórios

Este fluxo traduz os arquivos de um projeto, executa `run_tests.sh` do projeto alvo em Docker, tenta até três correções e, para alvos Python ou Java, tenta até três reduções de code smells. Uma refatoração só é aceita se os testes continuarem passando e a contagem de smells cair. Python usa Pylint; Java usa PMD 7.1.0. Nos outros idiomas do benchmark, o resultado de smells é `null` e o loop de smells é omitido.

O [RepoTransBench](https://github.com/DeepSoftwareAnalytics/RepoTransBench) distribui os projetos no [release v1.0](https://github.com/DeepSoftwareAnalytics/RepoTransBench/releases/tag/v1.0). Descompacte `projects.tar.gz` em um diretório que contenha `source_projects/` e `target_projects/`. O programa lê `target_projects/projects_summary.jsonl` e exige os diretórios `source_projects/<origem>/<projeto>/` e `target_projects/<origem>/<destino>/<projeto>/`, incluindo `run_tests.sh`.

Instale Python 3.10+, Docker e as dependências de `class_translation/requirements.txt`. Preencha a chave do provedor em `.env` (veja `.env.example`). Você pode construir a imagem do próprio benchmark com `docker build -t repotransbench -f RepoTransBench/docker/Dockerfile RepoTransBench/docker`. A imagem informada precisa conter também as dependências requeridas pelo `run_tests.sh` do projeto escolhido. Para Java, instale o PMD no caminho descrito em `class_translation/README.md`.

Exemplo, na raiz deste repositório:

```powershell
python -m pip install -r class_translation/requirements.txt
python -m repo_translation.run --dataset-root C:\RepoTransBench-data --project NOME --source Java --target Python --provider openai --docker-image NOME_DA_IMAGEM
```

Teste local da integração, com projetos e cliente falsos: `python -m pip install pytest` e `python -m pytest repo_translation`.

Para executar vários projetos, use `python -m repo_translation.run_batch --dataset-root C:\RepoTransBench-data --provider openai --docker-image NOME_DA_IMAGEM --max-per-pair 1`. Pode filtrar com `--source` e `--target`. O lote pula projetos que já têm um `.result.json`.

O diretório de trabalho fica em `<dataset-root>/translated_projects/<provider>/<origem>/<destino>/<projeto>/`. O registro JSON fica ao lado da pasta do projeto. A ferramenta recusa sobrescrever uma tradução existente. Para repetir a execução, use outro `--output-root` dentro de `--dataset-root`.

O teste em Docker monta o dataset em `/workspace`, desativa a rede do contêiner e executa `bash run_tests.sh` no projeto traduzido. O resultado funcional usa o código de saída do script; a contagem individual de testes depende do próprio output do benchmark e não é inferida aqui. Execute apenas projetos do benchmark em um ambiente Docker preparado para eles.
