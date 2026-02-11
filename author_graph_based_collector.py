import OpenalexUtils
import OpenalexWriter
from collections import deque
import time
import os


def get_files(output_dir):
    return {
        "works": f"{output_dir}/works.csv",
        "authorships": f"{output_dir}/authorships.csv",
        "unique_authors": f"{output_dir}/unique_authors_metadata.csv",
        "unique_institutions": f"{output_dir}/unique_institutions_metadata.csv",
        "citations": f"{output_dir}/citations.csv",
        "concepts": f"{output_dir}/concepts.csv",
        "topics": f"{output_dir}/topics.csv",
        "keywords": f"{output_dir}/keywords.csv",
        "related": f"{output_dir}/related_works.csv",
    }


def ensure_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def get_initial_author_id(initial_work_id):
    """
    Extrai o ID do autor inicial a partir de um work_id ou autor_id.
    Se initial_work_id começar com 'A' ou for uma URL de autor, usa diretamente.
    Caso contrário, busca o trabalho e extrai o primeiro autor.
    """
    if initial_work_id.startswith("A") or "/A" in initial_work_id:
        if "/" in initial_work_id:
            return initial_work_id.split("/")[-1]
        return initial_work_id

    try:
        data = OpenalexUtils.get_data_works_from_openalex([initial_work_id])
        if data.get("results") and len(data["results"]) > 0:
            work = data["results"][0]
            if work.get("authorships") and len(work["authorships"]) > 0:
                author_id_raw = work["authorships"][0]["author"]["id"]
                return author_id_raw.split("/")[-1]
    except Exception as e:
        print(f"Erro ao buscar autor inicial do trabalho {initial_work_id}: {e}")

    return "A5080238381"


def run_bfs_collection(max_authors_to_collect, output_dir, initial_author_id):
    ensure_output_dir(output_dir)

    FILES = get_files(output_dir)

    # Normaliza o ID do autor inicial
    start_id = (
        initial_author_id.split("/")[-1]
        if "/" in initial_author_id
        else initial_author_id
    )

    queue = deque([start_id])
    collected_authors_ids = {start_id}
    processed_authors_ids = set()
    seen_works_ids = set()
    collected_institution_ids = set()

    print("--- Iniciando Coleta BFS ---")
    print(f"Autor Inicial: {start_id}")
    print(f"Meta: Coletar {max_authors_to_collect} autores distintos.")
    print("-" * 30)

    while queue:
        if len(collected_authors_ids) >= max_authors_to_collect:
            print("Limite de autores atingido. Parando busca.")
            break

        current_author_id = queue.popleft()

        if current_author_id in processed_authors_ids:
            continue

        print(f"\nProcessando autor: {current_author_id}")
        print(
            f"Status: {len(collected_authors_ids)}/{max_authors_to_collect} autores coletados. Fila: {len(queue)}"
        )

        works = OpenalexUtils.get_author_works([current_author_id])
        processed_authors_ids.add(current_author_id)

        new_works_buffer = []

        for work in works:
            w_id = work["id"]

            if w_id not in seen_works_ids:
                seen_works_ids.add(w_id)
                new_works_buffer.append(work)

                for authorship in work.get("authorships", []):
                    auth_obj = authorship.get("author")
                    if not auth_obj:
                        continue

                    auth_id_raw = auth_obj.get("id")
                    if not auth_id_raw:
                        continue

                    auth_id = auth_id_raw.split("/")[-1]

                    if auth_id not in collected_authors_ids:
                        if len(collected_authors_ids) < max_authors_to_collect:
                            collected_authors_ids.add(auth_id)
                            queue.append(auth_id)

                    # Coletar IDs de instituições
                    for inst in authorship.get("institutions", []):
                        if inst.get("id"):
                            collected_institution_ids.add(inst["id"])

        if new_works_buffer:
            print(f"  > Salvando {len(new_works_buffer)} novos trabalhos...")
            OpenalexWriter.write_works_to_csv(FILES["works"], new_works_buffer)
            OpenalexWriter.write_authors_to_csv(FILES["authorships"], new_works_buffer)
            OpenalexWriter.write_citations_to_csv(FILES["citations"], new_works_buffer)
            OpenalexWriter.write_related_works_to_csv(
                FILES["related"], new_works_buffer
            )
            OpenalexWriter.write_concepts_to_csv(FILES["concepts"], new_works_buffer)
            OpenalexWriter.write_topics_to_csv(FILES["topics"], new_works_buffer)
            OpenalexWriter.write_keywords_to_csv(FILES["keywords"], new_works_buffer)
        else:
            print(
                "  > Nenhum trabalho novo (todos já processados via co-autores anteriores)."
            )

        if not queue and len(collected_authors_ids) >= max_authors_to_collect:
            break

    print("\n" + "=" * 30)
    print("Busca e extração de trabalhos finalizada.")
    print(f"Total de autores únicos identificados: {len(collected_authors_ids)}")

    print("Baixando metadados detalhados para os autores coletados...")

    all_authors_list = list(collected_authors_ids)
    chunk_size = 50

    total_chunks = (len(all_authors_list) // chunk_size) + 1

    for i in range(0, len(all_authors_list), chunk_size):
        chunk = all_authors_list[i : i + chunk_size]
        print(
            f"Baixando lote {i//chunk_size + 1}/{total_chunks} ({len(chunk)} autores)..."
        )

        try:
            data = OpenalexUtils.get_data_authors_from_openalex(chunk)
            results = data.get("results", [])

            OpenalexWriter.write_unique_authors_metadata(
                FILES["unique_authors"], results
            )

            time.sleep(0.2)

        except Exception as e:
            print(f"Erro ao baixar lote de autores: {e}")

    # Baixar metadados das instituições coletadas
    if collected_institution_ids:
        print(
            f"\nBaixando metadados detalhados para {len(collected_institution_ids)} instituições coletadas..."
        )

        all_institutions_list = list(collected_institution_ids)
        chunk_size = 50

        total_chunks = (len(all_institutions_list) // chunk_size) + 1

        for i in range(0, len(all_institutions_list), chunk_size):
            chunk = all_institutions_list[i : i + chunk_size]
            print(
                f"Baixando lote {i//chunk_size + 1}/{total_chunks} ({len(chunk)} instituições)..."
            )

            try:
                data = OpenalexUtils.get_data_institutions_from_openalex(chunk)
                results = data.get("results", [])

                OpenalexWriter.write_unique_institutions_metadata(
                    FILES["unique_institutions"], results
                )

                time.sleep(0.2)

            except Exception as e:
                print(f"Erro ao baixar lote de instituições: {e}")

    print("\nProcesso Completo com Sucesso!")


def main(record_limit, checkpoint_size, initial_work_id):
    """
    Função principal para coleta baseada em grafo de autores.

    Args:
        record_limit: Limite de autores distintos a serem coletados
        checkpoint_size: Tamanho do checkpoint (não utilizado atualmente, mantido para compatibilidade)
        initial_work_id: ID do trabalho inicial ou ID/URL do autor inicial
    """
    print(f"Author limit: {record_limit}")
    print(f"Checkpoint size: {checkpoint_size} (não utilizado neste método)")
    print(f"Initial work/author ID: {initial_work_id}")

    output_dir = f"{initial_work_id}_author_graph_database"
    initial_author_id = get_initial_author_id(initial_work_id)
    run_bfs_collection(record_limit, output_dir, initial_author_id)


if __name__ == "__main__":
    run_bfs_collection(10000, "output_data", "A5080238381")
