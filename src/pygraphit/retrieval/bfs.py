from pygraphit.storage.sqlite import SQLiteStorage
from collections import deque

class BFSGraphRetrieval:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def bfs_query(self, query: str, max_depth: int = 2):
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT id FROM Nodes WHERE name = ? OR id = ?", (query, query))
        start_nodes = [row[0] for row in cursor.fetchall()]

        if not start_nodes:
            return []

        visited = set(start_nodes)
        queue = deque([(node_id, 0) for node_id in start_nodes])
        subgraph_nodes = set(start_nodes)

        while queue:
            current_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Get outgoing edges
            edges_out = self.storage.get_edges_from(current_id)
            for relation, target_id in edges_out:
                if target_id not in visited:
                    visited.add(target_id)
                    subgraph_nodes.add(target_id)
                    queue.append((target_id, depth + 1))
            
            # Get incoming edges
            edges_in = self.storage.get_edges_to(current_id)
            for source_id, relation in edges_in:
                if source_id not in visited:
                    visited.add(source_id)
                    subgraph_nodes.add(source_id)
                    queue.append((source_id, depth + 1))

        return list(subgraph_nodes)
