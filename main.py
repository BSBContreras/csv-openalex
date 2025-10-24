import argparse
import sys
import importlib

def run_author_based(record_limit, checkpoint_size, initial_work_id):
    module = importlib.import_module("AuthorBasedCollector")
    if hasattr(module, 'main'):
        module.main(record_limit, checkpoint_size, initial_work_id)

def run_citation_based(record_limit, checkpoint_size, initial_work_id):
    module = importlib.import_module("CitationBasedCollector")
    if hasattr(module, 'main'):
        module.main(record_limit, checkpoint_size, initial_work_id)

def run_author_limit(record_limit, checkpoint_size, initial_work_id):
    module = importlib.import_module("AuthorLimitCollector")
    if hasattr(module, 'main'):
        module.main(record_limit, checkpoint_size, initial_work_id)

def main():
    parser = argparse.ArgumentParser(description="Execute a coleta de dados baseada em autor ou citação com parâmetros.")

    parser.add_argument(
        "method",
        choices=["author", "citation", "author_limit"],
        help="Escolha o método de coleta: 'author' para coleta baseada em autor, 'citation' para coleta baseada em citação, ou 'author_limit' para coleta baseada em autor com limite no número de autores."
    )

    parser.add_argument(
        "--record_limit",
        type=int,
        default=100000,
        help="Limite de registros a serem coletados (padrão: 100000). Para 'author_limit', este é o limite de autores."
    )

    parser.add_argument(
        "--checkpoint_size",
        type=int,
        default=500,
        help="Tamanho do checkpoint (padrão: 500)."
    )

    parser.add_argument(
        "--initial_work_id",
        type=str,
        default="W4398186459",
        help="ID do trabalho inicial (padrão: W4398186459)."
    )

    args = parser.parse_args()

    if args.method == "author":
        run_author_based(args.record_limit, args.checkpoint_size, args.initial_work_id)
    elif args.method == "citation":
        run_citation_based(args.record_limit, args.checkpoint_size, args.initial_work_id)
    elif args.method == "author_limit":
        run_author_limit(args.record_limit, args.checkpoint_size, args.initial_work_id)
    else:
        print("Método inválido escolhido.")
        sys.exit(1)

if __name__ == "__main__":
    main()
