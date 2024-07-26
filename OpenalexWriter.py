import csv
import datetime
import os

from OpenalexUtils import parse_abstract_inverted_index


# Função para escrever dados no arquivo CSV dos trabalhos
def write_works_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id',
            'title',
            'abstract',
            'doi',
            'publication_date',
            'cited_by_count',
            'language',
            'type',
            'fwci',
            'open_access',
            'has_fulltext',
            'is_retracted',
            'is_paratext',
            'locations_count',
            'countries_distinct_count',
            'institutions_distinct_count',
            'referenced_works_count'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            writer.writerow({
                'id': work.get('id'),
                'title': work.get('title'),
                'abstract': parse_abstract_inverted_index(work.get('abstract_inverted_index', {})),
                'doi': work.get('doi'),
                'publication_date': work.get('publication_date'),
                'cited_by_count': work.get('cited_by_count', 0),
                'language': work.get('language'),
                'type': work.get('type'),
                'fwci': work.get('fwci', 0),
                'open_access': work['open_access'].get('is_oa', False),
                'has_fulltext': work.get('has_fulltext', False),
                'is_retracted': work.get('is_retracted', False),
                'is_paratext': work.get('is_paratext', False),
                'locations_count': work.get('locations_count', 0),
                'countries_distinct_count': work.get('countries_distinct_count', 0),
                'institutions_distinct_count': work.get('institutions_distinct_count', 0),
                'referenced_works_count': work.get('referenced_works_count', 0),
            })


# Função para escrever dados no arquivo CSV dos autores
def write_authors_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'author_id', 'author_name', 'author_position', 'is_corresponding', 'countries']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for author in work['authorships']:
                writer.writerow({
                    'work_id': work['id'],
                    'author_id': author['author']['id'],
                    'author_name': author['author'].get('display_name'),
                    'author_position': author.get('author_position'),
                    'is_corresponding': author.get('is_corresponding', False),
                    'countries': '|'.join(author.get('countries', [])),
                })


# Função para escrever dados no arquivo CSV das citações
def write_citations_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'cited_work_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for cited_work in work.get('referenced_works', []):
                writer.writerow({
                    'work_id': work['id'],
                    'cited_work_id': cited_work
                })


# Função para escrever dados no arquivo CSV dos trabalhos relacionados
def write_related_works_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'related_work_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for related_work in work.get('related_works', []):
                writer.writerow({
                    'work_id': work['id'],
                    'related_work_id': related_work
                })


# Função para escrever dados no arquivo CSV dos conceitos
def write_concepts_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'concept_id', 'concept_name', 'wikidata', 'level', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for concept in work['concepts']:
                writer.writerow({
                    'work_id': work['id'],
                    'concept_id': concept.get('id'),
                    'concept_name': concept.get('display_name'),
                    'wikidata': concept.get('wikidata'),
                    'level': concept.get('level', 0),
                    'score': concept.get('score', 0),
                })


# Função para escrever dados no arquivo CSV dos tópicos
def write_topics_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'topic_id', 'topic_name', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for topic in work['topics']:
                writer.writerow({
                    'work_id': work['id'],
                    'topic_id': topic.get('id'),
                    'topic_name': topic.get('display_name'),
                    'score': topic.get('score', 0),
                })


# Função para escrever dados no arquivo CSV das palavras-chave
def write_keywords_to_csv(filename, works, mode='a'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['work_id', 'keyword_id', 'keyword_name', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or mode == 'w':
            writer.writeheader()

        for work in works:
            for keyword in work['keywords']:
                writer.writerow({
                    'work_id': work['id'],
                    'keyword_id': keyword.get('id'),
                    'keyword_name': keyword.get('display_name'),
                    'score': keyword.get('score', 0),
                })


# Função para gerar relatório de progresso
def generate_progress_report(
        start_time,
        total_count,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        report_file
):
    file_exists = os.path.isfile(report_file)
    with open(report_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'timestamp',
            'total_count',
            'authors_count',
            'citations_count',
            'related_works_count',
            'concepts_count',
            'topics_count',
            'keywords_count',
            'elapsed_time'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        elapsed_time = datetime.datetime.now() - start_time
        writer.writerow({
            'timestamp': datetime.datetime.now().isoformat(),
            'total_count': total_count,
            'authors_count': authors_count,
            'citations_count': citations_count,
            'related_works_count': related_works_count,
            'concepts_count': concepts_count,
            'topics_count': topics_count,
            'keywords_count': keywords_count,
            'elapsed_time': str(elapsed_time)
        })
