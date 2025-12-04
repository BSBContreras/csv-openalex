import csv
import os
from collections import defaultdict

# Caminho do arquivo gerado pelo seu script anterior
INPUT_FILE = "output_data/authorships.csv"


def analyze_coauthors():
    # Verifica se o arquivo existe
    if not os.path.exists(INPUT_FILE):
        print(f"Erro: O arquivo '{INPUT_FILE}' não foi encontrado.")
        print(
            "Certifique-se de rodar o coletor (author_graph_based_collector_v2.py) primeiro."
        )
        return

    print(f"Lendo dados de: {INPUT_FILE} ...")

    # Estruturas de dados
    # works_map: Dicionário onde a chave é o ID do trabalho e o valor é uma lista de IDs de autores nesse trabalho
    works_map = defaultdict(list)
    # names_map: Dicionário para guardar o nome do autor baseado no ID (para exibir bonito no final)
    names_map = {}

    # 1. Leitura do CSV
    try:
        with open(INPUT_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                work_id = row["work_id"]
                author_id = row["author_id"]
                author_name = row["author_name"]

                # Guarda a relação Trabalho -> Autor
                works_map[work_id].append(author_id)

                # Guarda o nome do autor (se já não tiver guardado)
                if author_id not in names_map:
                    names_map[author_id] = author_name

    except KeyError as e:
        print(f"Erro de formato no CSV: Coluna {e} não encontrada.")
        return

    # 2. Processamento de Coautores
    # coauthors_count: Dicionário onde chave é o ID do autor e valor é um SET de coautores (para evitar duplicatas)
    coauthors_map = defaultdict(set)
    # all_authors: Set com todos os autores que aparecem no arquivo (incluindo os de trabalhos solo)
    all_authors = set()

    print("Calculando conexões de coautoria...")

    for work_id, authors_list in works_map.items():
        # Adiciona todos os autores ao conjunto de todos os autores
        for author_id in authors_list:
            all_authors.add(author_id)

        # Se o trabalho tem apenas 1 autor, não gera coautoria
        if len(authors_list) < 2:
            continue

        # Para cada autor no trabalho, adiciona todos os outros como coautores
        for author_a in authors_list:
            for author_b in authors_list:
                if author_a != author_b:
                    # Adiciona B na lista de coautores de A
                    # Usamos set() para garantir que se trabalharam juntos 10 vezes, conte apenas 1 coautor
                    coauthors_map[author_a].add(author_b)

    # 3. Exibição dos Resultados
    # Transforma em lista para ordenar: (Quantidade, Nome, ID)
    results = []
    for author_id, coauth_set in coauthors_map.items():
        qtd = len(coauth_set)
        name = names_map.get(author_id, "Desconhecido")
        results.append((qtd, name, author_id))

    # Ordena do maior para o menor número de coautores
    results.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "=" * 80)
    print(
        f"{'RANK':<5} | {'QTD COAUTORES':<15} | {'NOME DO AUTOR':<40} | {'ID OPENALEX'}"
    )
    print("=" * 80)

    for i, (qtd, name, auth_id) in enumerate(results, 1):
        # Truncar nome se for muito longo para não quebrar a tabela
        display_name = (name[:37] + "..") if len(name) > 37 else name
        print(f"{i:<5} | {qtd:<15} | {display_name:<40} | {auth_id}")

    print("=" * 80)
    print(f"Total de autores analisados com pelo menos 1 coautor: {len(results)}")

    # 4. Identificar autores sem coautoria
    authors_without_coauthors = all_authors - set(coauthors_map.keys())

    if authors_without_coauthors:
        print("\n" + "=" * 80)
        print(f"AUTORES SEM COAUTORIA (Total: {len(authors_without_coauthors)})")
        print("=" * 80)
        print(f"{'NOME DO AUTOR':<50} | {'ID OPENALEX'}")
        print("=" * 80)

        # Ordena por nome para facilitar leitura
        authors_list = []
        for author_id in authors_without_coauthors:
            name = names_map.get(author_id, "Desconhecido")
            authors_list.append((name, author_id))
        authors_list.sort(key=lambda x: x[0].lower())

        for name, auth_id in authors_list:
            display_name = (name[:48] + "..") if len(name) > 48 else name
            print(f"{display_name:<50} | {auth_id}")

        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("Nenhum autor sem coautoria encontrado.")
        print("Todos os autores participaram de pelo menos um trabalho com coautores.")
        print("=" * 80)

    # Opcional: Buscar autor específico
    while True:
        search = (
            input(
                "\nDigite parte do nome de um autor para buscar (ou ENTER para sair): "
            )
            .strip()
            .lower()
        )
        if not search:
            break

        found = False
        for qtd, name, auth_id in results:
            if search in name.lower():
                print(f" -> {name} ({auth_id}) tem {qtd} coautores distintos.")
                found = True

        if not found:
            print("Autor não encontrado na lista de coautorias.")


if __name__ == "__main__":
    analyze_coauthors()
