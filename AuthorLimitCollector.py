import os

import requests
import time
from collections import deque
from tqdm import tqdm
import datetime

from OpenalexCheckpoints import load_checkpoint, save_checkpoint_author_limit
from OpenalexUtils import get_data_from_openalex, get_author_works, batch_size, sleep_time
from OpenalexWriter import write_works_to_csv, write_citations_to_csv, \
    write_related_works_to_csv, write_authors_to_csv, write_concepts_to_csv, \
    write_topics_to_csv, write_keywords_to_csv, generate_progress_report


def main(record_limit, checkpoint_size, initial_work_id):
    print(f"Author limit: {record_limit}")
    print(f"Checkpoint size: {checkpoint_size}")
    print(f"Initial work ID: {initial_work_id}")
    
    csv_base_folder = f'{initial_work_id}_author_limit_database'

    if not os.path.exists(csv_base_folder):
        os.makedirs(csv_base_folder)

    csv_works_filename = f'{csv_base_folder}/openalex_works.csv'
    csv_authors_filename = f'{csv_base_folder}/openalex_authors.csv'
    csv_citations_filename = f'{csv_base_folder}/openalex_citations.csv'
    csv_related_works_filename = f'{csv_base_folder}/openalex_related_works.csv'
    csv_concepts_filename = f'{csv_base_folder}/openalex_concepts.csv'
    csv_topics_filename = f'{csv_base_folder}/openalex_topics.csv'
    csv_keywords_filename = f'{csv_base_folder}/openalex_keywords.csv'

    progress_report_file = f'{csv_base_folder}/openalex_progress_report.csv'
    checkpoint_file = f'{csv_base_folder}/openalex_checkpoint.pkl'

    # Carrega o estado salvo, se existir
    checkpoint = load_checkpoint(checkpoint_file)
    if checkpoint:
        author_queue = deque(checkpoint['queue'])
        work_visited = set(checkpoint['work_visited'])
        author_visited = set(checkpoint['author_visited'])
        work_counts = checkpoint['work_counts']
        authors_count = checkpoint['authors_count']
        citations_count = checkpoint['citations_count']
        related_works_count = checkpoint['related_works_count']
        concepts_count = checkpoint['concepts_count']
        topics_count = checkpoint['topics_count']
        keywords_count = checkpoint['keywords_count']
    else:
        data = get_data_from_openalex([initial_work_id])
        work = data['results'][0]

        author_queue = deque([author['author']['id'] for author in work['authorships']])
        work_visited = set()
        author_visited = set()
        work_counts = 0
        authors_count = 0
        citations_count = 0
        related_works_count = 0
        concepts_count = 0
        topics_count = 0
        keywords_count = 0

    # Início da coleta
    start_time = datetime.datetime.now()

    # Coleta os dados
    with tqdm(total=record_limit, desc="Collecting authors") as pbar:
        pbar.update(authors_count)
        while author_queue and authors_count < record_limit:
            batch_ids = []
            while author_queue and len(batch_ids) < batch_size:
                current_author_id = author_queue.popleft()
                if current_author_id not in author_visited:
                    batch_ids.append(current_author_id)
                    author_visited.add(current_author_id)

            if not batch_ids:
                continue

            try:
                data = get_author_works(batch_ids)
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve data for batch {batch_ids}: {e}")
                continue

            works = []
            for work in data:
                if work['id'] not in work_visited:
                    works.append(work)

            write_works_to_csv(csv_works_filename, works, mode='a')
            write_authors_to_csv(csv_authors_filename, works, only_authors=batch_ids, mode='a')
            write_citations_to_csv(csv_citations_filename, works, mode='a')
            write_related_works_to_csv(csv_related_works_filename, works, mode='a')
            write_concepts_to_csv(csv_concepts_filename, works, mode='a')
            write_topics_to_csv(csv_topics_filename, works, mode='a')
            write_keywords_to_csv(csv_keywords_filename, works, mode='a')

            # Atualiza contadores
            authors_count += len(batch_ids)

            for work in works:
                work_visited.add(work['id'])
                work_counts += 1
                citations_count += len(work.get('referenced_works', []))
                related_works_count += len(work.get('related_works', []))
                concepts_count += len(work.get('concepts', []))
                topics_count += len(work.get('topics', []))
                keywords_count += len(work.get('keywords', []))

                # Adicionar trabalhos dos autores do trabalho atual à fila
                for author in work['authorships']:
                    author_work_id = author['author']['id']
                    if author_work_id not in author_visited:
                        author_queue.append(author_work_id)

            # Atualiza o progresso baseado no número de autores
            pbar.update(len(batch_ids))

            # Salva o checkpoint baseado no número de autores processados
            if authors_count // checkpoint_size > (authors_count - len(batch_ids)) // checkpoint_size:
                save_checkpoint_author_limit(
                    list(author_queue),
                    list(work_visited),
                    list(author_visited),
                    work_counts,
                    authors_count,
                    citations_count,
                    related_works_count,
                    concepts_count,
                    topics_count,
                    keywords_count,
                    checkpoint_file
                )
                generate_progress_report(
                    start_time,
                    work_counts,
                    authors_count,
                    citations_count,
                    related_works_count,
                    concepts_count,
                    topics_count,
                    keywords_count,
                    progress_report_file
                )

            # Espera entre as requisições para não sobrecarregar a API
            time.sleep(sleep_time)

    # Salva o checkpoint final
    save_checkpoint_author_limit(
        list(author_queue),
        list(work_visited),
        list(author_visited),
        work_counts,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        checkpoint_file
    )
    print(f"Data collection complete: {authors_count} authors processed, {work_counts} works collected.")
    generate_progress_report(
        start_time,
        work_counts,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        progress_report_file
    )
    print("Progress report generated.")
