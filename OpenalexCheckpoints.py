import os
import pickle


# Função para salvar o estado atual (fila e contagem de registros)
def save_checkpoint_citations_based(
        queue,
        visited,
        count,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        checkpoint_file
):
    with open(checkpoint_file, 'wb') as f:
        pickle.dump({
            'queue': queue,
            'visited': visited,
            'count': count,
            'authors_count': authors_count,
            'citations_count': citations_count,
            'related_works_count': related_works_count,
            'concepts_count': concepts_count,
            'topics_count': topics_count,
            'keywords_count': keywords_count
        }, f)


def save_checkpoint_author_based(
        queue,
        work_visited,
        author_visited,
        count,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        checkpoint_file
):
    with open(checkpoint_file, 'wb') as f:
        pickle.dump({
            'queue': queue,
            'work_visited': work_visited,
            'author_visited': author_visited,
            'count': count,
            'authors_count': authors_count,
            'citations_count': citations_count,
            'related_works_count': related_works_count,
            'concepts_count': concepts_count,
            'topics_count': topics_count,
            'keywords_count': keywords_count
        }, f)


def save_checkpoint_author_limit(
        queue,
        work_visited,
        author_visited,
        work_counts,
        authors_count,
        citations_count,
        related_works_count,
        concepts_count,
        topics_count,
        keywords_count,
        checkpoint_file
):
    with open(checkpoint_file, 'wb') as f:
        pickle.dump({
            'queue': queue,
            'work_visited': work_visited,
            'author_visited': author_visited,
            'work_counts': work_counts,
            'authors_count': authors_count,
            'citations_count': citations_count,
            'related_works_count': related_works_count,
            'concepts_count': concepts_count,
            'topics_count': topics_count,
            'keywords_count': keywords_count
        }, f)


# Função para carregar o estado salvo
def load_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'rb') as f:
            return pickle.load(f)
    return None
