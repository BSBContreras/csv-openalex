import time
import requests
from tqdm import tqdm

# URL base da API do OpenAlex
works_base_url = "https://api.openalex.org/works"
authors_base_url = "https://api.openalex.org/authors"
institutions_base_url = "https://api.openalex.org/institutions"
batch_size = 50  # Reduzido levemente para evitar erros de URL muito longa em filtros
per_page = 200
sleep_time = 0.2


def get_data_works_from_openalex(work_urls: list[str]) -> dict:
    """Get works from OpenAlex API."""
    work_ids = [work_url.split("/")[-1] for work_url in work_urls]
    params = {"filter": f"openalex:{'|'.join(work_ids)}", "per-page": batch_size}
    response = requests.get(works_base_url, params=params)
    response.raise_for_status()
    return response.json()


def get_data_authors_from_openalex(author_urls: list[str]) -> dict:
    """Get authors from OpenAlex API."""
    # Garante que pegamos apenas o ID, caso venha a URL completa
    author_ids = [author_url.split("/")[-1] for author_url in author_urls]

    # OpenAlex pode falhar se a URL do filtro for muito longa, então é bom chamar essa função com lotes (chunks)
    params = {"filter": f"openalex:{'|'.join(author_ids)}", "per-page": len(author_ids)}
    response = requests.get(authors_base_url, params=params)
    response.raise_for_status()
    return response.json()


def get_data_institutions_from_openalex(institution_urls: list[str]) -> dict:
    """Get institutions from OpenAlex API."""
    # Garante que pegamos apenas o ID, caso venha a URL completa
    institution_ids = [inst_url.split("/")[-1] for inst_url in institution_urls]

    # OpenAlex pode falhar se a URL do filtro for muito longa, então é bom chamar essa função com lotes (chunks)
    params = {"filter": f"openalex:{'|'.join(institution_ids)}", "per-page": len(institution_ids)}
    response = requests.get(institutions_base_url, params=params)
    response.raise_for_status()
    return response.json()


def get_data_authors_samples(samples: int = 1, seed: int = 42):
    """Get works sample from OpenAlex API."""
    params = {"seed": seed, "sample": samples, "per-page": batch_size}
    response = requests.get(authors_base_url, params=params)
    response.raise_for_status()
    return response.json()


def get_auhtor_sample(seed: int = 42) -> dict:
    """Get author sample from OpenAlex API."""
    data = get_data_authors_samples(samples=1, seed=seed)
    return data["results"][0]


# Função para obter os trabalhos publicados por um autor
def get_author_works(author_urls: list[str]) -> list[dict]:
    """Get author works from OpenAlex API."""
    author_ids = [author_url.split("/")[-1] for author_url in author_urls]
    works = []
    cursor = "*"

    # Descrição dinâmica para saber qual autor está sendo baixado se for apenas 1
    desc = "Fetching works"
    if len(author_ids) == 1:
        desc = f"Fetching works for {author_ids[0]}"

    pbar = tqdm(total=1, leave=False, desc=desc)

    while True:
        params = {
            "filter": f"author.id:{'|'.join(author_ids)}",
            "per-page": per_page,
            "cursor": cursor,
        }
        try:
            response = requests.get(works_base_url, params=params)
            response.raise_for_status()
            data = response.json()

            pbar.total = data["meta"]["count"]
            pbar.update(len(data["results"]))
            works.extend(data["results"])

            if not data["meta"]["next_cursor"]:
                break

            cursor = data["meta"]["next_cursor"]
            time.sleep(sleep_time)

        except requests.exceptions.RequestException as e:
            print(f"\nErro na requisição: {e}")
            time.sleep(1)  # Espera um pouco antes de tentar de novo ou sair
            break

    pbar.close()
    return works


def parse_abstract_inverted_index(inverted_index):
    if inverted_index is None:
        return ""

    abstract_words = []

    for word, positions in inverted_index.items():
        for pos in positions:
            abstract_words.append((pos, word))

    abstract_words.sort()

    abstract = " ".join(
        word.replace("\n", " ").replace("\r", "") for pos, word in abstract_words
    )

    return abstract
