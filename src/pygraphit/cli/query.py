import argparse
from pygraphit.storage.sqlite import SQLiteStorage
from pygraphit.retrieval.bfs import BFSGraphRetrieval
from pygraphit.retrieval.ranking import Ranking

def main():
    parser = argparse.ArgumentParser(description="Query the PyGraph knowledge graph")
    parser.add_argument("query", help="Node name to query (e.g., 'login')")
    parser.add_argument("--depth", type=int, default=2, help="BFS search depth")
    parser.add_argument("--db", default="pygraph.db", help="Path to SQLite database")

    args = parser.parse_args()

    storage = SQLiteStorage(args.db)
    retrieval = BFSGraphRetrieval(storage)
    ranking = Ranking(storage)

    print(f"Querying for '{args.query}' with depth {args.depth}...")
    
    node_ids = retrieval.bfs_query(args.query, args.depth)
    
    if not node_ids:
        print(f"No nodes found for query: {args.query}")
        return

    ranked_nodes = ranking.rank_nodes(node_ids, args.query)
    chunks = ranking.extract_code_chunks(ranked_nodes)
    
    print(f"\nFound {len(chunks)} related code chunks:\n")
    for chunk in chunks:
        print(f"--- {chunk['type']}: {chunk['name']} ({chunk['file']}) ---")
        print(chunk['code'])
        print("-" * 40 + "\n")

if __name__ == "__main__":
    main()
