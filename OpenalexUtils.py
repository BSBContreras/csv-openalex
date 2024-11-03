import time
import requests

# URL base da API do OpenAlex
works_base_url = "https://api.openalex.org/works"
authors_base_url = "https://api.openalex.org/authors"
batch_size = 100
per_page = 200
sleep_time = 0.2


# Função para fazer requisição à API e obter dados
def get_data_from_openalex(work_urls):
    work_ids = [work_url.split('/')[-1] for work_url in work_urls]
    params = {
        'filter': f"openalex:{'|'.join(work_ids)}",
        'per-page': batch_size
    }
    response = requests.get(works_base_url, params=params)
    response.raise_for_status()
    return response.json()


# Função para obter os trabalhos publicados por um autor
def get_author_works(author_urls):
    author_ids = [author_url.split('/')[-1] for author_url in author_urls]
    works = []
    page = 1

    while True:
        params = {
            'filter': f"author.id:{'|'.join(author_ids)}",
            'per-page': per_page,
            'page': page
        }
        response = requests.get(works_base_url, params=params)
        response.raise_for_status()
        data = response.json()
        works.extend(data['results'])

        if page * per_page >= data['meta']['count']:
            break

        page += 1

        # Espera entre as requisições para não sobrecarregar a API
        time.sleep(sleep_time)

    return works


# Função para obter informações de um autor
def get_authors(author_urls):
    author_ids = [author_url.split('/')[-1] for author_url in author_urls]
    authors = []
    page = 1

    while True:
        params = {
            'filter': f"openalex:{'|'.join(author_ids)}",
            'per-page': per_page,
            'page': page
        }
        response = requests.get(authors_base_url, params=params)
        response.raise_for_status()
        data = response.json()
        authors.extend(data['results'])

        if page * per_page >= data['meta']['count']:
            break

        page += 1

        # Espera entre as requisições para não sobrecarregar a API
        time.sleep(sleep_time)

    return authors


def parse_abstract_inverted_index(inverted_index):
    if inverted_index is None:
        return ''

    abstract_words = []

    for word, positions in inverted_index.items():
        for pos in positions:
            abstract_words.append((pos, word))

    abstract_words.sort()

    abstract = ' '.join(word for pos, word in abstract_words)

    return abstract
