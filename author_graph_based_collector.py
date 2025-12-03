import OpenalexUtils
import OpenalexWriter
from collections import deque
import time
import os

# CONFIGURAÇÕES
START_AUTHOR_ID = (
    "https://openalex.org/A5080238381"  # Substitua pelo ID/URL do autor inicial
)
MAX_AUTHORS_TO_COLLECT = 1000  # Limite N de autores diferentes
OUTPUT_DIR = "output_data"

# Nomes dos arquivos de saída
FILES = {
    "works": f"{OUTPUT_DIR}/works.csv",
    "authorships": f"{OUTPUT_DIR}/authorships.csv",  # Relação Trabalho-Autor
    "unique_authors": f"{OUTPUT_DIR}/unique_authors_metadata.csv",  # Detalhes dos Autores
    "citations": f"{OUTPUT_DIR}/citations.csv",
    "concepts": f"{OUTPUT_DIR}/concepts.csv",
    "topics": f"{OUTPUT_DIR}/topics.csv",
    "keywords": f"{OUTPUT_DIR}/keywords.csv",
    "related": f"{OUTPUT_DIR}/related_works.csv",
}


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def run_bfs_collection():
    ensure_output_dir()

    # Normaliza o ID do autor inicial
    start_id = START_AUTHOR_ID.split("/")[-1]

    # Estruturas de controle
    # Queue: fila de autores para processar (pegar os trabalhos)
    queue = deque([start_id])

    # Collected: autores que já "descobrimos" e contamos para o limite N
    collected_authors_ids = {start_id}

    # Processed: autores cujos trabalhos JÁ baixamos (para não baixar de novo)
    processed_authors_ids = set()

    # Seen Works: trabalhos já salvos para evitar duplicatas no CSV
    seen_works_ids = set()

    print(f"--- Iniciando Coleta BFS ---")
    print(f"Autor Inicial: {start_id}")
    print(f"Meta: Coletar {MAX_AUTHORS_TO_COLLECT} autores distintos.")
    print("-" * 30)

    while queue:
        # Verifica se já atingimos o limite de autores COLETADOS
        # Para imediatamente quando o limite for atingido
        if len(collected_authors_ids) >= MAX_AUTHORS_TO_COLLECT:
            print("Limite de autores atingido. Parando busca.")
            break

        current_author_id = queue.popleft()

        # Evita reprocessar autor (ciclos)
        if current_author_id in processed_authors_ids:
            continue

        print(f"\nProcessando autor: {current_author_id}")
        print(
            f"Status: {len(collected_authors_ids)}/{MAX_AUTHORS_TO_COLLECT} autores coletados. Fila: {len(queue)}"
        )

        # 1. Busca TODOS os trabalhos deste autor
        # Passamos como lista pois a função espera lista
        works = OpenalexUtils.get_author_works([current_author_id])
        processed_authors_ids.add(current_author_id)

        new_works_buffer = []

        # 2. Processa cada trabalho
        for work in works:
            w_id = work["id"]

            # Se o trabalho é novo, salvamos
            if w_id not in seen_works_ids:
                seen_works_ids.add(w_id)
                new_works_buffer.append(work)

                # 3. Extrai co-autores (autores que não repetiram)
                for authorship in work.get("authorships", []):
                    auth_obj = authorship.get("author")
                    if not auth_obj:
                        continue

                    auth_id_raw = auth_obj.get("id")
                    if not auth_id_raw:
                        continue

                    auth_id = auth_id_raw.split("/")[-1]

                    # Se é um autor novo (não coletado ainda)
                    if auth_id not in collected_authors_ids:
                        # Só adicionamos à fila se ainda não atingimos o limite N
                        if len(collected_authors_ids) < MAX_AUTHORS_TO_COLLECT:
                            collected_authors_ids.add(auth_id)
                            queue.append(auth_id)
                            # print(f"  + Novo autor encontrado: {auth_id}")
                        else:
                            # Atingiu o limite, não adiciona mais à fila
                            # Mas a autoria deste trabalho ainda será salva em 'authorships.csv'
                            pass

        # 4. Escreve os dados no disco (apenas se houver novos trabalhos)
        if new_works_buffer:
            print(f"  > Salvando {len(new_works_buffer)} novos trabalhos...")
            OpenalexWriter.write_works_to_csv(FILES["works"], new_works_buffer)
            OpenalexWriter.write_authors_to_csv(
                FILES["authorships"], new_works_buffer
            )  # Relação Trabalho-Autor
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

        # Verifica parada se a fila esvaziar ou se quisermos parar estritamente
        if not queue and len(collected_authors_ids) >= MAX_AUTHORS_TO_COLLECT:
            break

    print("\n" + "=" * 30)
    print("Busca e extração de trabalhos finalizada.")
    print(f"Total de autores únicos identificados: {len(collected_authors_ids)}")

    # 5. Passo Final: Buscar Metadados Detalhados dos Autores Coletados
    # Até agora temos os IDs e nomes via 'authorships', mas se quiser dados como
    # 'last_known_institution' ou 'summary_stats' para o CSV de autores, precisamos buscar na API de autores.

    print("Baixando metadados detalhados para os autores coletados...")

    all_authors_list = list(collected_authors_ids)
    chunk_size = 50  # Tamanho do lote seguro para a URL da API

    total_chunks = (len(all_authors_list) // chunk_size) + 1

    for i in range(0, len(all_authors_list), chunk_size):
        chunk = all_authors_list[i : i + chunk_size]
        print(
            f"Baixando lote {i//chunk_size + 1}/{total_chunks} ({len(chunk)} autores)..."
        )

        try:
            # Reutiliza função do Utils
            data = OpenalexUtils.get_data_authors_from_openalex(chunk)
            results = data.get("results", [])

            # Salva no CSV de autores únicos
            OpenalexWriter.write_unique_authors_metadata(
                FILES["unique_authors"], results
            )

            time.sleep(0.2)  # Respeitar API

        except Exception as e:
            print(f"Erro ao baixar lote de autores: {e}")

    print("\nProcesso Completo com Sucesso!")


if __name__ == "__main__":
    run_bfs_collection()
