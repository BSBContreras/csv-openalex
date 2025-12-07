# OpenAlex CSV Data Collector - Author & Citation Based

Este projeto contém quatro métodos de coleta de dados: um baseado em autores, outro baseado em citações, um terceiro baseado em autores com limite no número de autores, e um quarto baseado em grafo de autores (BFS). Ele permite coletar registros de dados da api do openalex (`https://api.openalex.org`), salvando os resultados em checkpoints para facilitar a retomada da coleta em caso de interrupções.

## Como funciona

O projeto possui quatro scripts principais:

- **AuthorBasedCollector.py**: Coleta de dados baseada em autores (limite baseado no número de trabalhos).
- **CitationBasedCollector.py**: Coleta de dados baseada em citações.
- **AuthorLimitCollector.py**: Coleta de dados baseada em autores com limite no número de autores processados.
- **author_graph_based_collector.py**: Coleta de dados baseada em grafo de autores usando busca em largura (BFS), coletando trabalhos de autores e expandindo através de co-autores.

Durante a execução, o sistema coleta e armazena sete principais tipos de informações, que são salvas em arquivos CSV dentro de uma pasta especificada (`citations_based_database`, `author_based_database`, `author_limit_database` ou `author_graph_database`):

1. **Trabalhos**: Salvos no arquivo `openalex_works.csv`.
2. **Autores**: Salvos no arquivo `openalex_authors.csv`.
3. **Citações**: Salvas no arquivo `openalex_citations.csv`.
4. **Trabalhos relacionados**: Salvos no arquivo `openalex_related_works.csv`.
5. **Conceitos**: Salvos no arquivo `openalex_concepts.csv`.
6. **Tópicos**: Salvos no arquivo `openalex_topics.csv`.
7. **Palavras-chave**: Salvas no arquivo `openalex_keywords.csv`.

Você pode escolher qual script executar passando o método desejado pela linha de comando, juntamente com os parâmetros de configuração, como limite de registros, tamanho de checkpoint e um ID OpenAlex de trabalho inicial.

## Parâmetros

Os seguintes parâmetros podem ser passados para ajustar a coleta:

- `method`: Escolhe o método de coleta (`author` para coleta baseada em autor, `citation` para coleta baseada em citação, `author_limit` para coleta baseada em autor com limite no número de autores, `author_graph` para coleta baseada em grafo de autores usando BFS).
- `--record_limit`: Limite de registros a serem coletados (padrão: 100000). Para `author_limit` e `author_graph`, este é o limite de autores.
- `--checkpoint_size`: Tamanho do checkpoint para salvar progresso (padrão: 500). Nota: `author_graph` não utiliza checkpoints atualmente.
- `--initial_work_id`: ID do trabalho inicial ou ID/URL do autor inicial para começar a coleta (padrão: `W4398186459`). Para `author_graph`, pode ser um ID de autor (começa com 'A') ou URL de autor (ex: `https://openalex.org/A5080238381`).

## Instalação

1. Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina.
2. Instale o `uv` se ainda não tiver:
   ```bash
   pip install uv
   ```
3. Clone este repositório ou baixe os arquivos.
4. Instale as dependências usando o `uv`:
   ```bash
   uv sync
   ```

## Executando o código

Você pode executar o código a partir da linha de comando usando o `uv`, especificando o método de coleta e os parâmetros desejados.

### Exemplo de uso - Coleta baseada em autores:

```bash
uv run python main.py author --record_limit 50000 --checkpoint_size 1000 --initial_work_id "W4398186459"
```

### Exemplo de uso - Coleta baseada em citações:

```bash
uv run python main.py citation --record_limit 75000 --checkpoint_size 250 --initial_work_id "W4398186459"
```

### Exemplo de uso - Coleta baseada em autores com limite de autores:

```bash
uv run python main.py author_limit --record_limit 1000 --checkpoint_size 50 --initial_work_id "W4398186459"
```

### Exemplo de uso - Coleta baseada em grafo de autores (BFS):

```bash
uv run python main.py author_graph --record_limit 5000 --checkpoint_size 100 --initial_work_id "A5080238381"
```

Ou usando uma URL de autor:

```bash
uv run python main.py author_graph --record_limit 5000 --initial_work_id "https://openalex.org/A5080238381"
```

Ou usando um ID de trabalho (o primeiro autor do trabalho será usado):

```bash
uv run python main.py author_graph --record_limit 5000 --initial_work_id "W4398186459"
```

## Parâmetros opcionais:

- `record_limit`: Define o limite de registros a serem coletados. Se omitido, o padrão é 100000. Para `author_limit` e `author_graph`, este é o limite de autores.
- `checkpoint_size`: Define o tamanho do checkpoint, que determina quantos registros são processados antes de salvar o progresso. Se omitido, o padrão é 500. Nota: `author_graph` não utiliza checkpoints atualmente.
- `initial_work_id`: Define o ID do trabalho inicial ou ID/URL do autor inicial para iniciar a coleta. Se omitido, o padrão é "W4398186459". Para `author_graph`, pode ser um ID de autor (começa com 'A') ou URL de autor.

## Diferenças entre os métodos:

- **author**: Percorre o grafo através dos autores, coletando trabalhos até atingir o limite de trabalhos especificado.
- **citation**: Percorre o grafo através das citações, coletando trabalhos até atingir o limite de trabalhos especificado.
- **author_limit**: Percorre o grafo através dos autores, mas para quando atinge o limite de autores especificado (não trabalhos).
- **author_graph**: Usa busca em largura (BFS) para percorrer o grafo de co-autores. Coleta todos os trabalhos de cada autor e expande através dos co-autores encontrados. Para quando atinge o limite de autores distintos especificado. Também baixa metadados detalhados dos autores coletados em um arquivo separado (`unique_authors_metadata.csv`).

## Contribuindo

Se você encontrar problemas ou tiver sugestões de melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.
