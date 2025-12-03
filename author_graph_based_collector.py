"""Author graph based collector."""

import os
from OpenalexUtils import get_author_works


# Luciano Antonio Digiampietri
AUTHOR_URL = "https://openalex.org/A5080238381"
works = get_author_works([AUTHOR_URL])
print(works[0])
print(len(works))


def main(record_limit, checkpoint_size, initial_author_id):
    print(f"Record limit: {record_limit}")
    print(f"Checkpoint size: {checkpoint_size}")
    print(f"Initial author ID: {initial_author_id}")

    csv_base_folder = f"{initial_author_id}_author_graph_based_database"

    if not os.path.exists(csv_base_folder):
        os.makedirs(csv_base_folder)

    csv_works_filename = f"{csv_base_folder}/openalex_works.csv"
    csv_authors_filename = f"{csv_base_folder}/openalex_authors.csv"
    csv_citations_filename = f"{csv_base_folder}/openalex_citations.csv"
    csv_related_works_filename = f"{csv_base_folder}/openalex_related_works.csv"
    csv_concepts_filename = f"{csv_base_folder}/openalex_concepts.csv"
    csv_topics_filename = f"{csv_base_folder}/openalex_topics.csv"
    csv_keywords_filename = f"{csv_base_folder}/openalex_keywords.csv"
