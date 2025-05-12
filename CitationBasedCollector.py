import os

import requests
import time
from collections import deque
from tqdm import tqdm
import datetime

from OpenalexCheckpoints import load_checkpoint, save_checkpoint_citations_based
from OpenalexUtils import get_data_from_openalex, batch_size, sleep_time
from OpenalexWriter import write_works_to_csv, write_citations_to_csv, \
    write_related_works_to_csv, write_authors_to_csv, write_concepts_to_csv, \
    write_topics_to_csv, write_keywords_to_csv, generate_progress_report


def main(record_limit, checkpoint_size, initial_work_id):
    print(f"Record limit: {record_limit}")
    print(f"Checkpoint size: {checkpoint_size}")
    print(f"Initial work ID: {initial_work_id}")
    
    csv_base_folder = f'{initial_work_id}_citations_based_database'

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
        queue = deque(checkpoint['queue'])
        work_visited = set(checkpoint['visited'])
        works_count = checkpoint['count']
        authors_count = checkpoint['authors_count']
        citations_count = checkpoint['citations_count']
        related_works_count = checkpoint['related_works_count']
        concepts_count = checkpoint['concepts_count']
        topics_count = checkpoint['topics_count']
        keywords_count = checkpoint['keywords_count']
    else:
        queue = deque([initial_work_id])
        work_visited = set()
        works_count = 0
        authors_count = 0
        citations_count = 0
        related_works_count = 0
        concepts_count = 0
        topics_count = 0
        keywords_count = 0

    # Início da coleta
    start_time = datetime.datetime.now()

    # Coleta os dados
    with tqdm(total=record_limit, desc="Collecting data") as pbar:
        pbar.update(works_count)
        while queue and works_count < record_limit:
            batch_ids = []
            while queue and len(batch_ids) < batch_size:
                current_work_id = queue.popleft()
                if current_work_id not in work_visited:
                    batch_ids.append(current_work_id)

            if not batch_ids:
                continue

            try:
                data = get_data_from_openalex(batch_ids)
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve data for batch {batch_ids}: {e}")
                continue

            works = data['results']
            write_works_to_csv(csv_works_filename, works, mode='a')
            write_authors_to_csv(csv_authors_filename, works, mode='a')
            write_citations_to_csv(csv_citations_filename, works, mode='a')
            write_related_works_to_csv(csv_related_works_filename, works, mode='a')
            write_concepts_to_csv(csv_concepts_filename, works, mode='a')
            write_topics_to_csv(csv_topics_filename, works, mode='a')
            write_keywords_to_csv(csv_keywords_filename, works, mode='a')

            for work in works:
                work_visited.add(work['id'])
                works_count += 1
                authors_count += len(work.get('authorships', []))
                citations_count += len(work.get('referenced_works', []))
                related_works_count += len(work.get('related_works', []))
                concepts_count += len(work.get('concepts', []))
                topics_count += len(work.get('topics', []))
                keywords_count += len(work.get('keywords', []))

                for cited_work_id in work.get('referenced_works', []):
                    if cited_work_id not in work_visited:
                        queue.append(cited_work_id)

            # Atualiza o progresso
            pbar.update(len(works))

            # Salva o checkpoint
            if works_count // checkpoint_size > (works_count - len(works)) // checkpoint_size:
                save_checkpoint_citations_based(
                    list(queue),
                    list(work_visited),
                    works_count,
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
                    works_count,
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
    save_checkpoint_citations_based(
        list(queue),
        list(work_visited),
        works_count,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        checkpoint_file
    )
    print(f"Data collection complete: {works_count} records collected.")
    generate_progress_report(
        start_time,
        works_count,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        progress_report_file
    )
    print("Progress report generated.")
