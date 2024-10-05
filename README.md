# OpenAlex CSV Data Collector - Author & Citation Based

Este projeto contém dois métodos de coleta de dados: um baseado em autores e outro baseado em citações. Ele permite coletar registros de dados da api do openalex (`https://api.openalex.org`), salvando os resultados em checkpoints para facilitar a retomada da coleta em caso de interrupções.

## Como funciona

O projeto possui dois scripts principais:

- **AuthorBasedCollector.py**: Coleta de dados baseada em autores.
- **CitationBasedCollector.py**: Coleta de dados baseada em citações.

Durante a execução, o sistema coleta e armazena sete principais tipos de informações, que são salvas em arquivos CSV dentro de uma pasta especificada (`citations_based_database` ou `author_based_database`):

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

- `method`: Escolhe o método de coleta (`author` para coleta baseada em autor, `citation` para coleta baseada em citação).
- `--record_limit`: Limite de registros a serem coletados (padrão: 100000).
- `--checkpoint_size`: Tamanho do checkpoint para salvar progresso (padrão: 500).
- `--initial_work_id`: ID do trabalho inicial para começar a coleta (padrão: `W4398186459`).

## Instalação

1. Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina.
2. Clone este repositório ou baixe os arquivos.
3. (Opcional) Crie um ambiente virtual para isolar as dependências:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

4. Instale as dependências listadas no arquivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Executando o código

Você pode executar o código a partir da linha de comando, especificando o método de coleta e os parâmetros desejados.

### Exemplo de uso - Coleta baseada em autores:

```bash
python main.py author --record_limit 50000 --checkpoint_size 1000 --initial_work_id "W4398186459"
```

## Exemplo de uso - Coleta baseada em citações:

```bash
python main.py citation --record_limit 75000 --checkpoint_size 250 nitial_work_id "W4398186459"
```

## Parâmetros opcionais:
- `record_limit`: Define o limite de registros a serem coletados. Se omitido, o padrão é 100000.
- `checkpoint_size`: Define o tamanho do checkpoint, que determina quantos registros são processados antes de salvar o progresso. Se omitido, o padrão é 500.
- `initial_work_id`: Define o ID do trabalho inicial para iniciar a coleta. Se omitido, o padrão é "W4398186459".

## Contribuindo
Se você encontrar problemas ou tiver sugestões de melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.