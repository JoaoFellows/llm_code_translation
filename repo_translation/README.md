# RepoTransBench: tradução de repositórios

Este fluxo faz uma tradução por arquivo de origem e executa `run_tests.sh` **uma vez** para o projeto traduzido. Não faz correção iterativa nem avaliação de code smells. Registra o resultado funcional e, quando o runner informa uma contagem de testes reconhecível, a taxa de testes aprovados.

O [RepoTransBench](https://github.com/DeepSoftwareAnalytics/RepoTransBench) distribui os projetos no [release v1.0](https://github.com/DeepSoftwareAnalytics/RepoTransBench/releases/tag/v1.0). Descompacte `projects.tar.gz` em um diretório que contenha `source_projects/` e `target_projects/`. O programa lê `target_projects/projects_summary.jsonl` e exige os diretórios `source_projects/<origem>/<projeto>/` e `target_projects/<origem>/<destino>/<projeto>/`, incluindo `run_tests.sh`.

Instale Python 3.10+, Docker e `openai` (`python -m pip install openai`). Preencha a chave do provedor em `.env` (veja `.env.example`). Você pode construir a imagem do próprio benchmark com `docker build -t repotransbench -f RepoTransBench/docker/Dockerfile RepoTransBench/docker`. A imagem informada precisa conter também as dependências requeridas pelo `run_tests.sh` do projeto escolhido.

Exemplo, na raiz deste repositório:

```powershell
python -m pip install openai
python -m repo_translation.run --dataset-root C:\RepoTransBench-data --project NOME --source Java --target Python --provider openai --docker-image NOME_DA_IMAGEM
```

Teste local da integração, com projetos e cliente falsos: `python -m pip install pytest` e `python -m pytest repo_translation`.

Para executar vários projetos, use `python -m repo_translation.run_batch --dataset-root C:\RepoTransBench-data --provider openai --docker-image NOME_DA_IMAGEM --max-per-pair 1`. Pode filtrar com `--source` e `--target`. O lote pula projetos que já têm um `.result.json` e grava `summary.json` com a taxa de projetos aprovados. Quando a saída dos runners informa contagens, o resumo inclui também a taxa agregada de testes aprovados.

O diretório de trabalho fica em `<dataset-root>/translated_projects/<provider>/<origem>/<destino>/<projeto>/`. O registro JSON fica ao lado da pasta do projeto. A ferramenta recusa sobrescrever uma tradução existente. Para repetir a execução, use outro `--output-root` dentro de `--dataset-root`.

O teste em Docker monta o dataset em `/workspace`, desativa a rede do contêiner e executa `bash run_tests.sh` no projeto traduzido. A aprovação do projeto usa o código de saída do script. A taxa individual é `testes aprovados / testes executados`; casos ignorados ficam fora do denominador quando o runner os identifica. As contagens só são preenchidas quando há um resumo reconhecível de pytest, unittest, Maven, Cargo ou Jest; caso contrário, ficam `null`. Execute apenas projetos do benchmark em um ambiente Docker preparado para eles.
